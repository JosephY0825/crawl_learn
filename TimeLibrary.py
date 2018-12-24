#!/usr/bin/env python
# -*- coding:utf-8 -*-
from datetime import datetime, timedelta
import time


def generate_recent_date(recent_days=7):
    recent_day = []
    for i in range(1, recent_days+1):
        recent_time = datetime.now() + timedelta(days=-i)
        recent_time = recent_time.strftime("%Y%m%d")
        recent_day.append(recent_time)
    return recent_day


def generate_now_date(style="%Y-%m-%d"):
    return datetime.now().strftime(style)


def generate_ttl_from_date(format_date, style="%Y-%m-%d"):
    time_array = time.strptime(format_date, style)
    timestamp = int(time.mktime(time_array))
    return timestamp


def generate_timestamp():
    return int(time.time())
