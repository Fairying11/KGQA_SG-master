from neo4j import GraphDatabase
from neo4j.exceptions import (
    AuthError,
    ServiceUnavailable,
    TransientError,
    DriverError
)
import logging
import time
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 配置参数
NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '12345678')

# 重试参数
MAX_RETRIES = 3
RETRY_DELAY = 2  # 秒

# 人物类别映射
CATEGORY_MAP = {
    "唐朝": 0,
    "宋朝": 1,
    "明朝": 2,
    "清朝": 3,
    "其他": 4
}

class Neo4jConnection:
    """Neo4j数据库连接类，支持上下文管理器"""

    def __init__(self, uri, user, password):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def connect(self):
        """创建并测试数据库连接"""
        for attempt in range(MAX_RETRIES):
            try:
                self.driver = GraphDatabase.driver(
                    self.uri,
                    auth=(self.user, self.password),
                    max_connection_pool_size=50,
                    connection_acquisition_timeout=30
                )
                self.driver.verify_connectivity()  # 验证连接
                logger.info(f"Neo4j数据库连接成功 (尝试 {attempt + 1}/{MAX_RETRIES})")
                return self
            except AuthError as e:
                logger.error(f"认证失败: {e}")
                break  # 认证错误无需重试
            except ServiceUnavailable as e:
                logger.warning(f"服务不可用 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
            except TransientError as e:
                logger.warning(f"临时错误 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
            except DriverError as e:
                logger.error(f"驱动错误 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")

            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)

        logger.error("无法建立数据库连接")
        self.driver = None
        return self

    def close(self):
        """关闭数据库连接"""
        if self.driver:
            try:
                self.driver.close()
                logger.info("Neo4j数据库连接已关闭")
            except Exception as e:
                logger.error(f"关闭数据库连接时出错: {e}")

    def query(self, query, params=None):
        """执行Cypher查询"""
        if not self.driver:
            raise Exception("数据库连接未初始化")

        with self.driver.session() as session:
            return session.run(query, params).data()

# 创建全局连接实例
driver = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD).connect().driver

def test_connection():
    """测试数据库连接是否正常"""
    if not driver:
        return False

    try:
        with driver.session() as session:
            session.run("RETURN 1").single()
        return True
    except Exception as e:
        logger.error(f"连接测试失败: {e}")
        return False
