#!/usr/bin/python
#! -*- coding:utf8 -*-

from splinter import Browser

# 还需要添加验证码认证功能



if __name__ == '__main__':
    # create a Browser instance, the default driver is firefox
    browser = Browser('phantomjs')

    for index in range(8,11):
        email_address = 'spider00' + str(index) + '@modelinking.com'
        email_passwd = 'spider00' + str(index)
        lagou_register_url = 'https://passport.lagou.com/register/register.html'
        # visit lagou register url
        browser.visit(lagou_register_url)

        browser.find_by_xpath("//i[@class='icon icon_mail']").click()
        email = browser.find_by_xpath("//input[@placeholder='请输入常用邮箱地址']")
        passwd = browser.find_by_xpath("//input[@placeholder='请输入密码']")[1]
        job = browser.find_by_xpath("//input[@value='找工作']")[1]
        # contract = browser.find_by_xpath("//span[@class='checkbox_icon']")[1]
        submit = browser.find_by_xpath("//input[@class='btn btn_green btn_active btn_block btn_lg']")[1]

        email.fill(email_address)
        passwd.fill(email_passwd)
        print(email_address, email_passwd)
        job.click()
        # contract.click()
        submit.click()
