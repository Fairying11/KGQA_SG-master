from flask import Flask, request, jsonify, render_template
from neo_db.config import driver, close_driver
import logging
import atexit

# 注册程序退出时关闭数据库连接
atexit.register(close_driver)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1  # 关闭静态文件缓存
app.config['JSON_AS_ASCII'] = False  # 解决JSON中文乱码

# 配置日志（便于调试）
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def query_neo4j(cypher, params):
    """通用Neo4j查询函数，处理异常并返回结果"""
    if not driver:
        logging.error("数据库驱动未初始化，无法执行查询")
        return []
    try:
        with driver.session() as session:
            result = session.run(cypher, params)
            return result.data()  # 返回字典格式的查询结果
    except Exception as e:
        logging.error(f"Neo4j查询失败: {str(e)}，Cypher语句: {cypher}")
        return []

# 1. 实体属性查询接口
@app.route('/star/attribute', methods=['POST'])
def get_entity_attr():
    keyword = request.json.get('keyword', '').strip()
    if not keyword:
        return jsonify({"status": 400, "respon": "请输入人物名称"})

    # 查询人物属性（确保Cypher语句无注释，避免语法错误）
    cypher = """
    MATCH (p:Person {name: $keyword})
    RETURN p.name AS name,
           p.alias AS alias,
           p.dynasty AS dynasty,
           p.birthplace AS birthplace,
           p.summary AS summary,
           p.pic AS pic
    """
    result = query_neo4j(cypher, {"keyword": keyword})

    if result:
        # 格式化结果，兼容空值
        data = {
            "name": result[0].get("name", ""),
            "basicInfo": {
                "别名": result[0].get("alias", "无数据"),
                "所处时代": result[0].get("dynasty", "无数据"),
                "籍贯": result[0].get("birthplace", "无数据")
            },
            "summary": result[0].get("summary", "无简介信息"),
            "pic": result[0].get("pic", "")  # 图片URL，若不存在则为空
        }
        return jsonify({"status": 200, "respon": data})
    else:
        return jsonify({"status": 404, "respon": f"未查询到「{keyword}」的属性信息"})

# 2. 关系查询接口（用于知识图谱可视化）
@app.route('/relationship', methods=['POST'])
def get_relations():
    keyword = request.json.get('keyword', '').strip()
    if not keyword:
        return jsonify({"status": 400, "respon": "请输入人物名称"})

    # 查询人物关系（不使用id()函数，避免弃用警告）
    cypher = """
    MATCH (s:Person {name: $keyword})-[r:RELATION]->(o:Person)
    RETURN s.name AS source,
           o.name AS target,
           r.type AS relation
    """
    result = query_neo4j(cypher, {"keyword": keyword})

    # 处理结果为前端可视化所需格式
    nodes = []
    links = []
    node_ids = set()  # 用于去重节点

    # 添加中心节点
    center_node = {"id": keyword, "text": keyword, "category": 0}
    nodes.append(center_node)
    node_ids.add(keyword)

    # 添加关联节点和关系
    for record in result:
        source = record["source"]
        target = record["target"]
        relation = record["relation"]

        # 添加目标节点（去重）
        if target not in node_ids:
            nodes.append({"id": target, "text": target, "category": 1})
            node_ids.add(target)

        # 添加关系
        links.append({
            "from": source,
            "to": target,
            "text": relation
        })

    return jsonify({
        "status": 200,
        "respon": {
            "nodes": nodes,
            "lines": links
        }
    })

# 3. 页面路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search_page():
    return render_template('search.html')  # 知识图谱可视化页面

@app.route('/search_attribute')
def search_attribute_page():
    return render_template('search_attribute.html')  # 实体属性查询页面

@app.route('/KGQA')
def kgqa_page():
    return render_template('KGQA.html')  # 预留问答页面

if __name__ == '__main__':
    # 启动服务（端口5001，避免与Neo4j冲突）
    app.run(host='0.0.0.0', port=5001, debug=True)
