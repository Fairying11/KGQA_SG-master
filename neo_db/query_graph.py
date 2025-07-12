from neo_db.config import driver, CA_LIST, similar_words
from spider.show_profile import get_profile
import codecs
import os
import json
import base64

def query(name):
    def run_query(tx):
        result = tx.run("MATCH (p)-[r]->(n:Person{Name: $name}) "
                        "RETURN p.Name, r.relation, n.Name, p.cate, n.cate "
                        "UNION ALL "
                        "MATCH (p:Person {Name: $name})-[r]->(n) "
                        "RETURN p.Name, r.relation, n.Name, p.cate, n.cate", name=name)
        return list(result)

    with driver.session() as session:
        data = session.read_transaction(run_query)
    return get_json_data(data)

def get_json_data(data):
    json_data = {'data': [], "links": []}
    d = []

    for i in data:
        d.append(i["p.Name"] + "_" + i["p.cate"])
        d.append(i["n.Name"] + "_" + i["n.cate"])
        d = list(set(d))

    name_dict = {}
    count = 0
    for j in d:
        j_array = j.split("_")
        data_item = {}
        name_dict[j_array[0]] = count
        count += 1
        data_item['name'] = j_array[0]
        data_item['category'] = CA_LIST[j_array[1]]
        json_data['data'].append(data_item)

    for i in data:
        link_item = {}
        link_item['source'] = name_dict[i["p.Name"]]
        link_item['target'] = name_dict[i["n.Name"]]
        link_item['value'] = i["r.relation"]
        json_data['links'].append(link_item)

    return json_data

def get_KGQA_answer(array):
    data_array = []
    for i in range(len(array) - 2):
        if i == 0:
            name = array[0]
        else:
            name = data_array[-1]['p.Name']

        def run_query(tx):
            result = tx.run("MATCH (p)-[r:%s{relation: $rel}]->(n:Person{Name: $name}) "
                            "RETURN p.Name, n.Name, r.relation, p.cate, n.cate" % similar_words[array[i + 1]],
                            rel=similar_words[array[i + 1]], name=name)
            return list(result)

        with driver.session() as session:
            data = session.read_transaction(run_query)
            data_array.extend(data)

    with open("./spider/images/" + "%s.jpg" % (str(data_array[-1]['p.Name'])), "rb") as image:
        base64_data = base64.b64encode(image.read())
        b = str(base64_data)

    return [get_json_data(data_array), get_profile(str(data_array[-1]['p.Name'])), b.split("'")[1]]

def get_answer_profile(name):
    with open("./spider/images/" + "%s.jpg" % (str(name)), "rb") as image:
        base64_data = base64.b64encode(image.read())
        b = str(base64_data)
    return [get_profile(str(name)), b.split("'")[1]]
