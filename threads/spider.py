#!/usr/bin/python
#! -*- coding: utf-8 -*-

import requests
import random
import time
import json
import threading
import Queue
from useragent import *
test_user = { "id": "lagouspider@163.com", "passwd":"spiderlagou"}

# 获取职位 url
# "http://www.lagou.com/jobs/positionAjax.json?px=default&needAddtionalResult=false"
# 查询字段
# gj 工作经验   "三年及以下"
# xl 学历       "大专"
# jd 融资阶段   "未融资"
# px 排序       "default"
# city 城市     "上海"
# needAddtionalResult "false"       additional 拼写错误 


# 表单数据
# first: "true"
# pn: "1"
# kd: "python"

class Spider():
    
    _login_url = "https://passport.lagou.com/login/login.json"
    _position_url = "http://www.lagou.com/jobs/positionAjax.json?px=default&needAddtionalResult=false"
    headers = { "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0",
                        "Referer": "http://www.lagou.com/job",
                        "X-Requested-With": "XMLHttpRequest",
                        "Accept": "application/json,text/javascript,*/*;q=0.01",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Accept-Encoding": "gzip,deflate",
                        "Connection": "keep-alive" } 

    records = []
    ses = None
    cookies = ""
    record_lock = threading.Lock()
    _total_pages = 1
    page_q= Queue.Queue()
    threads = []
    def __init__(self, uid=None, passwd=None, num=None ):
        self.uid = uid or ""
        self.passwd = passwd or ""
        self.thread_num = num or 1

    def login(self):
        try:
            print "尝试登录"
            self.ses= requests.Session()
            self.ses.auth = (self.uid, self.passwd)
            res = self.ses.post(self._login_url, headers=self.headers)
            print res.content
        except Exception as e:
            print e.__str__

    def logout(self):
        print "尝试登出"
        #res = self.ses.get("http://www.lagou.com/frontLogout.do")
        #print res.content
        res = self.ses.close()
        print res

    def set_user_agent(self, agent_str):
        self.headers["User-Agent"] = agent_str
        
    def set_content_type(self, type_str):
        self.headers["Content-Type"] = type_str

    def cal_pages(self, key_word):
        json_res = "None"
        try:
            post_data = {"first": True, "pn":1, "kd": key_word}
            res = self.ses.post(self._position_url, data=post_data, headers=self.headers) 
            #print res.content
            json_res = json.loads(res.content)
            total_count = json_res["content"]["positionResult"]["totalCount"] # total records
            page_size = json_res["content"]["pageSize"] # number of records of each page 
        except Exception as e:
            print(e)
            print(json_res)
        return total_count // page_size + 1 
            
    def crawl_page(self, key_word):
        json_res = 'None'
        page = 0
        while not self.page_q.empty():
            try:
                page = self.page_q.get()
                slp = random.randrange(2,4)
                print '%s start to crawl page No. %d and sleep %d' % (threading.current_thread(),page, slp)
                post_data = {"first": True, "pn":page, "kd": key_word}
                time.sleep(slp)
                res = self.ses.post(self._position_url, data=post_data, headers=self.headers) 
                json_res = json.loads(res.content)
                # this_page_size = json_res["content"]["positionResult"]["pageSize"]
                self.record_lock.acquire() 
                self.records.extend(json_res["content"]["positionResult"]["result"])
                self.record_lock.release() 
            except Exception as e:
                print(e)
                print(json_res)
                print 'put the page No. %d into queue' % page
                self.page_q.put(page)
                if self.record_lock.locked():
                    print 'unlock the lock'
                    self.record_lock.release()
   
   
    def crawl(self, key_word):
        print "start to crwal %s \n" % key_word
        # get page numbers

        print "calculating page number ..."
        self._total_pages =  self.cal_pages(key_word)
        
        print "page number is %d" % self._total_pages
       
       
        print "start to init the queue" 
        # init queue
        for page in range(self._total_pages):
            self.page_q.put( page + 1 )

        print "init queue finished"

        print "start to generate threads" 
        for i in range(self.thread_num):
            self.threads.append(threading.Thread(target=self.crawl_page, args=(key_word,)))
        print "finish threads generation"
       
        print "threads started" 
        for i in range(self.thread_num):
            self.threads[i].start()

        print "threads join"
        for i in range(self.thread_num):
            self.threads[i].join()

        print "crawl finished"

    def dump_data(self,file_name):
        print "start to dump data"
        with open(file_name, "a+") as f:
            for record in self.records:
                f.write(json.dumps(record) + '\n')
        print "dump data finished"

if __name__ == "__main__":
    random.seed(time.time())
    index = random.randint(0,len(USER_AGENT)-1)
    
    spider = Spider(test_user["id"],test_user["passwd"],3) 
    spider.set_user_agent(USER_AGENT[2])
    spider.login()
    spider.crawl("hadoop")
    spider.dump_data("hadoop_records")
