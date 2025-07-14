import os
import pyltp
import logging
from typing import Tuple, List, Dict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# LTP模型目录的路径（请根据实际路径修改）
LTP_DATA_DIR = 'C:/Users/86182/A/KGQA_SG-master/KGQA/ltp-models/ltp_data_v3.'

# 检查模型文件是否存在
def check_model_files():
    """验证LTP模型文件是否存在"""
    required_models = ['cws.model', 'pos.model', 'ner.model', 'parser.model']
    missing = []
    for model in required_models:
        model_path = os.path.join(LTP_DATA_DIR, model)
        if not os.path.exists(model_path):
            missing.append(model)
    if missing:
        logger.error(f"缺少LTP模型文件：{', '.join(missing)}")
        raise FileNotFoundError(f"LTP模型文件缺失：{', '.join(missing)}")
    return True

# 确保模型文件存在
try:
    check_model_files()
except FileNotFoundError as e:
    logger.error(f"初始化失败：{str(e)}")
    raise

class LTPProcessor:
    """LTP自然语言处理工具类，封装分词、词性标注、命名实体识别和依存句法分析"""

    def __init__(self):
        # 初始化LTP工具（延迟加载以节省内存）
        self.segmentor = None
        self.postagger = None
        self.recognizer = None
        self.parser = None

    def __enter__(self):
        """上下文管理器进入时初始化工具"""
        self.load_tools()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出时释放资源"""
        self.release_tools()

    def load_tools(self):
        """加载LTP工具"""
        try:
            # 分词工具
            self.segmentor = pyltp.Segmentor()
            seg_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
            self.segmentor.load(seg_model_path)

            # 词性标注工具
            self.postagger = pyltp.Postagger()
            pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')
            self.postagger.load(pos_model_path)

            # 命名实体识别工具
            self.recognizer = pyltp.NamedEntityRecognizer()
            ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')
            self.recognizer.load(ner_model_path)

            # 依存句法分析工具
            self.parser = pyltp.Parser()
            parse_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')
            self.parser.load(parse_model_path)

            logger.info("LTP工具加载成功")
        except Exception as e:
            logger.error(f"LTP工具加载失败：{str(e)}")
            self.release_tools()
            raise

    def release_tools(self):
        """释放LTP工具资源"""
        if self.segmentor:
            self.segmentor.release()
        if self.postagger:
            self.postagger.release()
        if self.recognizer:
            self.recognizer.release()
        if self.parser:
            self.parser.release()
        logger.info("LTP工具资源已释放")

    def cut_words(self, text: str) -> List[str]:
        """
        对文本进行分词
        :param text: 输入文本
        :return: 分词结果列表
        """
        if not self.segmentor:
            raise RuntimeError("LTP分词工具未初始化，请先调用load_tools()")

        try:
            words = self.segmentor.segment(text)
            return list(words)
        except Exception as e:
            logger.error(f"分词失败：{str(e)}")
            return []

    def pos_tagging(self, words: List[str]) -> List[str]:
        """
        对分词结果进行词性标注
        :param words: 分词列表
        :return: 词性标注列表
        """
        if not self.postagger:
            raise RuntimeError("LTP词性标注工具未初始化，请先调用load_tools()")

        try:
            postags = self.postagger.postag(words)
            return list(postags)
        except Exception as e:
            logger.error(f"词性标注失败：{str(e)}")
            return []

    def ner(self, words: List[str], postags: List[str]) -> List[str]:
        """
        命名实体识别
        :param words: 分词列表
        :param postags: 词性标注列表
        :return: 实体识别结果列表
        """
        if not self.recognizer:
            raise RuntimeError("LTP命名实体识别工具未初始化，请先调用load_tools()")

        try:
            netags = self.recognizer.recognize(words, postags)
            return list(netags)
        except Exception as e:
            logger.error(f"命名实体识别失败：{str(e)}")
            return []

    def dependency_parse(self, words: List[str], postags: List[str]) -> List[Tuple[int, int, str]]:
        """
        依存句法分析
        :param words: 分词列表
        :param postags: 词性标注列表
        :return: 依存关系列表，每个元素为(源节点, 目标节点, 关系类型)
        """
        if not self.parser:
            raise RuntimeError("LTP句法分析工具未初始化，请先调用load_tools()")

        try:
            arcs = self.parser.parse(words, postags)
            return [(arc.head, arc.relation) for arc in arcs]
        except Exception as e:
            logger.error(f"依存句法分析失败：{str(e)}")
            return []

    def parse_question(self, question: str) -> Dict[str, List]:
        """
        完整解析问题，返回分词、词性、实体和依存关系
        :param question: 输入问题
        :return: 解析结果字典
        """
        try:
            words = self.cut_words(question)
            postags = self.pos_tagging(words) if words else []
            netags = self.ner(words, postags) if words and postags else []
            dependencies = self.dependency_parse(words, postags) if words and postags else []

            return {
                "words": words,
                "postags": postags,
                "netags": netags,
                "dependencies": dependencies
            }
        except Exception as e:
            logger.error(f"问题解析失败：{str(e)}")
            return {
                "words": [],
                "postags": [],
                "netags": [],
                "dependencies": []
            }


# 便捷使用函数
def process_question(question: str) -> Dict[str, List]:
    """
    处理单个问题的快捷函数
    :param question: 输入问题
    :return: 解析结果
    """
    with LTPProcessor() as processor:
        return processor.parse_question(question)


# 测试代码
if __name__ == "__main__":
    test_question = "李白和杜甫是什么关系？"
    result = process_question(test_question)

    print("问题：", test_question)
    print("分词结果：", result["words"])
    print("词性标注：", result["postags"])
    print("实体识别：", result["netags"])
    print("依存关系：", result["dependencies"])
