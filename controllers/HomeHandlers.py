#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tornado.web
import requests, json
from common.base import Config
from urllib.parse import unquote
import tornado.ioloop
import traceback
from concurrent.futures import ThreadPoolExecutor
from functools import partial

# 多线程执行
EXECUTOR = ThreadPoolExecutor(max_workers=10)


class BaseController(tornado.web.RequestHandler):
    def render(self, tpl, **render_data):
        if not tpl.endswith('html'):
            tpl = "{}.html".format(tpl)
        super(BaseController, self).render(tpl, **render_data)


class My404(BaseController):
    def get(self):
        self.render('404')


def write_error(self, stat, **kw):
    # self.write('访问url不存在!')
    self.render('404.html')


# 数据服务基类,其他服务均继承自此类
# 封装子接口公用的方法
class BaseHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def asynchronous_get(self, default=None):
        """异步请求，子类在get方法中调用此方法，然后实现_get(self)方法
        """

        def callback(future):
            ex = future.exception()
            if ex is None:
                self.write_result(future.result())
            self.finish()

        return_future = EXECUTOR.submit(self.nomalization_get)
        return_future.add_done_callback(
            lambda future: tornado.ioloop.IOLoop.instance().add_callback(
                partial(callback, future)))

    def nomalization_get(self):
        return self._get()

    @tornado.web.asynchronous
    def asynchronous_post(self, default=None):
        """异步请求，子类在get方法中调用此方法，然后实现_get(self)方法
        """

        def callback(future):
            ex = future.exception()
            if ex is None:
                self.write_result(future.result())
            self.finish()

        return_future = EXECUTOR.submit(self.nomalization_post())
        return_future.add_done_callback(
            lambda future: tornado.ioloop.IOLoop.instance().add_callback(
                partial(callback, future)))

    def nomalization_post(self):
        return self._post()

    def get_argument(self, name, default='', **kwargs):
        value = super(BaseHandler, self).get_argument(name, default)
        return value

    # write result to reaponse
    def write_result(self, result):
        self.write(result)


    # 备注：钩子函数不能像django一样遇到错误终止--需改进
    def initialize(self):
        pass
