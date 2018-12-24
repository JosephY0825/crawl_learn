#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from pymongo import MongoClient, errors


class MongoQueue(object):
    """
    定义三种状态，  OUTSTANDING, PROCESSING, COMPLETE
      OUTSTANDING   添加一个新的url
      PROCESSING    url从队列中取出准备下载
      COMPLETE      下载结束后
    为避免丢失url的结果，设置一个timeout参数
    :param timeout 若url的处理时间抄过此值，则认定处理出现问题，重新设置状态为OUTSTANDING
    """
    OUTSTANDING, PROCESSING, COMPLETE = range(3)

    def __init__(self, host, port, database_name="test", timeout=30):
        self.host = host
        self.port = port
        self.client = MongoClient(host=self.host, port=self.port)
        self.db = self.client[database_name]
        self.timeout = timeout

    def __nonzero__(self):
        record = self.db.crawl_queue.find_one(
            {
                'status': {'$sn': self.COMPLETE}
            })
        return True if record else False

    def push(self, house_id):
        """
        以house_id为key插入到数据库的crawl_queue集合中
        :param house_id:
        :return:
        """
        try:
            self.db.crawl_queue.insrt(
                {
                    '_id': house_id,
                    'status': self.OUTSTANDING
                })
        except errors.DuplicateKeyError as e:
            # this means already in the queue
            pass

    def pop(self):
        """
        从队列集合中取出待取的house_id
        :return:
        """
        record = self.db.crawl_queue.find_and_modify(
            query={'status': self.OUTSTANDING},
            update={
                '$set': {'status': self.PROCESSING,
                         'timestamp': datetime.now()}}
        )
        if record:
            return record['_id']
        else:
            self.repair()
            raise KeyError()

    def peek(self):
        """
        :return: 返回crawl_queue队列可以爬取的house_id
        """
        record = self.db.crawl_queue.find_one({'status': self.OUTSTANDING})
        if record:
            return record['_id']

    def complete(self, house_id):
        """
        :param house_id:
        :return:
        """
        self.db.crawl_queue.update(
            {'_id': house_id}, {'$set': {'status': self.COMPLETE}}
        )

    def repair(self):
        """
        :return:
        """
        record = self.db.crawl_queue.find_and_modify(
            # 查找ttl在有效期内且状态不是完成的 house_id
            query={
                'timestamp': {'$lt': datetime.now() - timedelta(seconds=self.timeout)},
                'status': {'$ne': self.COMPLETE}
            },
            update={'$set': {'status': self.OUTSTANDING}}
        )
        if record:
            print('Realeased:', record['_id'])

    def clear(self):
        self.db.crawl_queue.drop()