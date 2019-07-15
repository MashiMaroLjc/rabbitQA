# coding:utf8

import urllib.request, urllib.parse, urllib.error
import re
from bs4 import BeautifulSoup
import requests, time
import random

from requests.cookies import RequestsCookieJar

'''
获取百度知道的页面
'''


def get_html_zhidao(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686)Gecko/20071127 Firefox/2.0.0.11'}
    soup_zhidao = BeautifulSoup(requests.get(url=url, headers=headers, timeout=10).content, "lxml")

    # 去除无关的标签
    [s.extract() for s in soup_zhidao(['script', 'style', 'img'])]
    # print(soup.prettify())
    return soup_zhidao


'''
获取百度百科的页面
'''


def get_html_baike(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686)Gecko/20071127 Firefox/2.0.0.11'}
    soup_baike = BeautifulSoup(requests.get(url=url, headers=headers, timeout=10).content, "lxml")

    # 去除无关的标签
    [s.extract() for s in soup_baike(['script', 'style', 'img', 'sup'])]
    # print(soup.prettify())
    return soup_baike


'''
获取任意一个html的网页
'''


def get_html(url,clean=True):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686)Gecko/20071127 Firefox/2.0.0.11'}
    soup_html = BeautifulSoup(requests.get(url=url, headers=headers, timeout=10).content, "lxml")

    # 去除无关的标签
    if clean:
        [s.extract() for s in soup_html(['script', 'style'])]
    # print(soup.prettify())
    return soup_html


'''
获取Bing网典的页面
'''


def get_html_bingwd(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686)Gecko/20071127 Firefox/2.0.0.11'}
    soup_bingwd = BeautifulSoup(requests.get(url=url, headers=headers, timeout=10).content, "lxml")

    # 去除无关的标签
    [s.extract() for s in soup_bingwd(['script', 'style', 'img', 'sup', 'b'])]
    # print(soup.prettify())
    return soup_bingwd


'''
获取百度搜索的结果
'''


def get_html_baidu(url):
    # headers =
    # User_Agent = random.choice([
    #     {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686)Gecko/20071127 Firefox/2.0.0.11'},
    #     {
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
    # ])

    headers = {
        'Host': 'www.baidu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/73.0.3683.103 Safari/537.36',

    }
    cookie_jar = RequestsCookieJar()
    cookie_jar.set("BAIDUID", "D720A5546E0B92653F503EB940BE1374:FG=1", domain="baidu.com")
    a = "D720A5546E0B92653F503EB940BE1374:FG=1"  # "B1CCDD4B4BC886BF99364C72C8AE1C01:FG=1"
    soup_baidu = BeautifulSoup(requests.get(url=url, headers=headers, cookies=cookie_jar, timeout=10).content, "lxml")

    # 去除无关的标签
    [s.extract() for s in soup_baidu(['script', 'style', 'img'])]
    # print(soup.prettify())
    return soup_baidu


'''
获取Bing搜索的结果
'''


def get_html_bing(url):
    # url = 'http://global.bing.com/search?q='+word
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
    soup_bing = BeautifulSoup(requests.get(url=url, headers=headers, timeout=10).content.decode('utf-8'), "lxml")

    # 去除无关的标签
    # [s.extract() for s in soup_bing(['script', 'style','img'])]
    return soup_bing


'''
print answer
'''


def ptranswer(ans, ifhtml):
    result = ''
    # print ans
    for answer in ans:
        if ifhtml:
            print(answer)
        else:
            if answer == '\n':
                # print '回车'
                continue
            p = re.compile('<[^>]+>')
            # print '##############'
            # print answer
            # print type(answer)
            # if answer.name == 'br':
            #     continue
            # print p.sub("", answer.string)
            # print '##############'
            result += p.sub("", answer.string).encode('utf8')
    return result


def ltptools(args):
    url_get_base = "http://api.ltp-cloud.com/analysis/"
    result = urllib.request.urlopen(url_get_base, urllib.parse.urlencode(args))  # POST method
    content = result.read().strip()
    return content


if __name__ == '__main__':
    pass
    # args = {
    #     'api_key' : 'F1e194G841HHvTDhqb4JsGrHHw4Q0DYFbzKqgQNm',
    #     'text' : '太阳为什么是圆的。',
    #     'pattern' : 'srl',
    #     'format' : 'json'
    # }
    # content = ltptools(args=args)
    # print content
