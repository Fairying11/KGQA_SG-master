# -*- coding: utf-8 -*-
import pyltp
import os

# 可以将 LTP 模型目录路径作为配置项，方便修改
LTP_DATA_DIR = 'C:/Users/86182//KGQA_SG-master/KGQA/ltp-models/ltp_data_v3.4.0'

def cut_words(words):
    """
    分词函数
    :param words: 输入的文本
    :return: 分词后的列表
    """
    segmentor = pyltp.Segmentor()
    seg_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
    segmentor.load(seg_model_path)
    words = segmentor.segment(words)
    result = list(words)
    segmentor.release()
    return result

def words_mark(array):
    """
    词性标注函数
    :param array: 分词后的列表
    :return: 词性标注后的列表
    """
    pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')
    postagger = pyltp.Postagger()
    postagger.load(pos_model_path)
    postags = postagger.postag(array)
    result = list(postags)
    postagger.release()
    return result

def get_target_array(words):
    """
    获取目标词汇数组
    :param words: 输入的文本
    :return: 目标词汇数组
    """
    target_pos = ['nh', 'n']
    seg_array = cut_words(words)
    pos_array = words_mark(seg_array)
    target_array = [seg_array[i] for i in range(len(pos_array)) if pos_array[i] in target_pos]
    if len(seg_array) > 1:
        target_array.append(seg_array[1])
    return target_array
