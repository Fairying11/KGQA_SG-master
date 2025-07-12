from neo_db.config import driver
import os

def create_graph():
    with driver.session() as session:
        # 删除所有节点和关系
        session.run("MATCH (n) DETACH DELETE n")
        print("Delete all nodes and relationships")

        # 获取当前脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建文件的绝对路径，向上一级目录然后进入raw_data目录
        file_path = os.path.join(script_dir, '../raw_data/triples_processed.txt')

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # 跳过空行
                    if not line.strip():
                        continue

                    relation_array = line.strip().split(',')
                    print(relation_array)

                    # 确保数据有足够的元素
                    if len(relation_array) < 5:
                        print(f"跳过不完整的行: {relation_array}")
                        continue

                    # 创建节点
                    session.run("MERGE (p:Person {cate:$cate, Name:$name})",
                                cate=relation_array[3], name=relation_array[0])
                    session.run("MERGE (p:Person {cate:$cate, Name:$name})",
                                cate=relation_array[4], name=relation_array[1])

                    # 创建关系 - 使用参数化查询避免注入风险
                    rel_type = relation_array[2]
                    # 确保关系类型是有效的Cypher标识符
                    if not rel_type.isidentifier():
                        print(f"无效的关系类型: {rel_type}")
                        continue

                    # 使用参数化查询创建关系
                    query = (
                        f"MATCH (e:Person {{Name: $e_name}}), (cc:Person {{Name: $cc_name}}) "
                        f"MERGE (e)-[r:{rel_type} {{relation: $rel}}]->(cc) "
                        "RETURN r"
                    )
                    session.run(query,
                                e_name=relation_array[0],
                                cc_name=relation_array[1],
                                rel=relation_array[2])

        except FileNotFoundError:
            print(f"错误: 文件未找到 - {file_path}")
            print("请确保raw_data目录存在且包含triples_processed.txt文件")
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    create_graph()
