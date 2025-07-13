from neo4j import GraphDatabase
from .config import NEO4J_CONFIG

class GraphQuery:
    def __init__(self):
        self.driver = GraphDatabase.driver(**NEO4J_CONFIG)

    def close(self):
        self.driver.close()

    def get_entity_attribute(self, keyword):
        """实体属性查询接口实现{insert\_element\_4\_}"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Person {name: $keyword})
                RETURN p.name AS name,
                       p.alias AS alias,
                       p.dynasty AS dynasty,
                       p.birthplace AS birthplace,
                       p.summary AS summary,
                       p.pic AS pic
            """, keyword=keyword)
            record = result.single()
            if record:
                return {
                    "name": record["name"],
                    "basicInfo": {
                        "别名": record["alias"],
                        "所处时代": record["dynasty"],
                        "籍贯": record["birthplace"],
                        "简介": record["summary"]
                    },
                    "summary": record["summary"],
                    "pic": record["pic"]
                }
            return None

    def get_relations(self, keyword):
        """关系查询接口实现{insert\_element\_5\_}"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Person {name: $keyword})-[r:RELATION]->(o:Person)
                RETURN s.name AS subj,
                       o.name AS obj,
                       r.type AS rel_type,
                       id(s) AS subj_id,
                       id(o) AS obj_id
            """, keyword=keyword)
            nodes = []
            lines = []
            node_ids = set()
            # 添加中心节点
            center_node = {"id": id(keyword), "text": keyword, "color": "#43a2f1", "fontColor": "yellow"}
            nodes.append(center_node)
            node_ids.add(keyword)
            
            for record in result:
                obj = record["obj"]
                if obj not in node_ids:
                    nodes.append({"id": record["obj_id"], "text": obj, "color": "#43a2f1", "fontColor": "yellow"})
                    node_ids.add(obj)
                lines.append({
                    "from": id(keyword),
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
