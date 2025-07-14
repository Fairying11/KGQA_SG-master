# neo_db/create_graph.py
import json
import logging
from config import driver

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def import_baike_data(file_path):
    """导入百度百科人物数据（含实体和关系）"""
    with driver.session() as session:
        # 清空现有数据（首次导入时使用）
        session.run("MATCH (n) DETACH DELETE n")
        logging.info("已清空数据库现有数据")

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    name = data["name"]

                    # 将 basicinfo 字典转换为 JSON 字符串
                    basicinfo_str = json.dumps(data.get("basicinfo", {}))

                    # 创建人物实体节点
                    session.run("""
                        MERGE (p:Person {name: $name})
                        SET p.summary = $summary,
                            p.basicinfo = $basicinfo,
                            p.baike_url = $baike_url,
                            p.pic = $pic
                    """, name=name,
                       summary=data.get("summary", ""),
                       basicinfo=basicinfo_str,
                       baike_url=data.get("baike_url", ""),
                       pic=data.get("pic", ""))
                    logging.info(f"已导入实体: {name}")

                    # 导入人物关系
                    for rel in data.get("peoplerelations", []):
                        # 解析关系数据
                        parts = rel.split('#')
                        if len(parts) < 3:
                            logging.warning(f"无效关系数据: {rel}")
                            continue
                        name1, relation, name2 = parts[0], parts[1], parts[2]

                        # 创建关系（避免笛卡尔积）
                        session.run("""
                            MATCH (a:Person {name: $name1})
                            MATCH (b:Person {name: $name2})
                            MERGE (a)-[r:RELATION {type: $relation}]->(b)
                        """, name1=name1, name2=name2, relation=relation)
                        logging.info(f"已导入关系: {name1} -[{relation}]-> {name2}")
                except Exception as e:
                    logging.error(f"处理数据时出错: {e}，数据行: {line}")

if __name__ == "__main__":
    # 导入主要人物和补充人物数据
    import_baike_data("../raw_data/baike_data.txt")
    import_baike_data("../raw_data/baike_append_data.txt")
    driver.close()
