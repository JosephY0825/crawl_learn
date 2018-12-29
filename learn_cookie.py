# encoding: utf-8
# !/usr/bin/env python
import cookielib
import requests

def format_output(resp):
    print resp.status_code, resp.reason
    for key in resp.headers:
        print key + ":" + resp.headers.get(key)
    print "\n" + resp.text

def main():
    s = requests.session()
    """
    https://blog.csdn.net/zhu_free/article/details/50563756
    https://blog.csdn.net/falseen/article/details/46962011
    """
    headers_1 = {
        "test": "yx",
        "user-agent": "2"
    }
    filename = "cookies.txt"
    my_cookies = {"abc": "123"}
    resp = s.get("http://10.47.159.140:9080/get_cookie", headers=headers_1)
    format_output(resp)
    new_cookie_jar = cookielib.LWPCookieJar(filename)

    for c in s.cookies:
        new_cookie_jar = requests.utils.cookiejar_from_dict({c.name: c.value}, new_cookie_jar)

    new_cookie_jar.save(filename, ignore_discard=True, ignore_expires=True)

if __name__ == '__main__':
    main()