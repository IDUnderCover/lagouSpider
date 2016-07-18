#!/usr/bin/python
# -*- coding: utf8 -*-

import multiprocessing

from mythreads.myspider import spider


def worker(keyword, num, db, filename):
    work = spider.LagouSpider(keyword, num, db, filename)
    work.crawl()



if __name__ == '__main__':
    #keywords = 'hadoop,spark,docker,python,java,机器学习,数据挖掘,大数据,前端,数据库'.split(',')
    keywords = ['python']
    processings = []
    thread_num = 3
    print("start processings")
    for keyword in keywords:
        process = multiprocessing.Process(target=worker, args=(keyword, thread_num, 'postgresql', keyword))
        process.start()
        processings.append(process)

    for process in processings:
        process.join()

    print("processings finished")
