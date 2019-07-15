from gensim.summarization.summarizer import summarize
from Tools import TextProcess


def get_summarize(text, radio=0.2):
    """
    将中文表达换成英文表达，再调用summarize
    词语划分用空格，句子划分用英文句号
    :param text:
    :param radio:
    :return:
    """

    return summarize(text, radio)


def split_sentence_from_text(text):
    chinese_split = ["！", "!", "。", "？", "?", "\n", "\r"]
    text = text.replace("  ", "").replace("\t", "").replace("\xa0", "")
    for sym in chinese_split:
        text = text.replace(sym, '<split>')
    result = [sentence for sentence in text.split("<split>") if len(sentence) > 0]
    return list(set(result))


def is_include_china(sentence):
    for ch in sentence:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


def judge_pure_english(keyword):
    return all((65 <= ord(c) <= 90 or 97 <= ord(c) <= 122) for c in keyword)
