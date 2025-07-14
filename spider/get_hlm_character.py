import os
import json
from urllib import request
from bs4 import BeautifulSoup

# 输出目录（对应步骤2-16、2-17）
OUTPUT_DIR = "../raw_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def crawl_character(name):
    """爬取百度百科数据（符合步骤2-20数据结构）"""
    url = f"https://baike.baidu.com/item/{name}"
    headers = {"User-Agent": "Mozilla/5.0"}
    req = request.Request(url, headers=headers)

    with request.urlopen(req) as resp:
        soup = BeautifulSoup(resp.read(), "html.parser")

        # 提取基本信息
        basicinfo = {}
        for item in soup.find_all(class_="basicInfo-item"):
            key = item.find(class_="name").get_text(strip=True) if item.find(class_="name") else ""
            value = item.find(class_="value").get_text(strip=True) if item.find(class_="value") else ""
            if key:
                basicinfo[key] = value

        # 提取关系（格式：姓名1#关系#姓名2#地址）
        peoplerelations = []
        for rel in soup.select(".lemma-relation a"):
            target = rel.get_text()
            rel_type = rel.find_parent().previous_sibling.get_text() if rel.find_parent().previous_sibling else ""
            if target and rel_type:
                peoplerelations.append(f"{name}#{rel_type}#{target}#{url}")

        return {
            "name": name,
            "summary": soup.find(class_="lemma-summary").get_text(strip=True) if soup.find(class_="lemma-summary") else "",
            "peoplerelations": peoplerelations,
            "basicinfo": basicinfo,
            "pic": soup.find(class_="summary-pic img")["src"] if soup.find(class_="summary-pic img") else "",
            "baike_url": url
        }

if __name__ == "__main__":
    # 爬取主要人物
    main_chars = ["刘备", "曹操", "孙权"]
    with open(f"{OUTPUT_DIR}/baike_data.txt", "w", encoding="utf-8") as f:
        for char in main_chars:
            f.write(json.dumps(crawl_character(char), ensure_ascii=False) + "\n")

    # 爬取补充人物
    append_chars = ["诸葛亮", "关羽"]
    with open(f"{OUTPUT_DIR}/baike_append_data.txt", "w", encoding="utf-8") as f:
        for char in append_chars:
            f.write(json.dumps(crawl_character(char), ensure_ascii=False) + "\n")
