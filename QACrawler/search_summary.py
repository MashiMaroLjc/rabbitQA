# coding:utf8

import time
from urllib.parse import quote
from Tools import Html_Tools as To
from Tools import TextProcess as T

'''
对百度、Bing 的搜索摘要进行答案的检索
（需要加问句分类接口）
'''


def baike_search(query):
    index = query.index("是什么")
    entity = query[:index]
    url = "http://baike.baidu.com/item/" + entity
    baike_soup = To.get_html_baike(url)
    r = baike_soup.find(class_='lemma-summary')
    if r == None:
        return []
    else:
        r = r.get_text().replace("\n", "").strip()
        return [r]


def kwquery(query):
    # 分词 去停用词 抽取关键词
    keywords = []
    words = T.postag(query)
    for k in words:
        # 只保留名词
        if k.flag.__contains__("n"):
            # print k.flag
            # print k.word
            keywords.append(k.word)

    answer = []
    text = ''
    # 找到答案就置1
    flag = 0

    # 抓取百度前10条的摘要
    url = 'https://www.baidu.com/s?wd=' + quote(query)
    # print(url)
    soup_baidu = To.get_html_baidu(url)
    for i in range(1, 10):
        # print("content -- {}".format(i))
        if soup_baidu == None:
            break

        results = soup_baidu.find(id=i)

        if results == None:
            print("Id{}找不到".format(i))
            continue

        # 判断是否有mu,如果第一个是百度知识图谱的 就直接命中答案
        text += results.get_text()
        if 'mu' in results.attrs:  # 一般在前三条
            # print results.attrs["mu"]
            r = results.find(class_='op_exactqa_s_answer')
            if r == None:
                # print("百度知识图谱找不到答案")
                pass
            else:
                # print r.get_text()
                # print("百度知识图谱找到答案")
                answer.append(r.get_text().strip().replace("  ", ""))
                flag = 1
                break

        # 电影栏目
        if 'mu' in results.attrs and results.attrs['mu'].__contains__(
                "http://nourl.baidu.com/"):
            if results.find(class_="c-gap-top-small") is not None:
                items = results.find_all(class_="c-gap-top-small")
                for item in items:
                    if item.find("a") is not None:
                        answer.append(item.find("a").get_text())
                flag = 1
                break
            else:
                pass

        # 天气判断
        weather_list = results.find_all(class_="op_weather4_twoicon_today OP_LOG_LINK")  # 今天的天气
        if len(weather_list) > 0:
            # print("百度天气找到了")
            weather_info = weather_list[0]
            date = weather_info.find(class_="op_weather4_twoicon_date").get_text().strip()
            C = weather_info.find(class_="op_weather4_twoicon_temp").get_text().strip()
            rain_or_not = weather_info.find(class_="op_weather4_twoicon_weath").get_text().strip()
            wind = weather_info.find(class_="op_weather4_twoicon_wind").get_text().strip()
            ans = "{}\t{}\t{}\t{}".format(date, C, rain_or_not, wind)
            answer.append(ans)
            # 获取未来的天气
            weather_list = results.find_all(class_="op_weather4_twoicon_day OP_LOG_LINK")  # 未来的天气
            for weather_info in weather_list:
                # print(weather_info)
                date = weather_info.find(class_="op_weather4_twoicon_date_day").get_text().strip()
                C = weather_info.find(class_="op_weather4_twoicon_temp").get_text().strip()
                rain_or_not = weather_info.find(class_="op_weather4_twoicon_weath").get_text().strip()
                wind = weather_info.find(class_="op_weather4_twoicon_wind").get_text().strip()
                ans = "{}\t{}\t{}\t{}".format(date, C, rain_or_not, wind)
                answer.append(ans)
            flag = 1
            break
        else:
            # print("百度天气找不到")
            pass

        # 古诗词判断
        if 'mu' in results.attrs:
            r = results.find(class_="op_exactqa_detail_s_answer")
            if r == None:
                # print("百度诗词找不到答案")
                pass
            else:
                # print r.get_text()
                # print("百度诗词找到答案")
                answer.append(r.get_text().strip())
                flag = 1
                break

        # 万年历 & 日期
        if 'mu' in results.attrs and i == 1 and results.attrs['mu'].__contains__('http://open.baidu.com/calendar'):
            r = results.find(class_="op-calendar-content")
            if r == None:
                # print("百度万年历找不到答案")
                pass
            else:
                # print r.get_text()
                # print("百度万年历找到答案")
                answer.append(r.get_text().strip().replace("\n", "").replace(" ", ""))
                flag = 1
                break

        # if 'tpl' in results.attrs and i == 1 and results.attrs['tpl'].__contains__('calendar_new'):
        #     # print(results)
        #     r = None  # results.attrs['fk'].replace("6018_", "")
        #     print(r)
        #
        #     if r == None:
        #         print("百度万年历新版找不到答案")
        #         # continue
        #     else:
        #         # print r.get_text()
        #         print("百度万年历新版找到答案")
        #         answer.append(r)
        #         flag = 1
        #         break

        # 计算器
        if 'mu' in results.attrs and results.attrs['mu'].__contains__(
                'http://open.baidu.com/static/calculator/calculator.html'):
            # r = results.find('div').find_all('td')[1].find_all('div')[1]
            r = results.find(class_="op_new_val_screen_result")
            if r == None:
                # print("计算器找不到答案")
                pass
                # continue
            else:
                # print r.get_text()
                # print("计算器找到答案")
                answer.append(r.get_text().strip())
                flag = 1
                break

        # 百度知道答案
        # if 'mu' in results.attrs:
        #     r = results.find(class_='op_best_answer_question_link')
        #     if r == None:
        #         print("百度知道图谱找不到答案")
        #     else:
        #         print("百度知道图谱找到答案")
        #         url = r['href']
        #         zhidao_soup = To.get_html_zhidao(url)
        #         r = zhidao_soup.find(class_='bd answer').find('pre')
        #         if r == None:
        #             r = zhidao_soup.find(class_='bd answer').find(class_='line content')
        #
        #         answer.append(r.get_text())
        #         flag = 1
        #         break
        #
        if results.find("h3") != None:
            # 百度知道
            # if results.find("h3").find("a").get_text().__contains__("百度知道") and (i == 1 or i == 2):
            #     url = results.find("h3").find("a")['href']
            #     if url == None:
            #         # print("百度知道图谱找不到答案")
            #         continue  # 当前id只会存在一个h3，没有答案则进入下一个id找
            #     else:
            #         # print("百度知道图谱找到答案")
            #         zhidao_soup = To.get_html_zhidao(url)
            #         r = zhidao_soup.find(class_='bd answer')
            #         if r == None:
            #             continue
            #         else:
            #             r = r.find('pre')
            #             if r == None:
            #                 r = zhidao_soup.find(class_='bd answer').find(class_='line content')
            #         text = r.get_text().strip()
            #         answer.append(text)
            #         flag = 1
            #         break

            # 百度百科
            link = results.find("h3").find("a")
            if link is not None and link.get_text().__contains__("百度百科"):
                url = results.find("h3").find("a")['href']
                if url == None:
                    # print("百度百科找不到答案")
                    continue
                else:
                    # print("百度百科找到答案")
                    baike_soup = To.get_html_baike(url)

                    r = baike_soup.find(class_='lemma-summary')
                    if r == None:
                        continue
                    else:
                        r = r.get_text().replace("\n", "").strip()
                    answer.append(r)
                    flag = 1
                    break

        text += results.get_text()

    if flag == 1:
        return answer

    # 获取bing的摘要
    soup_bing = To.get_html_bing('https://www.bing.com/search?q=' + quote(query))
    # 判断是否在Bing的知识图谱中
    # bingbaike = soup_bing.find(class_="b_xlText b_emphText")
    bingbaike = soup_bing.find(class_="bm_box")

    if bingbaike != None:
        if bingbaike.find_all(class_="b_vList")[1] != None:
            if bingbaike.find_all(class_="b_vList")[1].find("li") != None:
                # print("Bing知识图谱找到答案")
                flag = 1
                answer.append(bingbaike.get_text())
                # print "====="
                # print answer
                # print "====="
                return answer
    else:
        # print("Bing知识图谱找不到答案")
        results = soup_bing.find(id="b_results")
        bing_list = results.find_all('li')
        for bl in bing_list:
            temp = bl.get_text()
            if temp.__contains__(" - 必应网典"):
                print("查找Bing网典")
                url = bl.find("h2").find("a")['href']
                if url == None:
                    # print("Bing网典找不到答案")
                    continue
                else:
                    # print("Bing网典找到答案")
                    bingwd_soup = To.get_html_bingwd(url)

                    r = bingwd_soup.find(class_='bk_card_desc').find("p")
                    if r == None:
                        continue
                    else:
                        r = r.get_text().replace("\n", "").strip()
                    answer.append(r)
                    flag = 1
                    break

        if flag == 1:
            return answer

            # text += results.get_text()
    # 如果再两家搜索引擎的知识图谱中都没找到答案，
    # answer.append("")
    return answer


if __name__ == '__main__':
    query = "linux是什么"
    ans = kwquery(query)
    print("~~~~~~~")
    for a in ans:
        print(a)
    print("~~~~~~~")
