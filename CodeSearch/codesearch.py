from Tools import Html_Tools, TextProcess
from urllib.parse import quote
import util
import math
from .csdn import CSDN
from .bokeyuan import BKY
from .jiansh import JS
from .jiaobenzhijia import JBZJ

import util
from util import logger


class CodeSearch:
    def __init__(self, stopwords_path="./resources/code_stop_word.txt", n=10):
        """

        :param stopwords_path:
        :param n: 返回答案的数目
        """
        self._flag = 0  # 有没有找到答案的标志位
        self.stop_word = [line.strip() for line in open(stopwords_path, encoding="utf-8")]
        self.stop_word.append(" ")
        # self.stop_word.append("\t")
        # self.stop_word.append("\u3000")
        self.n = n

    def _judge_pure_english(self, keyword):
        return util.judge_pure_english(keyword)

    def _get_key_sentence(self, contents):
        """

        获得关键语句作为答案
        :param contents: 句子集合
        :return:
        """
        # 一个句子内有更高的高频词，说明句子的重要性更棒棒
        split_result = []  # 分词结果
        TF = {}
        IDF = {}
        for s in contents:
            word_list = TextProcess.cut(s)
            word_list = [word for word in word_list if word not in self.stop_word]
            split_result.append(word_list)
            for word in word_list:
                TF[word] = TF.get(word, 0) + 1
            for word in set(word_list):
                IDF[word] = IDF.get(word, 0) + 1  # 含该词的句子数，而不是出现的次数
        for k in TF:
            TF[k] = TF[k] / len(TF)
            IDF[k] = math.log(len(contents) / IDF[k])
        # 得分 词的重要性是（用tf或tf-idf衡量）/句子长度
        score = []
        for i, word_list in enumerate(split_result):
            s = 0.

            if len(word_list) <= 1 or (len(word_list) == 2 and word_list[1] == " "):
                # 只有一个词或者一个词加空格不太可能是答案
                continue
            alpha_num = 0.  # 考虑答案多为代码和命令含英文和符号超过一定比例的的权重增加
            for word in word_list:
                if self._judge_pure_english(word):
                    alpha_num += 1
                s += TF[word] * IDF[word]

            if alpha_num == 0:
                s = 0  # 一个英文字符都没，肯定是不需要的
            else:
                s = s / len(word_list)
                if (alpha_num / len(word_list)) > 0.5:
                    s = s * (1. + (alpha_num / len(word_list)))
                else:
                    s = s * (alpha_num / len(word_list))
            # print("word cut{} score:{} alpha:{}".format(word_list, s, alpha_num))
            score.append((i, s))
        score = sorted(score, key=lambda x: x[1], reverse=True)
        result = []
        if len(score) > self.n:
            score = score[:self.n]

        for pair in score:
            print(contents[pair[0]], pair[1])
            result.append(contents[pair[0]])
        return result

    def _is_include_china(self, sentence):
        return util.is_include_china(sentence)

    def query(self, query):
        ans = self.respond(query)
        if len(ans) == 0:
            return "我不懂。"
        elif len(ans) == 1:
            return ans[0]
        else:
            return "<sentence>".join(ans)

    def respond(self, query):
        """
        含有中文，查百度
        纯英文,stack_overflow
        :param query:
        :return:
        """
        if self._is_include_china(query):
            return self.china_respond(query)
        else:
            return self.stack_overflow(query)

    def _extract_stackoverflow(self, soup):
        """

        :param soup:
        :return: {accept:是否接受 code:代码部分}
        """
        result = []
        answers = soup.find(id="answers")
        accpet = answers.find(class_="answer accepted-answer")  # 被接受的答案
        if accpet is not None:
            result.append({
                "accept": 1,
                "text": [c.get_text() for c in accpet.find_all("p")]
            })
        normal_ans = soup.find_all(class_="answer")
        for ans in normal_ans:
            result.append({
                "accept": 0,
                "text": [c.get_text() for c in ans.find_all("p")]
            })
        return result

    def stack_overflow(self, query):
        url = "https://stackoverflow.com/search?q={}".format(quote(query))
        # print(url)
        soup = Html_Tools.get_html(url, clean=False)
        result_list = soup.find_all(class_="question-summary search-result")
        if len(result_list) == 0:
            logger.global_logger.info("StackOverFlow No answer")
            return []
        else:
            contents = []
            for item in result_list:
                # votes = item.find(class_="votes").get_text()
                answer = item.find(class_="status answered")
                if answer is None:
                    answer = item.find(class_="status answered-accepted")
                    if answer is None:
                        continue
                answer = answer.find("strong").get_text()
                try:
                    answer = int(answer)
                except Exception as e:
                    continue
                if answer > 0:
                    href = item.find("h3").find("a")["href"]
                    url = "https://stackoverflow.com{}".format(href)
                    new_soup = Html_Tools.get_html(url)
                    item = self._extract_stackoverflow(new_soup)
                    contents.extend(item)
            # 排序
            result = sorted(contents, key=lambda item: item["accept"], reverse=True)
            if len(result) > self.n:
                result = result[:self.n]
            return ['\n'.join(item['text']) for item in result]

    def china_respond(self, query):
        """

        思路
        百度查找，进入博客园 脚本之家 简书 CSDN 百度经验，百度知道等域下的网站，然后对text做信息抽取类的处理
        找不到就去掉query的所有中文，使用stack-overflow
        :param text:
        :return:
        """
        # 查找百度
        url = 'https://www.baidu.com/s?wd=' + quote(query)
        # print(url)
        soup_baidu = Html_Tools.get_html_baidu(url)
        contents = []
        for i in range(1, 10):
            # print("content -- {}".format(i))
            if soup_baidu == None:
                break

            results = soup_baidu.find(id=i)

            if results == None:
                # print("Id{}找不到".format(i))
                continue
            infos = results.find_all('h3')
            # key_word = TextProcess.cut(query)
            for info in infos:

                tag = info.find("a")
                if tag is None:
                    continue
                tag = tag.get_text()
                extractor = None
                if "CSDN" in tag:
                    extractor = CSDN()
                if "博客园" in tag:
                    extractor = BKY()
                if "简书" in tag:
                    extractor = JS()
                if "脚本之家" in tag:
                    extractor = JBZJ()

                if extractor is not None:
                    href = info.find("a")['href']
                    sub_soup = Html_Tools.get_html(href)
                    code_list = extractor.extract_code(sub_soup)
                    contents.extend(code_list)
                    # else:
                    #     print("{}  Can't not match a extractor".format(i))
        if len(contents) > 0:
            key_sentence = self._get_key_sentence(list(set(contents)))
        else:
            logger.global_logger.info("BaiDu No Answer")
            key_sentence = []
        return key_sentence
