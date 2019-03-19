# coding: utf-8
import urllib
import requests
import json
import re
import sys
import getopt

def get_1haodian_url(product_url):
    # 商品ID
    product_id = re.findall(r'com/(.*?).html', product_url)[0]
    url_dict = {
        # "extraParam": "{\"originid\":\"1\"}",
        # "ch": "9",
        # "callback": "jQuery1113013499259665725116_1552625201304",  # 回调参数?
        "skuId": "%s" % product_id,     # 商品ID
        "area": "2_2817_51973_0",       # 地区ID
        "cat": "1319,1527,1559",
        # "buyNum": "1",
        # "venderId": "1000000745",
        # "fqsp": "0",
        # "coord": "",
        # "_": "1552625201305",
    }
    url_data = urllib.urlencode(url_dict)
    req_url = "https://c0.3.cn/stock?"+url_data
    # 设置请求头
    request_header = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
        #"Cookie": "c3cn=Ef9Ms03P",
        #"Host": "c0.3.cn",
        "Referer": "https://item.yhd.com/%s.html" % product_id,
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
    }

    sess = requests.session()
    sess.headers = request_header
    resp = sess.get(url=req_url)
    result = resp.text
    json_result = json.loads(result)
    # 将所有的类json数据格式化存入字典
    print "库存: %s 价格: %s" %(json_result["stock"]["StockStateName"].encode("utf-8"), json_result["stock"]["jdPrice"]["p"].encode("utf-8"))


def usage():
    message = '''
    python test_jd.py [-h] [-u https://item.jd.com/xxx.html]
    -h:         print this message
    -u:         request url
    '''
    print message


if __name__ == "__main__":
    request_url = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:", ["url="])
        for op, value in opts:
            if op == "-u" or op == "--url":
                request_url = value
                get_1haodian_url(request_url)
            elif op == "-h":
                usage()
            else:
                usage()
    except Exception as e:
        print 'Error: %s' % str(e)