#!/usr/bin/python
# -*- coding: utf8 -*-

import spider
import sys
import multiprocessing


def worker(keyword, num, filename):
    work = spider.LagouSpider(keyword, num, filename)
    work.crawl()



if __name__ == '__main__':
    keywords = 'hadoop,spark,docker,python,java,机器学习,数据挖掘,大数据,前端,数据库'.split(',')
    processings = []
    thread_num = 3
    print("start processings")
    for keyword in keywords:
        process = multiprocessing.Process(target=worker, args=(keyword, thread_num, keyword))
        process.start()
        processings.append(process)

    for process in processings:
        process.join()

    print("processings finished")
