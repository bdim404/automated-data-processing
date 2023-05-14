import json
import re
import pypinyin
from bs4 import BeautifulSoup

def convert_html(text):
    if text == "":
        return ""
    # 将html标签过滤掉
    soup = BeautifulSoup(text, 'html.parser')
    text = soup.get_text()

    # 替换空格、换行等特殊字符为空格
    text = re.sub(r'[\n\t\xa0\u3000]', ' ', text)
    
    # 去除多余的空格
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def extract_text_from_html(html_content):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', html_content)
    return cleantext

def convert_pinyin(text):
    return ' '.join(pypinyin.lazy_pinyin(text, style=pypinyin.Style.NORMAL, strict=False))

def convert_to_article(data):
    title = data.get("notice_title", "")
    url = data.get("notice_link", "")

    return {
        "id": data.get("notice_id", ""),
        "type": data.get("notice_type_name", ""),
        "date": data.get("notice_create_time", ""),
        "org": data.get("organization_name", ""),
        "title": title,
        "pinyin": convert_pinyin(title),
        "content": data.get("notice_content", "").strip(),
        "link": f"$STR{data.get('notice_id', '')}",
        "url": url,
        "uri": f"$STR{url}" if url else "",
    }


def check_update_data(update_data):
    if "datas" in update_data and "tables" in update_data["datas"]:
        return update_data["datas"]["tables"]
    else:
        print("数据格式不正确。")
        return None

def process_update_json(update_json_file, article_json_file, html_json_file, news_json_file, notice_json_file):
    with open(update_json_file, encoding="utf-8") as file:
        update_data = json.load(file)

    tables = check_update_data(update_data)
    if tables is None:
        return
    
    article_data = []
    news_data = []
    notice_data = []
    html_data = []

    for entry in tables:
        article = convert_to_article(entry)
        if article["uri"]:  # If 'uri' field is not empty, it's a news
            news = {k: article[k] for k in article if k != "content"}
            news_data.append(news)
        else:  # If 'uri' field is empty, it's a notice
            html_data.append({
                'id': article['id'],
                'html': article['content'],
            })
            article['content'] = convert_html(article['content'])
            notice_data.append({
                k: article[k] for k in article if k != "uri" and k != "url"
            })

        article_data.append(article)

    with open(article_json_file, "w", encoding="utf-8") as file:
        json.dump(article_data, file, ensure_ascii=False, indent=2)

    with open(html_json_file, "w", encoding="utf-8") as file:
        json.dump(html_data, file, ensure_ascii=False, indent=2)
        
    with open(news_json_file, "w", encoding="utf-8") as file:
        json.dump(news_data, file, ensure_ascii=False, indent=2)

    with open(notice_json_file, "w", encoding="utf-8") as file:
        json.dump(notice_data, file, ensure_ascii=False, indent=2)


process_update_json("update.json", "article.json", "html.json", "news.json", "notice.json")

