from flask import Flask, request, jsonify, render_template
from neo_db.config import driver
import logging

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1  # 关闭静态文件缓存

# 配置日志
logging.basicConfig(level=logging.INFO)

def query_neo4j(cypher, params):
    """通用查询函数（对应步骤2-29、2-30）"""
    try:
        with driver.session() as session:
            return session.run(cypher, params).data()
    except Exception as e:
        logging.error(f"查询失败: {e}")
        return []

# 实体属性查询接口（对应步骤2-29、示例2-32）
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

# 关系查询接口（对应步骤2-30、示例2-35）
@app.route('/relationship', methods=['POST'])
def get_relations():
    keyword = request.json.get('keyword')
    if not keyword:
        return jsonify({"status": 400, "respon": "缺少关键字"})

    cypher = """
    MATCH (s:Person {name: $keyword})-[r:RELATION]->(o:Person)
    RETURN s.name AS source, o.name AS target, r.type AS relation
    """
    result = query_neo4j(cypher, {"keyword": keyword})
    nodes = [{"id": r["source"], "text": r["source"]} for r in result] + \
            [{"id": r["target"], "text": r["target"]} for r in result]
    links = [{"from": r["source"], "to": r["target"], "text": r["relation"]} for r in result]
    return jsonify({"status": 200, "respon": {"nodes": nodes, "lines": links}})

# 页面路由
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)  # 避免与Neo4j端口冲突
