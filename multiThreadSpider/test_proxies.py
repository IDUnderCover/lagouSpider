#!/usr/bin/python
# -*- coding: utf8 -*-
from mythreads.myproxies.freeProxyCrawler import crawler, proxy_latency_test, get_proxy


if __name__ == '__main__':
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
    # proxy_latency_test()
    pro = get_proxy(3)
    for i in range(1,10):
        print pro()