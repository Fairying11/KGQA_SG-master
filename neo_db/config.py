from neo4j import GraphDatabase

# Neo4j 数据库连接配置
# 默认的 Bolt 端口
NEO4J_URI = "bolt://localhost:7687"
# Neo4j 数据库的用户名
NEO4J_USER = "neo4j"
# Neo4j 数据库的密码
NEO4J_PASSWORD = "12345678"
# 创建 Neo4j 数据库驱动
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# 人物分类列表，将不同家族或势力映射到数字编号
CA_LIST = {
    "贾家荣国府": 0,
    "贾家宁国府": 1,
    "王家": 2,
    "史家": 3,
    "薛家": 4,
    "其他": 5,
    "林家": 6
}

# 相似词映射表，将不同表述的亲属关系映射到统一的表述
similar_words = {
    "爸爸": "父亲",
    "妈妈": "母亲",
    "爸": "父亲",
    "妈": "母亲",
    "父亲": "父亲",
    "母亲": "母亲",
    "儿子": "儿子",
    "女儿": "女儿",
    "丫环": "丫环",
    "兄弟": "兄弟",
    "妻": "妻",
    "老婆": "妻",
    "哥哥": "哥哥",
    "表妹": "表兄妹",
    "弟弟": "弟弟",
    "妾": "妾",
    "养父": "养父",
    "姐姐": "姐姐",
    "娘": "母亲",
    "爹": "父亲",
    "father": "父亲",
    "mother": "母亲",
    "朋友": "朋友",
    "爷爷": "爷爷",
    "奶奶": "奶奶",
    "孙子": "孙子",
    "老公": "丈夫",
    "岳母": "岳母",
    "表兄妹": "表兄妹",
    "孙女": "孙女",
    "嫂子": "嫂子",
    "暧昧": "暧昧"
}

def get_ca_index(category):
    """
    根据人物分类名称获取对应的索引编号
    :param category: 人物分类名称
    :return: 对应的索引编号，如果未找到则返回 None
    """
    return CA_LIST.get(category)

def get_similar_word(word):
    """
    根据输入的亲属关系表述获取统一的表述
    :param word: 输入的亲属关系表述
    :return: 统一的表述，如果未找到则返回原词
    """
    return similar_words.get(word, word)
