from QACrawler import search_summary
import kv
from util import logger
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
        self.kv = kv.KV(self.config)
        self.last_text = None
        self.qa = SqliteQA(db_path, kv_path[0], stopwords_path, model_path)
        self.gen = General(stopwords_path)
        self.multiprocess_queue = Queue()

    def _replace(self, s, src_list, target):
        for src in src_list:
            s = s.replace(src, target)
        return s

    def _replace_standard(self, text):
        # 先检查标准问答进行替换
        if "standard" in self.config:
            ori_text = text
            for kv in self.config["standard"]:
                pattern = kv["pattern"]
                mode = kv.get("mode", "equal")
                if mode == "equal" and pattern == text:
                    replace = kv.get("replace", None)
                    if replace is None:
                        text = kv["standard"]
                    else:
                        text = self._replace(text, replace["src"], replace["target"])
                    logger.global_logger.info("text {} 替换成 {}".format(ori_text, text))
                    break
                if mode == "in" and pattern in text:
                    replace = kv.get("replace", None)
                    if replace is None:
                        text = kv["standard"]
                    else:
                        text = self._replace(text, replace["src"], replace["target"])
                    logger.global_logger.info("text {} 替换成 {}".format(ori_text, text))
                    break
                if mode == "re" and re.search(pattern, text) is not None:
                    replace = kv.get("replace", None)
                    if replace is None:
                        text = kv["standard"]
                    else:
                        text = self._replace(text, replace["src"], replace["target"])
                    logger.global_logger.info("text {} 替换成 {}".format(ori_text, text))
                    break
        return text

    def get_respond(self, text) -> list:
        """
        当几个接口找不到答案时，返回[]
        :param text:
        :return:
        """
        if len(text) == 0:
            return []
        text = self._replace_standard(text)
        ans = self.kv_search(text)
        if len(ans) == 0 and re.search(".{2,10}是什么", text) is not None:
            ans = search_summary.baike_search(text)
        if len(ans) == 0:
            ans = self._search_engine(text)
        if len(ans) == 0:
            ans = self.qa_search(text)
        if len(ans) == 0:
            ans = self.gen.respond(text)
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
