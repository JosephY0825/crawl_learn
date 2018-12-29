# -*- coding: utf-8 -*-
import requests
from lxml import etree
import datetime
import xlwt
import time



def send_get_from_search_tag(search_tag, page_num=""):
    if page_num == "":
        get_url = "https://nj.lianjia.com/ershoufang/rs" + search_tag + "/"
    else:
        get_url = "https://nj.lianjia.com/ershoufang/pg" + str(page_num) + "rs" + search_tag + "/"
    request_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
    }
    resp = requests.get(url=get_url, headers=request_headers, timeout=10)
    return resp


def parse_houseid_from_html(resp_body):
    result = []
    htmlelement = etree.HTML(resp_body)
    # house_tmp = htmlelement.xpath("//html//body//div[@class='content']")
    house_tmp = htmlelement.xpath("//div[@data-houseid]")
    for i in house_tmp:
        house_id = i.attrib.get("data-houseid")
        result.append(house_id)
    return result



def parse_page_num_from_html(resp_body):
    result = []
    htmlelement = etree.HTML(resp_body)
    page_num_tmp = htmlelement.xpath("""//div//div//div//div//div[@class="page-box house-lst-page-box"]""")
    page_num_str = page_num_tmp[0].attrib.get("page-data")
    page_num = eval(page_num_str).get('totalPage')
    return page_num



def parse_houseinfo_from_html(resp_body, houseid):
    myparser = etree.HTMLParser(encoding="utf-8")
    htmlelement = etree.HTML(resp_body, parser=myparser)
    title_xpath = """//h3[@data-ulog="housedel_id=%s"]""" % houseid
    price_xpath = """//p//span[@data-mark="price"]"""
    #area_xpath = """//div[@class="similar_data_detail"]//p[@class="red big"]"""
    house_style_xpath = """//div[@class="similar_data_detail"]//p[@class="red big"]"""
    house_tmp_0 = htmlelement.xpath(title_xpath)
    title = house_tmp_0[0].text.strip()
    house_tmp_1 = htmlelement.xpath(price_xpath)
    total_price = house_tmp_1[0].text.strip()
    house_tmp_2 = htmlelement.xpath(house_style_xpath)
    house_style = house_tmp_2[1].text.strip()
    house_area = house_tmp_2[2].text.strip()
    result = {
        "title": title,
        "total_price": total_price,
        "house_style": house_style,
        "house_area": house_area,
        "timestamp": datetime.datetime.now().strftime("%Y%m%d")
    }
    return result



def send_get_request_from_houseid(houseid):
    # get_url = "https://nj.lianjia.com/ershoufang/" + houseid + ".html"
    get_url = "https://m.lianjia.com/nj/ershoufang/" + houseid + ".html"
    request_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
    }
    resp = requests.get(url=get_url, headers=request_headers, timeout=10)
    return resp



def write_result_to_excel(write_dic, output_filename, search_tag):
    wb = xlwt.Workbook(encoding="utf-8")
    sheet_title = search_tag + "-" + datetime.datetime.now().strftime("%Y%m%d")
    sheet_title = sheet_title
    wb_sheet = wb.add_sheet(sheet_title)
    write_row = 1
    write_col = 0
    wb_sheet.write(0, 0, "houseid")
    wb_sheet.write(0, 1, "标题")
    wb_sheet.write(0, 2, "总价")
    wb_sheet.write(0, 3, "面积")
    wb_sheet.write(0, 4, "房型")
    for key in write_dic:
        value = write_dic.get(key)
        wb_sheet.write(write_row, 0, key)
        wb_sheet.write(write_row, 1, value.get("title"))
        wb_sheet.write(write_row, 2, value.get("total_price"))
        wb_sheet.write(write_row, 3, value.get("house_area"))
        wb_sheet.write(write_row, 4, value.get("house_style"))
        write_row += 1
    wb.save(output_filename)


def main():
    start_time = time.time()
    search_tag = "高科荣域"
    output_filename = "1.xls"
    search_result = []
    result = {}
    resp = send_get_from_search_tag(search_tag)
    page_num = parse_page_num_from_html(resp.content)

    for i in range(1, page_num+1):
        resp = send_get_from_search_tag(search_tag, i)
        search_result_tmp = parse_houseid_from_html(resp.content)
        search_result.extend(search_result_tmp)

    for houseid in search_result:
        resp2 = send_get_request_from_houseid(houseid)
        result_houseid = parse_houseinfo_from_html(resp2.content, houseid)
        result[houseid] = result_houseid

    write_result_to_excel(result, output_filename, search_tag)
    finish_time = time.time()
    print "处理完毕,用时%s" % (finish_time - start_time)


def format_print_result(result):
    for key in result:
        print "houseid -- %s " % key
        for key2 in result.get(key):
            print key2 + ":" + result.get(key).get(key2)


if __name__ == '__main__':
    main()
