# coding:utf-8
# 全局的日志
import logging
import time
import os


class _Logger:
    def __init__(self):
        logger = logging.getLogger('QA')
        logger.setLevel(logging.DEBUG)
        now = int(time.time())  # 1533952277
        timeArray = time.localtime(now)
        t = time.strftime("%Y%m%d-%H%M%S", timeArray)
        log_file = os.path.join("./log", "log_{}.txt".format(t))
        handler = logging.FileHandler(log_file, encoding="utf-8")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.info("Create the log in {}".format(t))
        self.logger = logger

    def __call__(self, *args, **kwargs):
        return self.logger


global_logger = _Logger()()
