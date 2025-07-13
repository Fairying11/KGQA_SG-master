from neo4j import GraphDatabase

# Neo4j数据库连接配置（对应步骤2-7）
NEO4J_URI = "bolt://localhost:7687"  # 端口冲突时可修改为bolt://localhost:7688等
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"  # 替换为实际密码

# 创建数据库驱动（对应步骤2-5）
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# 人物类别映射（用于可视化分类，对应步骤3-45）
CATEGORY_MAP = {
    "唐朝": 0,
    "宋朝": 1,
    "明朝": 2,
    "清朝": 3,
    "其他": 4
}
