from flask import Flask, request, jsonify, render_template
from neo_db.config import driver
import logging
import re
import atexit

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1  # 关闭静态文件缓存

# 配置日志
logging.basicConfig(level=logging.INFO)

# 应用退出时关闭驱动
atexit.register(lambda: driver.close() if driver else None)

def query_neo4j(cypher, params):
    """通用查询函数"""
    try:
        with driver.session() as session:
            logging.debug(f"执行CQL：{cypher}，参数：{params}")
            return session.run(cypher, params).data()
    except Exception as e:
        logging.error(f"查询失败: {e}")
        return []

# 实体属性查询接口
@app.route('/star/attribute', methods=['POST'])
def get_entity_attr():
    keyword = request.json.get('keyword')
    if not keyword:
        return jsonify({"status": 400, "respon": "缺少关键字"})

    cypher = """
    MATCH (p:Person {name: $keyword})
    RETURN p.name AS name, p.summary AS summary, p.basicinfo AS basicInfo, p.pic AS pic
    """
    result = query_neo4j(cypher, {"keyword": keyword})
    return jsonify({"status": 200, "respon": result[0]}) if result else jsonify({"status": 404})

# 关系查询接口
@app.route('/relationship', methods=['POST'])
def get_relations():
    keyword = request.json.get('keyword')
    if not keyword:
        return jsonify({"status": 400, "respon": "缺少关键字"})

    cypher = """
    MATCH (s:Person {name: $keyword})-[r:RELATION]->(o:Person)
    RETURN s.name AS source, o.name AS target, r.type AS relation, 
           elementId(s) AS s_id, elementId(o) AS o_id
    """
    result = query_neo4j(cypher, {"keyword": keyword})
    nodes = [{"id": r["s_id"], "text": r["source"]} for r in result] + \
            [{"id": r["o_id"], "text": r["target"]} for r in result]
    links = [{"from": r["s_id"], "to": r["o_id"], "text": r["relation"]} for r in result]
    return jsonify({"status": 200, "respon": {"nodes": nodes, "lines": links}})

# 知识问答接口
@app.route('/answer', methods=['POST'])
def answer():
    if not request.is_json:
        return jsonify({"status": 415, "message": "请使用 application/json 格式请求"}), 415

    data = request.get_json()
    question = data.get('question')

    if not question:
        return jsonify({"status": 400, "message": "问题参数不能为空"}), 400

    logging.info(f"处理问答请求：{question}")

    # 简单的规则匹配
    match = re.match(r'(.+)的(.+)是谁？', question)
    if match:
        entity = match.group(1)
        relation = match.group(2)
        cypher = """
            MATCH (a:Person {name: $entity})-[r:RELATION {type: $relation}]->(b:Person)
            RETURN b.name AS answer
        """
        result = query_neo4j(cypher, {"entity": entity, "relation": relation})
        if result:
            return jsonify({"status": 200, "answer": f"{entity}的{relation}是{result[0]['answer']}"})

    match = re.match(r'谁是(.+)的(.+)?', question)
    if match:
        entity = match.group(1)
        relation = match.group(2)
        cypher = """
            MATCH (a:Person {name: $entity})<-[r:RELATION {type: $relation}]-(b:Person)
            RETURN b.name AS answer
        """
        result = query_neo4j(cypher, {"entity": entity, "relation": relation})
        if result:
            return jsonify({"status": 200, "answer": f"{result[0]['answer']}是{entity}的{relation}"})

    return jsonify({
        "status": 200,
        "answer": f"针对问题「{question}」的回答（示例）"
    })

# 页面路由（确保视图函数名与模板中的url_for一致）
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search_page():
    return render_template('search.html')

@app.route('/search_attribute')
def search_attribute_page():
    return render_template('search_attribute.html')

@app.route('/KGQA')
def kgqa_page():
    return render_template('KGQA.html')

@app.errorhandler(404)
def not_found(error):
    return jsonify({"status": 404, "message": "请求的资源不存在"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
