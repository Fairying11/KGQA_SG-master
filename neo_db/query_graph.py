from neo4j import GraphDatabase
from .config import NEO4J_CONFIG
import json

class GraphQuery:
    def __init__(self):
        self.driver = GraphDatabase.driver(**NEO4J_CONFIG)

    def close(self):
        self.driver.close()

    def get_entity_attribute(self, keyword):
        """查询实体属性"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Person {name: $keyword})
                RETURN p.name AS name,
                       p.summary AS summary,
                       p.basicinfo AS basicinfo,
                       p.pic AS pic
            """, keyword=keyword)
            record = result.single()
            if record:
                try:
                    basicinfo_dict = json.loads(record["basicinfo"])
                except json.JSONDecodeError:
                    basicinfo_dict = {}
                return {
                    "name": record["name"],
                    "basicInfo": basicinfo_dict,
                    "summary": record["summary"],
                    "pic": record["pic"]
                }
            return None

    def get_relations(self, keyword):
        """查询实体关系"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Person {name: $keyword})-[r:RELATION]->(o:Person)
                RETURN s.name AS subj,
                       o.name AS obj,
                       r.type AS rel_type,
                       elementId(s) AS subj_id,
                       elementId(o) AS obj_id
            """, keyword=keyword)

            nodes = []
            lines = []
            node_ids = set()

            # 添加中心节点
            center_node = {"id": id(keyword), "text": keyword, "color": "#43a2f1", "fontColor": "yellow"}
            nodes.append(center_node)
            node_ids.add(keyword)

            # 添加关联节点和关系
            for record in result:
                obj = record["obj"]
                if obj not in node_ids:
                    nodes.append({
                        "id": record["obj_id"],
                        "text": obj,
                        "color": "#43a2f1",
                        "fontColor": "yellow"
                    })
                    node_ids.add(obj)
                lines.append({
                    "from": record["subj_id"],
                    "to": record["obj_id"],
                    "text": record["rel_type"],
                    "color": "#43a2f1"
                })
            return {
                "rootId": id(keyword),
                "nodes": nodes,
                "lines": lines
            }

if __name__ == "__main__":
    query = GraphQuery()
    print(query.get_entity_attribute("刘备"))
    print(query.get_relations("刘备"))
    query.close()
