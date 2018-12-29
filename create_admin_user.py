#!/usr/bin/env python
# -*- coding:utf-8 -*-
from Mongoqueue import MongoQueue
from Mongocache import MongoCache
import TimeLibrary
import random


def main():
    house_id_list = ["10001", "10002", "10003"]
    mongotest = MongoCache("127.0.0.1", 50000)
    now_time = TimeLibrary.generate_now_date()
    # for house_id in house_id_list:
    house_id = "10001"
    recent_date = TimeLibrary.generate_recent_date()
    day = recent_date[1]

    for house_id in house_id_list:
        house_daily_price = {
            '_id': house_id,
            "price": random.randint(500, 600),
            'date': day,
        }
        print house_daily_price
        # print house_info
        mongotest.insert(house_daily_price, collection="house_info")

    for house_id in house_id_list:
        find_condition = {"_id": house_id}
        res = mongotest.find(find_condition, "house_info")
        for result in res:
            print result



if __name__ == '__main__':
    main()