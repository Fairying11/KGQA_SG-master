from neo4j import GraphDatabase, exceptions
import logging
import time

# 配置日志输出格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Neo4j数据库连接配置（根据实际情况修改）
NEO4J_URI = "bolt://localhost:7687"  # 默认端口，若冲突可改为7688等
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"  # 替换为你的Neo4j密码

# 人物类别映射（用于可视化分类）
CATEGORY_MAP = {
    "唐朝": 0,
    "宋朝": 1,
    "明朝": 2,
    "清朝": 3,
    "其他": 4
}

# 数据库连接重试参数
MAX_RETRIES = 3
RETRY_DELAY = 2  # 秒

def create_db_driver(uri, user, password):
    """创建并测试数据库驱动连接，带重试机制"""
    driver = None
    for attempt in range(MAX_RETRIES):
        try:
            driver = GraphDatabase.driver(uri, auth=(user, password))
            # 测试连接是否有效
            with driver.session() as session:
                session.run("MATCH (n) RETURN count(n) LIMIT 1")
            logger.info(f"Neo4j数据库连接成功 (尝试 {attempt + 1}/{MAX_RETRIES})")
            return driver
        except exceptions.AuthError:
            logger.error("数据库认证失败，请检查用户名和密码")
            break  # 认证错误无需重试
        except exceptions.ServiceUnavailable:
            logger.warning(f"数据库服务不可用 (尝试 {attempt + 1}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
        except Exception as e:
            logger.error(f"连接数据库时发生错误: {str(e)} (尝试 {attempt + 1}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)

    logger.error("无法建立数据库连接，将使用空驱动")
    return None

# 创建数据库驱动实例
driver = create_db_driver(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

def close_driver():
    """关闭数据库驱动连接"""
    if driver:
        try:
            driver.close()
            logger.info("Neo4j数据库驱动已关闭")
        except Exception as e:
            logger.error(f"关闭数据库驱动时发生错误: {str(e)}")
