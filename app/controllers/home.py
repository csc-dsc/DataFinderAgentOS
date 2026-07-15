"""
home.py — 前台首页控制器
"""

import tornado.web
from app.controllers.base import BaseHandler


class IndexHandler(BaseHandler):
    """普通用户登录后重定向到对话页面"""

    @tornado.web.authenticated
    def get(self):
        self.redirect("/chat")
