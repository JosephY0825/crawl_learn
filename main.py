# -*- coding: utf-8 -*-
"""
author: JosephYan
Generate excel result from Lianjia website
"""
from crawl import LianjiaCrawl
import time
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("mainModule")
logger.setLevel(level=logging.INFO)
handler = RotatingFileHandler("log.txt", maxBytes=10*1024*1024, backupCount =3)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s')
handler.setFormatter(formatter)
# 输出到屏幕
#console = logging.StreamHandler()
logger.addHandler(handler)
#logger.addHandler(console)

def main():
    start_time = time.time()
    search_tag = "鼓楼区"
    output_filename = "1.xls"
    max_threads = 30
    jo = LianjiaCrawl(search_tag,
                      output_filename=output_filename,
                      max_threads=max_threads,
                      save_excel_flag=True)
    jo.link_crawl_with_threading()
    finish_time = time.time()
    logger.critical("Generate results all success after  %s sec." % (finish_time - start_time))


if __name__ == '__main__':
    main()
