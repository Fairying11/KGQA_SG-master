from neo_db.config import driver
import codecs
import os
import json

CA_LIST = {"魏国":0,"蜀国":1,"吴国":2,"群雄":3}

def get_neo4j_data():
    def run_query(tx):
        result = tx.run("MATCH (p)-[r]->(n:Person) "
                        "RETURN p.Name, r.relation, n.Name, p.cate, n.cate")
        return list(result)

    with driver.session() as session:
        data = session.read_transaction(run_query)
    return data

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

if __name__ == "__main__":
    data = get_neo4j_data()
    json_data = get_json_data(data)

    f = codecs.open('../static/data.json', 'w+', 'utf-8')
    f.write(json.dumps(json_data, ensure_ascii=False))
