# -*- coding: utf-8 -*-
import requests
from lxml import etree
import datetime
import xlwt
import threading
from Mongocache import MongoCache
import logging

module_logger = logging.getLogger("mainModule.sub")

class LianjiaCrawl(object):
    def __init__(self, search_tag, output_filename, max_threads=10, **kwargs):
        """
        :param search_tag:
        :param output_filename:
        :param max_threads:
        :param kwargs: save_db_flag
        """
        self.search_tag = search_tag
        self.output_filename = output_filename
        self.search_result = []     # 存放house_id的list
        self.result = {}
        self.max_threads = max_threads
        kwargs.setdefault("save_db_flag", True)
        kwargs.setdefault("save_excel_flag", True)
        kwargs.setdefault("db_host", "127.0.0.1")
        kwargs.setdefault("db_port", 27017)
        kwargs.setdefault("db_name", "test_tmp")
        kwargs.setdefault("log_filename", "crawl.log")
        self.db_host = kwargs.get("db_host")
        self.db_port = kwargs.get("db_port")
        self.db_name = kwargs.get("db_name")
        self.save_db_flag = kwargs.get("save_db_flag")
        self.save_excel_flag = kwargs.get("save_excel_flag")
        self.page_num_list = []
        self.request_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
        }
        self.sess = requests.Session()
        self.sess.headers.update(self.request_headers)
        self.logger = logging.getLogger("mainModule.sub.module")

    def send_get_from_search_tag(self, page_num="1"):
        """
        搜索结果对应页面的响应
        :param page_num:
        :return:
        """
        get_url = "https://nj.lianjia.com/ershoufang/pg" + str(page_num) + "rs" + self.search_tag + "/"
        resp = self.sess.get(url=get_url, timeout=10)
        return resp

    def parse_houseid_from_html(self, resp_body):
        """
        抓取对应每个house响应页面的houseid
        :param resp_body:
        :return:
        """
        result = []
        htmlelement = etree.HTML(resp_body)
        # house_tmp = htmlelement.xpath("//html//body//div[@class='content']")
        house_tmp = htmlelement.xpath("//div[@data-houseid]")
        for i in house_tmp:
            house_id = i.attrib.get("data-houseid")
            result.append(house_id)
        self.search_result.extend(result)

    def parse_page_num_from_html(self, resp_body):
        """
        :param resp_body:
        :return: 获取页面搜索结果的总页面数
        """
        htmlelement = etree.HTML(resp_body)
        page_num_tmp = htmlelement.xpath("""//div//div//div//div//div[@class="page-box house-lst-page-box"]""")
        try:
            page_num_str = page_num_tmp[0].attrib.get("page-data")
            page_num = eval(page_num_str).get('totalPage')
        except Exception as e:
            self.logger.error("Error: %s, parse page num failed from html: %s. Please check search tag!" % (e))
            # search_tag无结果
            page_num = 0
        return page_num

    def parse_houseinfo_from_html(self, resp_body, house_id):
        """
        :param resp_body: 响应页面
        :return: 输出一个dict,里面是链家爬取下来的房屋信息
        """
        myparser = etree.HTMLParser(encoding="utf-8")
        htmlelement = etree.HTML(resp_body, parser=myparser)
        title_xpath = """//html//body//div//div//div//div//h1[@class="main"]"""
        house_style_xpath = """//html//body//div//div//div//div//div[@class="mainInfo"]"""
        xiaoqu_xpath = """//html//body//div//div//div//div[@class="communityName"]//a"""
        total_price_xpath = """//html//body//div//div//div//span[@class="total"]"""
        floor_xpath = """//div//div//div//div[@class="content"]//ul//li//span[@class="label"]"""
        tax_xpath = """//div[@class="transaction"]//div[@class="content"]//ul//li//span"""
        try:
            title = htmlelement.xpath(title_xpath)[0].text.encode("utf-8")
            house_style = htmlelement.xpath(house_style_xpath)[0].text.encode("utf-8")
            house_area = htmlelement.xpath(house_style_xpath)[2].text.encode("utf-8").replace("平米", "")
            community_name = htmlelement.xpath(xiaoqu_xpath)[0].text.encode("utf-8")
            total_price = htmlelement.xpath(total_price_xpath)[0].text.encode("utf-8")
            area_price = str(int(float(total_price) / float(house_area) * 10000))
            floor = htmlelement.xpath(floor_xpath)[1].tail.encode("utf-8")
            decoration = htmlelement.xpath(floor_xpath)[8].tail.encode("utf-8")  # 装修
            other_info_1 = htmlelement.xpath(floor_xpath)[9].tail.encode("utf-8")  # 梯户比
            tax_info = htmlelement.xpath(tax_xpath)[9].text.encode("utf-8")  # 税费
            result = {
                "title": title,
                "total_price": total_price,
                "house_style": house_style,
                "house_area": house_area,
                "area_price": area_price,
                "floor": floor,
                "community_name": community_name,
                "decoration": decoration,
                "tax_info": tax_info,
                "other_info_1": other_info_1,
                "timestamp": datetime.datetime.now().strftime("%Y%m%d"),
            }
            if self.save_db_flag:
                self.logger.info("Now saving data from house_id: %s" % (house_id))
                self.save_house_info_to_mgdb(result, house_id)
        except Exception as e:
            self.logger.error("Error: %s , get data failed from house_id: %s" % (e, house_id))
            result = None
        return result

    def save_house_info_to_mgdb(self, result, house_id):
        mg_test = MongoCache(host=self.db_host, port=self.db_port, db_name=self.db_name)
        # 更新house_info表, key "_id" 确保house_info表唯一性
        result["_id"] = house_id
        mg_test.insert(result, collection="house_info")
        # 更新house_daily_price表
        daily_record = {
            "house_id": house_id,
            "price": result.get("total_price"),
            "area_price": result.get("area_price"),
            "time": result.get("timestamp"),
                  }
        res = mg_test.find_one(daily_record, collection="house_daily_price")
        if res:
            # daily info already exists
            pass
        else:
            mg_test.insert(daily_record, collection="house_daily_price")

    def send_get_request_from_houseid(self, houseid):
        get_url = "https://nj.lianjia.com/ershoufang/" + houseid + ".html"
        resp = self.sess.get(url=get_url, timeout=10)
        return resp

    def write_result_to_excel(self):
        """
        输出结果到excel
        :return:
        """
        wb = xlwt.Workbook(encoding="utf-8")
        sheet_title = self.search_tag + "-" + datetime.datetime.now().strftime("%Y%m%d")
        sheet_title = sheet_title
        wb_sheet = wb.add_sheet(sheet_title)
        write_row = 1
        write_col = 0
        wb_sheet.write(0, 0, "houseid")
        wb_sheet.write(0, 1, "标题")
        wb_sheet.write(0, 2, "总价(万)")
        wb_sheet.write(0, 3, "面积(平方米)")
        wb_sheet.write(0, 4, "房型")
        wb_sheet.write(0, 5, "单价(元)")
        wb_sheet.write(0, 6, "税费")
        wb_sheet.write(0, 7, "装修")
        wb_sheet.write(0, 8, "楼层")
        wb_sheet.write(0, 9, "梯户比")
        wb_sheet.write(0, 10, "小区名称")

        for key in self.result:
            value = self.result.get(key)
            wb_sheet.write(write_row, 0, key)
            wb_sheet.write(write_row, 1, value.get("title"))
            wb_sheet.write(write_row, 2, value.get("total_price"))
            wb_sheet.write(write_row, 3, value.get("house_area"))
            wb_sheet.write(write_row, 4, value.get("house_style"))
            wb_sheet.write(write_row, 5, value.get("area_price"))
            wb_sheet.write(write_row, 6, value.get("tax_info"))
            wb_sheet.write(write_row, 7, value.get("decoration"))
            wb_sheet.write(write_row, 8, value.get("floor"))
            wb_sheet.write(write_row, 9, value.get("other_info_1"))
            wb_sheet.write(write_row, 10, value.get("community_name"))
            write_row += 1
        wb.save(self.output_filename)

    '''
    def link_crawl(self):
        """
        单线程爬虫
        :return:
        """
        resp = self.send_get_from_search_tag()
        page_num = self.parse_page_num_from_html(resp.content)
        for i in range(1, page_num + 1):
            resp = self.send_get_from_search_tag(i)
            search_result_tmp = self.parse_houseid_from_html(resp.content)
            self.search_result.extend(search_result_tmp)
        for houseid in self.search_result:
            resp2 = self.send_get_request_from_houseid(houseid)
            result_house_info = self.parse_houseinfo_from_html(resp2.content, houseid)
            if self.save_excel_flag:
                self.result[houseid] = result_house_info
        self.write_result_to_excel()
    '''


    def link_crawl_with_threading(self):
        """
        先获取search_tag的结果,多线程拉去获取page_num的houseid,存到一个list里
        然后获取每个houseid对应页面的houseinformation并存到一个dict里,
        最后根据flag是否输出到excel
        """
        def process_queue():
            while True:
                try:
                    page_num_tmp = self.page_num_list.pop()
                except IndexError:
                    # crawl queue is empty
                    break
                else:
                    resp2 = self.send_get_from_search_tag(page_num_tmp)
                    self.parse_houseid_from_html(resp2.content)
        # 根据搜索条件获取搜索结果页面并获取对应页数
        resp = self.send_get_from_search_tag()
        page_num = self.parse_page_num_from_html(resp.content)
        # 多线程拉取每个页面对应的house_id
        if page_num > 0:
            self.page_num_list = range(1, page_num + 1)
            threads = []
            while threads or self.page_num_list:
                for thread in threads:
                    if not thread.is_alive():
                        threads.remove(thread)
                while len(threads) < self.max_threads and self.page_num_list:
                    # 创建进程
                    thread = threading.Thread(target=process_queue)
                    thread.setDaemon(True)  # 设置为守护线程，完成了之后不管其他的线程有木有完成直接结束
                    thread.start()  # 开始
                    threads.append(thread)
            # 获取所有的house_id成功
            self.logger.critical("Init data success, total result num is %d" % (len(self.search_result)))
            self.threaded_crawler()
            if self.save_excel_flag:
                self.write_result_to_excel()
        else:
            # 未找到结果
            self.logger.error("not found result from search tag %s" %(self.search_tag))


    def threaded_crawler(self):
        """
        获取每个houseid页面的房屋信息
        """
        def process_queue():
            while True:
                try:
                    houseid = self.search_result.pop()
                except IndexError:
                    # crawl queue is empty
                    break
                else:
                    resp2 = self.send_get_request_from_houseid(houseid)
                    result_house_info = self.parse_houseinfo_from_html(resp2.content, houseid)
                    if (result_house_info is not None) and self.save_excel_flag:
                        self.result[houseid] = result_house_info
        threads = []
        while threads or self.search_result:
            for thread in threads:
                if not thread.is_alive():
                    threads.remove(thread)
            while len(threads) < self.max_threads and self.search_result:
                # 创建进程
                thread = threading.Thread(target=process_queue)
                thread.setDaemon(True)  # 设置为守护线程，完成了之后不管其他的线程有木有完成直接结束
                thread.start()  # 开始
                threads.append(thread)


    def format_print_result(self):
        for key in self.result:
            print "houseid -- %s " % key
            for key2 in self.result.get(key):
                print key2 + ":" + self.result.get(key).get(key2)
