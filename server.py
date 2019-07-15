from flask import Flask, request, render_template
from CodeSearch import codesearch
import json
from robot import Robot
from util import logger
import time

app = Flask(__name__)


# model = Seq2Seq()
class Model():
    def __init__(self):
        self.model = None

    def setModel(self, model):
        self.model = model

    def query(self, text, past):
        return self.model.query(text, past)


model = Model()
CodeSearch = codesearch.CodeSearch()


@app.route('/check_alive', methods=["POST", 'GET'])
def check_alive():
    """
    如果服务器在正常运行，那就返回0，大于0为错误玛
    :return:
    """
    result = {"status": 0}
    return json.dumps(result)


@app.route('/dialogue', methods=['POST', 'GET'])
def get_dialogue():
    """
    json 格式
    text：当前句子 str
    past: 过去的句子 list
    :return:
    """
    # 返回的json数据
    # ans 回复
    # status 0 成功, >0 为错误码
    # time 时间（s）
    # 300 - 399 服务器错误
    # info 错误信息
    result = {
        "ans": "",
        "status": 0,
        "info": "",
        "time": -1
    }
    json_obj = request.get_json(force=True)
    if json_obj is None:
        result["status"] = 100
        result["info"] = "Illegal Params"
    else:
        text = json_obj.get("text", "")
        past = json_obj.get("past", [])
        try:
            t1 = time.time()
            ans = model.query(text, past)
            result["time"] = "{:.2f}s".format(time.time() - t1)
            result["ans"] = ans.replace("\n", "")
        except Exception as e:
            logger.global_logger.debug("Exception: {}".format(e))
            result["status"] = 300
            result["info"] = "raise a exception."
    return json.dumps(result)


@app.route('/code', methods=['POST', 'GET'])
def get_code():
    """
    json 格式
    text：当前句子 str
    past: 过去的句子 list
    :return:
    """
    # 返回的json数据
    # ans 回复
    # status 0 成功, >0 为错误码
    # time 时间（s）
    # 300 - 399 服务器错误
    # info 错误信息
    result = {
        "ans": "",
        "status": 0,
        "info": "",
        "time": -1
    }
    json_obj = request.get_json(force=True)
    if json_obj is None:
        result["status"] = 100
        result["info"] = "Illegal Params"
    else:
        text = json_obj.get("text", "")
        past = json_obj.get("past", [])
        try:
            t1 = time.time()
            ans = CodeSearch.query(text)
            result["time"] = "{:.2f}s".format(time.time() - t1)
            result["ans"] = ans.replace("\n", "")
        except Exception as e:
            logger.global_logger.debug("Exception: {}".format(e))
            result["status"] = 300
            result["info"] = "raise a exception."
    return json.dumps(result)


@app.route("/", methods=["GET"])
def home_page():
    return render_template("index.html")


if __name__ == "__main__":
    robot = Robot()
    model.setModel(robot)
    app.run(host="0.0.0.0", port=8888, debug=True)
