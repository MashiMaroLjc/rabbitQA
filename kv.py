import json
import random
import re
from util import logger


class KV:
    def __init__(self, knowledge, standard):
        self.knowledge = knowledge
        self.standard = standard

    def _replace(self, s, src_list, target):
        for src in src_list:
            s = s.replace(src, target)
        return s

    def _replace_standard(self, text):
        # 先检查标准问答进行替换
        ori_text = text
        for kv in self.standard:
            pattern = kv["pattern"]
            mode = kv.get("mode", "equal")
            if mode == "equal" and pattern == text:
                replace = kv.get("replace", None)
                if replace is None:
                    text = kv["standard"]
                else:
                    text = self._replace(text, replace["src"], replace["target"])
                break
            if mode == "in" and pattern in text:
                replace = kv.get("replace", None)
                if replace is None:
                    text = kv["standard"]
                else:
                    text = self._replace(text, replace["src"], replace["target"])
                break
            if mode == "re" and re.search(pattern, text) is not None:
                replace = kv.get("replace", None)
                if replace is None:
                    text = kv["standard"]
                else:
                    text = self._replace(text, replace["src"], replace["target"])
                break
        result = {"origin": ori_text, "new": text}
        return result

    def respond(self, text):
        """
        获取回答
        :param text:
        :return:
        """
        # 进行问答的标准化
        result = self._replace_standard(text)

        if result["origin"] != result["new"]:
            logger.global_logger.info("[Replace] origin:{} new:{}".format(result["origin"], result["new"]))
            text = result["new"]
        # 再进行模板匹配,结果可能是以 # 开头的意图或直接为答案
        # print("new result_new --- text:{}  --- {}".format(result["new"], text))
        return self._respond(text)

    def _respond(self, text):

        answer = []
        for kv in self.knowledge:
            pattern = kv["pattern"]
            mode = kv.get("mode", "equal")
            if mode == "equal" and pattern == text:
                ans = random.choice(kv["ans"])
                answer.append(ans)
                break
            if mode == "in" and pattern in text:
                ans = random.choice(kv["ans"])
                answer.append(ans)
                break
            if mode == "re" and re.search(pattern, text) is not None:
                ans = random.choice(kv["ans"])
                answer.append(ans)
                break

        return answer, text
