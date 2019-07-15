from Tools import Html_Tools, TextProcess
from urllib.parse import quote
import util
import math
import time


class General:
    def __init__(self, stopwords_path, n=10, topic=5):
        """

        :param stopwords_path:
        :param n: 返回答案的数目
        :param topic 主题词个数
        """
        self._flag = 0  # 有没有找到答案的标志位
        self.stop_word = [line.strip() for line in open(stopwords_path, encoding="utf-8")]
        self.stop_word.append(" ")
        if ":" in self.stop_word:
            self.stop_word.remove(":")
        if "：" in self.stop_word:
            self.stop_word.remove("：")
        self.n = n
        self.topic = topic

    def _clean(self, text):
        """
        清理掉一些特殊符号
        :return:
        """
        symbol = ["、", "\r", "\t", "\xa0", "\u3000", "  ", ":", "："]  # 冒号可能跟原因，所以连接在一起
        for sym in symbol:
            text = text.replace(sym, "")
        # 将下面的符号断句
        # symbol = ["。", "！", "？", "?", "!", "."]
        # for sym in symbol:
        #     text = text.replace(sym, "\n")
        return text

    def _extract(self, soup):
        """
        一般的信息都是放在\<p>\</p>里面
        :param soup:
        :return:
        """
        ps = soup.find_all("p")
        result = []
        for p in ps:
            t = self._clean(p.get_text())
            result.extend(t.split("\n"))

        spans = soup.find_all("span")
        # result = []
        for p in spans:
            t = self._clean(p.get_text())
            result.extend(t.split("\n"))
        return result

    def _get_key_sentence(self, contents, query_cut):
        """
        获得关键语句作为答案
        :param contents: 句子集合
        :param query_cut: 问句提取关键词
        :return:
        """
        # 一个句子内有更高的高频词，说明句子的重要性更棒棒
        split_result = []  # 分词结果
        TF = {}
        IDF = {}
        TF_IDF = {}
        for s in contents:
            word_list = TextProcess.cut(s)
            word_list = list(set([word for word in word_list if word not in self.stop_word]))
            split_result.append(word_list)
            for word in word_list:
                TF[word] = TF.get(word, 0) + 1
            for word in set(word_list):
                IDF[word] = IDF.get(word, 0) + 1  # 含该词的句子数，而不是出现的次数
        for k in TF:
            TF[k] = TF[k] / len(TF)
            IDF[k] = math.log(len(contents) / IDF[k])
            TF_IDF[k] = TF[k] * IDF[k]
        topic_word = sorted(TF_IDF, key=lambda k: TF_IDF[k], reverse=True)
        topic_word = topic_word[:self.topic]
        # print("Query:", query_cut)
        # print("Topic:", topic_word)
        # 得分 词的重要性是（用tf或tf-idf衡量）/句子长度
        score = []
        for i, word_list in enumerate(split_result):
            s = 0.
            if len(word_list) <= 1 or (len(word_list) == 2 and word_list[1] == " "):
                # 只有一个词或者一个词加空格不太可能是答案
                continue
            # print("sentence:{}\nwortcut:{}".format(contents[i], word_list))
            for word in word_list:
                w = 0
                if word in query_cut:
                    # print("Word {} in query".format(word))
                    w += 0.5
                if word in topic_word:
                    # print("Word {} in topic".format(word))
                    w += 0.5
                s += TF_IDF[word] * w
            # s = s / len(word_list)
            score.append((i, s))
            # print("Score:{:.5f}".format(s))
            # print("-------------------------------------")
        score = sorted(score, key=lambda x: x[1], reverse=True)
        result = []
        if len(score) > self.n:
            score = score[:self.n]
        for pair in score:
            result.append(contents[pair[0]])
        return result

    def respond(self, query):
        """
        采用文本摘要等技术来完成更广泛提问的总结
        :param query:
        :return:
        """
        # 查找百度
        url = 'https://www.baidu.com/s?wd=' + quote(query)
        # print(url)
        t1 = time.time()
        soup_baidu = Html_Tools.get_html_baidu(url)
        # print("Query Baidu:{}".format(time.time() - t1))
        contents = []
        key_word = list(TextProcess.postag(query))  # (word tag)
        key_word = [word for word, tag in key_word if (word not in self.stop_word and "n" in tag)]
        t1 = time.time()
        for i in range(1, 10):
            # print("content -- {}".format(i))
            if soup_baidu == None:
                break

            results = soup_baidu.find(id=i)

            if results == None:
                # ("Id{}找不到".format(i))
                continue
            infos = results.find_all('h3')

            for info in infos:

                tag = info.find("a")
                if tag is None:
                    continue
                else:
                    href = tag['href']
                    if "www.baidu.com/link" not in href:
                        continue
                    try:
                        sub_soup = Html_Tools.get_html(href)
                        info_list = self._extract(sub_soup)
                        # 句子级的过滤
                        for info in info_list:
                            # 问句过滤
                            if any(["?" in info, "？" in info]):
                                continue
                            else:
                                contents.append(info)
                    except:
                        pass
        # print("For :{}".format((time.time() - t1) / 10))
        if len(contents) > 0:
            t1 = time.time()
            key_sentence = self._get_key_sentence(list(set(contents)), key_word)
            # print("Key Sentence:{}".format(time.time() - t1))
        else:
            key_sentence = []
        # print()
        return key_sentence
