import os
import pyltp

# ltp模型目录的路径
LTP_DATA_DIR = 'C:/Users/86182/A/KGQA_SG-master/KGQA/ltp-models/ltp_data_v3.'

def cut_words(words):
    segmentor = pyltp.Segmentor()
    seg_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
    segmentor.load(seg_model_path)
    words = segmentor.segment(words)
    array_str = "|".join(words)
    array = array_str.split("|")
    segmentor.release()
    return array

def pos_tagging(words):
    postagger = pyltp.Postagger()
    pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')
    postagger.load(pos_model_path)
    postags = postagger.postag(words)
    postagger.release()
    return list(postags)

def ner(words, postags):
    recognizer = pyltp.NamedEntityRecognizer()
    ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')
    recognizer.load(ner_model_path)
    netags = recognizer.recognize(words, postags)
    recognizer.release()
    return list(netags)

def parse_question(question):
    words = cut_words(question)
    postags = pos_tagging(words)
    netags = ner(words, postags)
    return words, postags, netags
