import json
import random
import re


class KV:
    def __init__(self, knowledge):
        self.knowledge = knowledge


    def respond(self, text):
        if "qa" not in self.knowledge:
            raise ValueError("The kv database need the 'qa' key.")

        answer = []
        for kv in self.knowledge["qa"]:
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

        return answer
