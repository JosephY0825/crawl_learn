#!/usr/bin/env python
# -*- coding:utf-8 -*-
from Mongocache import MongoCache
import TimeLibrary
import random


def main():
    mg_test = MongoCache(host="127.0.0.1", port=27017, db_name="test_tmp")
    condition = {"house_id": "103103483007"}
    result = mg_test.find(condition, collection="house_daily_price")
    for i in result:
        print i




if __name__ == '__main__':
    main()