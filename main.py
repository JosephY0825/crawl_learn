# -*- coding: utf-8 -*-
"""
author: JosephYan
Generate excel result from Lianjia website
"""
from crawl import LianjiaCrawl
import time
from mongocache import MongoQueue


def main():
    start_time = time.time()
    search_tag = "小营小学"
    output_filename = "1.xls"
    max_threads = 30
    test_flag = True
    jo = LianjiaCrawl(
        search_tag=search_tag, output_filename=output_filename,
        max_threads=max_threads, test_flag=test_flag)
    # jo.link_crawl()
    jo.link_crawl_with_threading()
    finish_time = time.time()
    print "处理完毕,用时%s" % (finish_time - start_time)


if __name__ == '__main__':
    main()
