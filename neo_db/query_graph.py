from neo_db.config import driver, CA_LIST, similar_words
from spider.show_profile import get_profile
import codecs
import os
import json
import base64

def query(name):
    """
    查询与指定人物相关的关系
    :param name: 人物名称
    :return: 包含关系信息的 JSON 数据
    """
    def run_query(tx):
        query_str = (
            "MATCH (p)-[r]->(n:Person{Name: $name}) "
            "RETURN p.Name, r.relation, n.Name, p.cate, n.cate "
            "UNION ALL "
            "MATCH (p:Person {Name: $name})-[r]->(n) "
            "RETURN p.Name, r.relation, n.Name, p.cate, n.cate"
        )
        result = tx.run(query_str, name=name)
        return list(result)

    with driver.session() as session:
        data = session.read_transaction(run_query)
    return get_json_data(data)

def get_json_data(data):
    """
    将查询结果转换为 JSON 格式
    :param data: 查询结果
    :return: JSON 数据
    """
    json_data = {'data': [], "links": []}
    nodes = set()
    for record in data:
        nodes.add(record["p.Name"] + "_" + record["p.cate"])
        nodes.add(record["n.Name"] + "_" + record["n.cate"])

    name_dict = {}
    node_id = 0
    for node in nodes:
        node_name, node_cate = node.split("_")
        node_item = {
            'name': node_name,
            'category': CA_LIST[node_cate]
        }
        name_dict[node_name] = node_id
        node_id += 1
        json_data['data'].append(node_item)

    for record in data:
        link_item = {
            'source': name_dict[record["p.Name"]],
            'target': name_dict[record["n.Name"]],
            'value': record["r.relation"]
        }
        json_data['links'].append(link_item)

    return json_data

def get_KGQA_answer(array):
    """
    获取知识图谱问答的答案
    :param array: 问题处理后的数组
    :return: 包含答案信息的列表
    """
    data_array = []
    for i in range(len(array) - 2):
        if i == 0:
            name = array[0]
        else:
            name = data_array[-1]['p.Name']

        def run_query(tx):
            query_str = (
                "MATCH (p)-[r:%s{relation: $rel}]->(n:Person{Name: $name}) "
                "RETURN p.Name, n.Name, r.relation, p.cate, n.cate" % similar_words[array[i + 1]]
            )
            result = tx.run(query_str, rel=similar_words[array[i + 1]], name=name)
            return list(result)

        with driver.session() as session:
            data = session.read_transaction(run_query)
            data_array.extend(data)

    image_path = os.path.join("./spider/images/", "%s.jpg" % (str(data_array[-1]['p.Name'])))
    try:
        with open(image_path, "rb") as image:
            base64_data = base64.b64encode(image.read())
            image_base64 = str(base64_data).split("'")[1]
    except FileNotFoundError:
        image_base64 = ""

    return [get_json_data(data_array), get_profile(str(data_array[-1]['p.Name'])), image_base64]

def get_answer_profile(name):
    """
    获取指定人物的资料和图片
    :param name: 人物名称
    :return: 包含人物资料和图片的列表
    """
    image_path = os.path.join("./spider/images/", "%s.jpg" % (str(name)))
    try:
        with open(image_path, "rb") as image:
            base64_data = base64.b64encode(image.read())
            image_base64 = str(base64_data).split("'")[1]
    except FileNotFoundError:
        image_base64 = ""

    return [get_profile(str(name)), image_base64]
