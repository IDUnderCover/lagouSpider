#!/usr/bin/python
# -*- coding: utf-8 -*-

import Queue
import json
import logging
import random
import requests
import threading
import time

from functools import reduce
from ..db import db_session
from ..db.mymodels import Position, ProxyEntity
from ..myheaders.useragent import USER_AGENT

'''
 获取职位 url
 "http://www.lagou.com/jobs/positionAjax.json?px=default&needAddtionalResult=false"
 查询字段
 gj 工作经验   "三年及以下"
 xl 学历       "大专"
 jd 融资阶段   "未融资"
 px 排序       "default"
 city 城市     "上海"
 needAddtionalResult "false"       additional 拼写错误


 表单数据
 first: "true"
 pn: "1"
 kd: "python"
'''
# threading.Thread


class LagouSpider(object):
    '''
        拉勾职位数据爬虫
        login_url: 拉勾登录链接
        position_url: 拉勾ajax请求地址
        headers: HTTP请求头
        records: 爬取的数据记录
        record_lock: 对records加锁
        cookies: cookies 存储
        total_pages: 该关键词记录总页数,默认认每页15条
        page_queue: 需要爬取页数的队列
        threads: 创建的线程数
        dump_thread: 数据写入文件线程
        uid: 登录名
        passwd: 密码
    '''
    login_url = "https://passport.lagou.com/login/login.json"
    position_url = "http://www.lagou.com/jobs/positionAjax.json?px=default&needAddtionalResult=false"
    total_pages = 1
    uid = "lagouspider@163.com"
    passwd = "spiderlagou"


    def __init__(self, keyword=None, num=None, db='postgresql', filename=None):
        '''
        @summary: 开启num个线程爬取 http://www.lagou.com 的 keyword 职位数据

        :param keyword: 关键词
        :param num: 线程数
        :param filename: 输出日志和数据文件名
        :param db: 数据写入地址, 'postgresql' 写入到数据库
                               'file' 写入到文件
        '''
        # threading.Thread.__init__(self)
        self.key_word = keyword or "None"
        self.thread_num = num or 1
        self.db = db
        self.filename = (filename or "lagouSpider") + '_' + str(time.time())
        self.init_logging()
        self.threads = []
        self.dump_thread = None
        self.records = []
        self.headers = LagouSpider.init_headers()
        self.page_queue = Queue.Queue()
        self.record_lock = threading.Lock()

    def dump_methods(self):
        dumps = {
            'postgresql':self.write_data_to_postgresql,
            'file': self.write_data_to_file
        }
        return dumps

    @staticmethod
    def init_headers():
        return {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0",
            "Referer": "http://www.lagou.com/job",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json,text/javascript,*/*;q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip,deflate",
            "Connection": "keep-alive"
        }

    def set_headers(self, **kwargs):
        self.headers = dict(self.headers, **kwargs)

    def get_headers(self, key=None, *args):
        if key is None:
            return (self.headers[key] for key in args)
        else:
            return self.headers[key]

    def init_logging(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
            datefmt='%a, %d %b %Y %H:%M:%S',
            filename=self.filename + '.log',
            filemode='w')

    def login(self):
        try:
            logging.info(
                "尝试以用户 {name} 密码 {passwd} 登录".format(
                    name=self.uid,
                    passwd=self.passwd))
            self.ses = requests.Session()
            self.ses.auth = (self.uid, self.passwd)
            res = self.ses.post(self.login_url, headers=self.headers)
            if res.status_code == 200:
                logging.info("login successfully")
            else:
                logging.warning("login failed")
        except Exception as e:
            logging.error(e.message)

    # def logout(self):
    #     print "尝试登出"
    #     #res = self.ses.get("http://www.lagou.com/frontLogout.do")
    #     #print res.content
    #     res = self.ses.close()
    #     print res

    # def set_user_agent(self, agent_str):
    #     self.headers["User-Agent"] = agent_str
    #
    # def set_content_type(self, type_str):
    #     self.headers["Content-Type"] = type_str

    def cal_pages(self):
        '''
        @summary: 计算页数
        :param key_word: 关键词
        :return:  该关键词对应的页数
        '''
        json_res = "None"
        total_count = 1
        page_size = 1
        try:
            post_data = {"first": True, "pn": 1, "kd": self.key_word}
            res = self.ses.post(
                self.position_url,
                data=post_data,
                headers=self.headers)
            if res.status_code == 200:
                json_res = json.loads(res.content)
                total_count = json_res["content"][
                    "positionResult"]["totalCount"]  # total records
                # number of records of each page
                page_size = json_res["content"]["pageSize"]
                logging.info(
                    "总记录条数为 {counts}, 每页 {size} 条数据".format(
                        counts=total_count, size=page_size))
            else:
                logging.warning(
                    "计算记录条数失败, 返回状态码 {code}, 返回内容: {content}" .format(
                        code=res.status_code, content=res.content))
        except Exception as e:
            logging.error(e.message)
            logging.debug(json_res)
        return total_count // page_size + 1

    def crawl_page(self):
        res = 'None'
        page = 0
        while not self.page_queue.empty():
            try:
                page = self.page_queue.get()
                slp = random.randrange(2, 4)
                logging.info(
                    '{thread} start to crawl page No. {page} and sleep {time}' .format(
                        thread=threading.current_thread(), page=page, time=slp))
                post_data = {"first": True, "pn": page, "kd": self.key_word}
                time.sleep(slp)
                res = self.ses.post(
                    self.position_url,
                    data=post_data,
                    headers=self.headers)
                if res.status_code == 200:
                    json_res = json.loads(res.content)
                    # this_page_size = json_res["content"]["positionResult"]["pageSize"]
                    self.record_lock.acquire()
                    self.records.extend(
                        json_res["content"]["positionResult"]["result"])
                    self.record_lock.release()
                else:
                    logging.warning(
                        "爬取页码 {page} 失败, 返回状态码： {code}, 返回值: {content}" .format(
                            page=page, code=res.status_code, content=res.content))
            except Exception as e:
                logging.error(e.message)
                logging.warning(
                    "爬取页码 {page} 失败, 返回状态码： {code}, 返回值: {content}" .format(
                        page=page, code=res.status_code, content=res.content))
                logging.info(
                    'return the page No.{page} into queue'.format(
                        page=page))
                self.page_queue.put(page)
                if self.record_lock.locked():
                    self.record_lock.release()

    def crawl(self):
        '''
        @summary: 启动 num 个threads 抓取数据 一个dump线程循环导出数据
        :return:
        '''
        logging.info("start to crwal {keyword} ".format(keyword=self.key_word))
        start = time.ctime()
        self.login()
        self.total_pages = self.cal_pages()
        # init queue
        for page in range(self.total_pages):
            self.page_queue.put(page + 1)

        for i in range(self.thread_num):
            self.threads.append(threading.Thread(target=self.crawl_page))

        for i in range(self.thread_num):
            self.threads[i].start()

        self.dump_thread = threading.Thread(target=self.dump_data)
        self.dump_thread.start()
        for i in range(self.thread_num):
            self.threads[i].join()
        self.dump_thread.join()

        end = time.ctime()
        logging.info(
            "spider start at {start} and finished at {end}".format(
                start=start, end=end))

    def all_threads_alive(self):
        status = [thread.is_alive() for thread in self.threads]
        return reduce(lambda x, y: x and y, status)

    def is_thread_alive(self):
        status = [thread.is_alive() for thread in self.threads]
        return reduce(lambda x, y: x or y, status)

    def all_threads_dead(self):
        status = [thread.is_alive() == False for thread in self.threads]
        return reduce(lambda x, y: x and y, status)

    def dump_data(self):
        '''
        @summary: 将内存中数据写出
        :return:
        '''
        file = self.filename + '.data'
        sleep_time = self.total_pages // self.thread_num + 1
        logging.info("dumping thread is started, target file is {file} "
                     "sleep time is {slp}".format(file=file, slp=sleep_time))
        self.dump_with_method(self.dump_methods()[self.db])

        logging.info("dumping data finished")

    def dump_with_method(self, dump_method):
        sleep_time = self.total_pages // self.thread_num + 1
        # 在还有抓取线程存活的情况下,缓存记录条数大于100条时dump,并睡眠相应的秒数
        while not self.all_threads_dead():
            if len(self.records) >= 1000:
                dump_method()
            time.sleep(sleep_time)
        # 当所有抓取线程退出后, dump 所有内存中数据
        dump_method()


    def write_data_to_postgresql(self):
        logging.info("writing data into postgresql")
        self.record_lock.acquire()
        ses = db_session()
        try:
            for record in self.records:
                ses.add(
                    Position(
                        keyword=self.key_word,
                        time=time.time(),
                        doc=record
                    )
                )
            ses.commit()
            self.records = []
        except Exception, e:
            logging.error(str(e))
            ses.rollback()
        finally:
            ses.close()
        self.record_lock.release()
        logging.info("writing finished")

    def write_data_to_file(self):
        """
        @summary: 获取records锁,将所有记录写入文件,释放锁
        :return:
        """
        logging.info("writing data into file")
        with open(self.filename + '.data', "w+") as f:
            self.record_lock.acquire()
            for record in self.records:
                f.write(json.dumps(record) + '\n')
            self.records = []
            self.record_lock.release()
        logging.info("writing finished")

if __name__ == "__main__":
    random.seed(time.time())
    index = random.randint(0, len(USER_AGENT) - 1)

    spider = LagouSpider("java", 3)

    spider.crawl()
