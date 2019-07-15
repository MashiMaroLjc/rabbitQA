import sqlite3
from Tools import TextProcess
import time
import gensim
import random
import numpy as np
from scipy.linalg import norm
from util import logger


class SqliteQA:
    def __init__(self, db, stop_words, stopwords_path="./resources/stopwords.txt",
                 model_path="./word2vec/word2vec_wordlevel_weibo"):
        self.cursor = sqlite3.connect(db, check_same_thread=False).cursor()
        self.stop_words = []
        with open(stop_words, encoding='utf-8') as f:
            for line in f.readlines():
                self.stop_words.append(line.strip('\n'))
        self.stop_word = [line.strip() for line in open(stopwords_path, encoding="utf-8")]
        self.unk = "<UNK>"
        self.model = gensim.models.Word2Vec.load(model_path)
        # self.model = gensim.models.KeyedVectors.load_word2vec_format(model_path, binary=True)

    def vector_similarity(self, s1, s2):
        def sentence_vector(words):
            # words = jieba.lcut(s)
            v = np.zeros(64)
            for word in words:
                v += self.model[word]
            v /= len(words)
            return v

        v1, v2 = sentence_vector(s1), sentence_vector(s2)
        return np.dot(v1, v2) / (norm(v1) * norm(v2))

    def sentence_emb(self, word_list):
        emb1 = 0
        for word in word_list:
            if word in self.model:
                emb1 += self.model[word]
            else:
                # print(word, self.unk)
                emb1 += self.model[self.unk]
        emb1 = emb1 / len(word_list)
        return emb1

    def _similarity(self, t1, t2):
        """
        百度api存在qps的问题
        :param t1:
        :param t2:
        :return:
        """
        t1_list = [word for word in TextProcess.cut(t1) if word not in self.stop_word]
        t2_list = [word for word in TextProcess.cut(t2) if word not in self.stop_word]
        em1 = self.sentence_emb(t1_list)
        em2 = self.sentence_emb(t2_list)
        score = self.cos(em1, em2)
        # score = self.vector_similarity(t1_list, t2_list)
        score = score * 0.5 + 0.5  # 归一化
        return 1, score

    def cos(self, a, b):
        score = np.dot(a, b) / (norm(a) * norm(b))
        return score

    def respond(self, text):

        question = list(TextProcess.postag(text))  # 对查询字符串进行分词
        keywords = []
        # print(question)
        logger.global_logger.info("query: {}  cut:{}".format(text, question))
        for word, tag in question:  # 去除停用词
            if word in self.stop_words:
                continue
            if 'n' not in tag or "un" == tag:  # and 'v' not in tag:
                # 保证名词进去keyword，即保证对象描述不会太远，后面再用语义匹配方法匹配出来
                continue
            keywords.append(word)
        if len(keywords) == 0:
            # 如果一个名词都没有，放动词
            for word, tag in question:  # 去除停用词
                if word in self.stop_words:
                    continue
                if 'v' not in tag:  # and 'v' not in tag:
                    # 保证名词进去keyword，即保证对象描述不会太远，后面再用语义匹配方法匹配出来
                    continue
                keywords.append(word)

        # 匹配keyword
        # condition = [" QUESTION like \'%{}%\'".format(keyword) for keyword in keywords] # 慢
        condition = [" instr(QUESTION, '{}') > 0 ".format(keyword) for keyword in keywords]  # 快
        if len(condition) == 0:
            return []
        sql = "select QUESTION ,ANSWER from qa_pair where {}".format("and".join(condition))
        logger.global_logger.info("going to execute this sql: {}".format(sql))
        result = self.cursor.execute(sql)  # (id ,q,a)
        res = []
        # 计算所有问题和问句得相似度,排序
        for row in result:
            q = row[0]
            a = row[1]
            state, sim = self._similarity(text, q)
            # logger.global_logger.info("text:{}  query:{} score:{}".format(text, q, sim))
            if state == 0:
                raise Exception("similarity Api Error.")
            elif sim > 0.9:
                res.append((q, a, sim))
        # 挑选得分第一的返回（可以并列）
        finall = []
        if len(res) > 0:
            ans = sorted(res, key=lambda x: x[2], reverse=True)
            score = -1
            for a in ans:
                if a[2] > score:
                    score = a[2]
                    logger.global_logger.info("[MATCH RESULT]{} match:{} score:{}".format(text, a[0], score))
                    finall.append((a[0], a[1]))
                elif a[2] == score:
                    finall.append((a[0], a[1]))
        # else:
        #     finall.append(("", ""))
        return finall


if __name__ == "__main__":
    # 遍历全表基本要10秒
    qs = [
        "六一儿童节去哪儿玩好",
        "六一儿童节送什么礼物好？",
        "女朋友和妈妈掉进水里，我该救谁?",
        "怎么减肥？",
        "独自出行需要注意些什么?",
        "有什么经典的动漫?",
        "《钢之炼金术师》最感动你的是什么",
        "更年期吃什么?",
    ]
    qa = SqliteQA("./db/qa.db", "./resources/kv.json")
    t1 = time.time()
    for q in qs:
        a = qa.respond(q)
        if len(a) > 0:
            pair = random.choice(a)
            logger.global_logger.info("{} match question {} --- ans:{}".format(q, pair[0], pair[1]))
            print("Q:{}\nA:{}".format(q, pair[1]))
        else:
            print("Q:{}\nA:{}".format(q, "no ans"))
        print()
    print("Average Cost Time:{:.5f}".format((time.time() - t1) / len(qs) ))
