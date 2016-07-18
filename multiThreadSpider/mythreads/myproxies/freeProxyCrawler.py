#!/usr/bin/python

from random import choice
from threading import Thread

import requests
from lxml import etree

from ..myheaders.useragent import USER_AGENT

_TARGET_URL = "http://www.xicidaili.com/"
_PROXY_FILE = 'proxies.data'

class RequestError(Exception):
    pass


def proxy_crwaler_handler(url, user_agent, f):
    content = do_request(url, user_agent)
    if content:
        proxies = html_parser(content)
        save_to_file(f, proxies)




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


def save_to_file(f, proxies):
    import json
    with open(f, 'w+') as f:
        for proxy in proxies:
            f.write(json.dumps(proxy) + '\n')


def crawler():
    thread = Thread(target=proxy_crwaler_handler, args=(_TARGET_URL, USER_AGENT, _PROXY_FILE))
    thread.start()
    thread.join()

