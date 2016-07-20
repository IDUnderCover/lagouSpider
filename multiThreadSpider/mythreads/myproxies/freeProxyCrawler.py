#!/usr/bin/python
# -*- coding: utf8 -*-
from random import choice
from threading import Thread

import requests
import time
from lxml import etree

from ..myheaders.useragent import USER_AGENT
from ..db import db_session
from ..db.mymodels import ProxyEntity
from contextlib import contextmanager

_TARGET_URL = "http://www.xicidaili.com/"
_LATENCY_TEST_URL = 'http://www.baidu.com/'
_PROXY_FILE = 'proxies.data'

class RequestError(Exception):
    pass


def proxy_crwaler_handler(url, user_agent):
    content = do_request(url, user_agent)
    if content:
        proxies = html_parser(content)
        save_to_postgresql(proxies)




def do_request(url, user_agent):
    headers = {'User-Agent': choice(user_agent)}
    content = ""
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            content = r.content
    except Exception, e:
        reason = 'encounter an error while requesting %s' % url
        raise RequestError(reason + '\n' + str(e))
    finally:
        return content


def html_parser(content):
    tree = etree.HTML(content)
    trs = tree.xpath("//tr[@class='odd']")
    proxies = []
    for tr in trs:
        proxy = {}

        properties = ['country', 'ip', 'port', 'address', 'anonymous', 'type', 'live', 'verify']
        values = tr.xpath(".//td/text()")
        remain = dict(zip(properties[1:], values))

        proxy['country'] = tr.xpath(".//td/img/@alt")
        proxy = dict(proxy, **remain)
        proxies.append(proxy)

    return proxies


def crawler():
    thread = Thread(target=proxy_crwaler_handler, args=(_TARGET_URL, USER_AGENT))
    thread.start()
    thread.join()


# def save_to_file(f, proxies):
#     import json
#     with open(f, 'w+') as f:
#         for proxy in proxies:
#             f.write(json.dumps(proxy) + '\n')
@contextmanager
def session_scope():
    ses = db_session()
    try:
        yield ses
        ses.commit()
    except:
        ses.rollback()
        raise
    finally:
        ses.close()


def save_to_postgresql(proxies):
    with session_scope() as ses:
        for proxy in proxies:
            ses.add(
                ProxyEntity(**proxy)
            )


def proxy_latency_test():
    with session_scope() as ses:
        #
        # all_proxyies = ses.query(ProxyEntity).filter(ProxyEntity.country == '{Cn}',
        #                                              ProxyEntity.type == 'HTTP',
        #                                              ProxyEntity.verify.like('%分钟前' )).all()
        all_proxyies = ses.query(ProxyEntity).filter(ProxyEntity.country == '{Cn}').all()
        for proxy in all_proxyies:
            host = proxy.ip
            port = proxy.port
            url = "".join(['http://', host, ':', port])
            t1 = time.clock()
            res = requests.get(_LATENCY_TEST_URL, proxies={'HTTP': url}, timeout=(3.05, 6.05))
            t2 = time.clock()
            if res.status_code == 200:
                # print res.content[0:1000]
                lat = t2 - t1
            else:
                lat = -1
            proxy.latency = lat
            print url, t2-t1, res.status_code
            time.sleep(2)


def get_proxy(num):
    p_count = [num]

    def seq_select():
        with session_scope() as ses:
            all_proxies = ses.query(ProxyEntity).filter(ProxyEntity.country == '{Cn}').order_by(ProxyEntity.latency).all()
            length = len(all_proxies)
            index = p_count[0] % length
            ip = all_proxies[index].ip
            port = all_proxies[index].port
        p_count[0] += 1
        return ip, port
    return seq_select