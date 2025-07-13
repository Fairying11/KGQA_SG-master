from flask import Flask, render_template, request, jsonify
from flask_caching import Cache
from datetime import timedelta
import logging
from neo_db.query_graph import query, get_KGQA_answer, get_answer_profile
from KGQA.ltp import get_target_array

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)

# 初始化缓存
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index(name=None):
    """首页路由"""
    try:
        return render_template('index.html', name=name)
    except Exception as e:
        logger.error(f"首页渲染失败: {str(e)}")
        return jsonify({"error": f"页面渲染失败: {str(e)}"}), 500

@app.route('/search', methods=['GET', 'POST'])
def search():
    """搜索页面路由"""
    try:
        return render_template('search.html')
    except Exception as e:
        logger.error(f"搜索页面渲染失败: {str(e)}")
        return jsonify({"error": f"页面渲染失败: {str(e)}"}), 500

@app.route('/KGQA', methods=['GET', 'POST'])
def KGQA():
    """知识图谱问答页面路由"""
    try:
        return render_template('KGQA.html')
    except Exception as e:
        logger.error(f"KGQA页面渲染失败: {str(e)}")
        return jsonify({"error": f"页面渲染失败: {str(e)}"}), 500

@app.route('/get_profile', methods=['GET', 'POST'])
def get_profile():
    """获取人物资料接口"""
    try:
        name = request.args.get('character_name')
        if not name:
            return jsonify({"error": "请提供人物名称"}), 400

        json_data = get_answer_profile(name)
        return jsonify(json_data)
    except Exception as e:
        logger.error(f"获取人物资料失败: {str(e)}")
        return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500

@app.route('/KGQA_answer', methods=['GET', 'POST'])
def KGQA_answer():
    """知识图谱问答接口"""
    try:
        question = request.args.get('name')
        if not question:
            return jsonify({"error": "请提供问题"}), 400

        json_data = get_KGQA_answer(get_target_array(str(question)))
        return jsonify(json_data)
    except Exception as e:
        logger.error(f"处理问答请求失败: {str(e)}")
        return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500

@app.route('/search_name', methods=['GET', 'POST'])
def search_name():
    """搜索人物关系接口"""
    try:
        name = request.args.get('name')
        if not name:
            return jsonify({"error": "请提供人物名称"}), 400

        json_data = query(str(name))
        return jsonify(json_data)
    except Exception as e:
        logger.error(f"搜索人物关系失败: {str(e)}")
        return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500

@app.route('/get_all_relation', methods=['GET', 'POST'])
@cache.cached(timeout=300)  # 缓存5分钟
def get_all_relation():
    """获取所有关系页面"""
    try:
        return render_template('all_relation.html')
    except Exception as e:
        logger.error(f"获取所有关系页面失败: {str(e)}")
        return jsonify({"error": f"页面渲染失败: {str(e)}"}), 500

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5001)
