# -*- coding: utf-8 -*-
import requests
from lxml import etree
import datetime
import xlwt
import threading


class LianjiaCrawl(object):
    def __init__(self, search_tag, output_filename, max_threads=10, test_flag=False):
        self.search_tag = search_tag
        self.output_filename = output_filename
        self.search_result = []
        self.result = {}
        self.max_threads = max_threads
        self.test_flag = test_flag
        self.page_num_list = []


    def send_get_from_search_tag(self, page_num=""):
        get_url = "https://nj.lianjia.com/ershoufang/pg" + str(page_num) + "rs" + self.search_tag + "/"
        request_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
        }
        resp = requests.get(url=get_url, headers=request_headers, timeout=10)
        return resp


    def parse_houseid_from_html(self, resp_body):
        result = []
        htmlelement = etree.HTML(resp_body)
        # house_tmp = htmlelement.xpath("//html//body//div[@class='content']")
        house_tmp = htmlelement.xpath("//div[@data-houseid]")
        for i in house_tmp:
            house_id = i.attrib.get("data-houseid")
            result.append(house_id)
        self.search_result.extend(result)


    def parse_page_num_from_html(self, resp_body):
        htmlelement = etree.HTML(resp_body)
        page_num_tmp = htmlelement.xpath("""//div//div//div//div//div[@class="page-box house-lst-page-box"]""")
        try:
            page_num_str = page_num_tmp[0].attrib.get("page-data")
            page_num = eval(page_num_str).get('totalPage')
        except IndexError:
            page_num = ""
        return page_num


    def parse_houseinfo_from_html(self, resp_body, houseid):
        myparser = etree.HTMLParser(encoding="utf-8")
        htmlelement = etree.HTML(resp_body, parser=myparser)
        title_xpath = """//html//body//div//div//div//div//h1[@class="main"]"""
        house_style_xpath = """//html//body//div//div//div//div//div[@class="mainInfo"]"""
        xiaoqu_xpath = """//html//body//div//div//div//div[@class="communityName"]//a"""
        total_price_xpath = """//html//body//div//div//div//span[@class="total"]"""
        floor_xpath = """//div//div//div//div[@class="content"]//ul//li//span[@class="label"]"""
        tax_xpath = """//div[@class="transaction"]//div[@class="content"]//ul//li//span"""
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
        return result


    def send_get_request_from_houseid(self, houseid):
        get_url = "https://nj.lianjia.com/ershoufang/" + houseid + ".html"
        # get_url = "https://m.lianjia.com/nj/ershoufang/" + houseid + ".html"
        request_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
        }
        resp = requests.get(url=get_url, headers=request_headers, timeout=10)
        return resp


    def write_result_to_excel(self):
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


    def link_crawl(self):
        resp = self.send_get_from_search_tag()
        page_num = self.parse_page_num_from_html(resp.content)
        for i in range(1, page_num + 1):
            resp = self.send_get_from_search_tag(i)
            search_result_tmp = self.parse_houseid_from_html(resp.content)
            self.search_result.extend(search_result_tmp)
        if self.test_flag:
            houseid = self.search_result[0]
            resp2 = self.send_get_request_from_houseid(houseid)
            result_house_info = self.parse_houseinfo_from_html(resp2.content, houseid)
            self.result[houseid] = result_house_info
        else:
            for houseid in self.search_result:
                resp2 = self.send_get_request_from_houseid(houseid)
                result_house_info = self.parse_houseinfo_from_html(resp2.content, houseid)
                self.result[houseid] = result_house_info
        self.write_result_to_excel()


    def link_crawl_with_threading(self):
        """
        resp = self.send_get_from_search_tag()
        page_num = self.parse_page_num_from_html(resp.content)
        for i in range(1, page_num + 1):
            resp = self.send_get_from_search_tag(i)
            self.parse_houseid_from_html(resp.content)
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
        resp = self.send_get_from_search_tag(1)
        page_num = self.parse_page_num_from_html(resp.content)
        if page_num != "":
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
            print "初始化数据成功,现在开始爬取数据"
            self.threaded_crawler()
            self.write_result_to_excel()
        else:
            print "未找到结果"


    def threaded_crawler(self):
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
