import json
import os
import logging
from urllib import request
from urllib.parse import quote
from bs4 import BeautifulSoup

# 配置（对应步骤2-15数据采集要求）
OUTPUT_DIR = "../raw_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
}

def crawl_character(name):
    """爬取单个人物数据（对应步骤2-15）"""
    try:
        url = f"https://baike.baidu.com/item/{quote(name)}"
        req = request.Request(url, headers=HEADERS)
        with request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8')

        soup = BeautifulSoup(html, 'html.parser')

        # 提取基本信息（对应步骤2-20数据结构）
        basicinfo = {}
        for item in soup.find_all(class_="basicInfo-item"):
            key = item.find(class_="name").get_text(strip=True).replace('\n', '') if item.find(class_="name") else ""
            value = item.find(class_="value").get_text(strip=True).replace('\n', '、') if item.find(class_="value") else ""
            if key:
                basicinfo[key] = value

        # 提取摘要
        summary = soup.find(class_="lemma-summary").get_text(strip=True) if soup.find(class_="lemma-summary") else ""

        # 提取关系（格式："姓名1#关系#姓名2#地址"）
        peoplerelations = []
        for rel_item in soup.select(".lemma-relation .list a"):
            target = rel_item.get_text(strip=True)
            rel_type = rel_item.find_parent().previous_sibling.get_text(strip=True) if rel_item.find_parent().previous_sibling else ""
            if target and rel_type:
                peoplerelations.append(f"{name}#{rel_type}#{target}#{url}")

        # 提取图片
        pic = soup.find(class_="summary-pic img")["src"] if soup.find(class_="summary-pic img") else ""

        return {
            "name": name,
            "summary": summary,
            "peoplerelations": peoplerelations,
            "basicinfo": basicinfo,
            "baike_url": url,
            "pic": pic
        }
    except Exception as e:
        logging.error(f"爬取{name}失败: {e}")
        return None

def main():
    # 示例人物列表（可扩展）
    characters = ["韩愈", "刘备", "曹操"]

    # 保存主要人物数据（对应步骤2-16）
    with open(os.path.join(OUTPUT_DIR, "baike_data.txt"), "w", encoding="utf-8") as f:
        for char in characters[:2]:
            data = crawl_character(char)
            if data:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")

    # 保存补充人物数据（对应步骤2-17）
    with open(os.path.join(OUTPUT_DIR, "baike_append_data.txt"), "w", encoding="utf-8") as f:
        for char in characters[2:]:
            data = crawl_character(char)
            if data:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
