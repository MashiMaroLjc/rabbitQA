from QACrawler import search_summary
import kv

import json
import re
import random
from multiprocessing import Process, Queue, queues
from QACrawler import General
from SqliteQA import SqliteQA
import time


class Robot:
    def __init__(self, db_path="./db/qa.db", kv_path=("./resources/kv.json",),
                 stopwords_path="./resources/stopwords.txt",
                 model_path="./word2vec/word2vec_wordlevel_weibo"):
        self.config = {}
        for path in kv_path:
            json_data = json.load(open(path, "r", encoding="utf-8"))
            self.config.update(json_data)
        self.kv = kv.KV(self.config['qa'], self.config["standard"])
        self.last_text = None
        self.qa = SqliteQA(db_path, kv_path[0], stopwords_path, model_path)
        self.gen = General(stopwords_path)
        # self.multiprocess_queue = Queue()

    def _exec_intent(self, intent, text):
        ans = []
        if intent == "search_engine":
            # 搜索引擎
            ans = self._search_engine(text)
        elif intent == "baike":
            ans = search_summary.baike_search(text)
        elif intent == "communities":
            ans = self.qa_search(text)
        elif intent == "summery":
            # 对知识进行归纳
            ans = self.gen.respond(text)
        # 其余情况为不懂
        return ans

    def stop(self):
        self.qa.close()

    def get_respond(self, text) -> list:
        """
        当几个接口找不到答案时，返回[]

        :param text:
        :return:
        """
        if len(text) == 0:
            return []
        ans, text = self.kv_search(text)  # text会被更改为标准问法
        if len(ans) == 0:
            # 找不到答案默认用搜索引擎和归纳
            ans.append("#search_engine&summery")
        if len(ans) == 1 and ans[0].startswith("#"):
            intents = ans[0][1:]
            # 按照意图来弄
            # 用&分割多个意图串行，直到结束或找到答案

            intent_list = intents.split("&")
            print("text {} intents:{}".format(text, intent_list))
            for intent in intent_list:
                ans = self._exec_intent(intent, text)
                if len(ans) > 0:
                    break
        return ans

    def query(self, text, past):
        """
        用于flask接口，
        请求和上下文管理，直接返回答案
        目前不支持上下文
        :param text:
        :param past:
        :return:
        """
        ans = self.get_respond(text)
        if len(ans) == 0:
            return "你说的这些我不懂哦"
        if len(ans) == 1:
            return ans[0]
        else:
            return "<sentence>".join(ans)

    def kv_search(self, text):
        return self.kv.respond(text)

    def _search_engine(self, text):
        """
        开放域的问答
        :param text:
        :return:
        """
        ans = search_summary.kwquery(text)
        return ans

    def qa_search(self, text):
        """
        QA库的问答，
        本地查询，
        但较慢
        :param text:
        :return:
        """
        a = self.qa.respond(text)
        if len(a) > 0:
            pair = random.choice(a)
            return [pair[1]]
        else:
            return []
