"""
auth.py — 认证相关控制器

处理用户登录、登出逻辑。
登录后根据角色跳转：系统管理员 → 管理后台，普通用户 → 用户前台。
"""

import tornado.web

from app.controllers.base import BaseHandler
from app.models.user import UserRepository


class LoginHandler(BaseHandler):
    """登录处理器"""

    def get(self):
        # 已登录用户直接跳转
        if self.current_user:
            return self._redirect_by_role(self.current_user)
        self.render("login.html", title="瞭望与问数系统 — 用户登录", error=None)

    def post(self):
        # 已登录用户直接跳转
        if self.current_user:
            return self._redirect_by_role(self.current_user)

        username = self.get_body_argument("username", "").strip()
        password = self.get_body_argument("password", "")

        # 参数校验
        if not username or not password:
            return self.render(
                "login.html",
                title="瞭望与问数系统 — 用户登录",
                error="用户名和密码不能为空",
            )

        # 验证用户
        if not UserRepository.verify_user(username, password):
            return self.render(
                "login.html",
                title="瞭望与问数系统 — 用户登录",
                error="用户名或密码错误",
            )

        # 登录成功：设置安全 Cookie 并根据角色跳转
        self.set_secure_cookie("username", username)
        # 注意：set_secure_cookie 后 self.current_user 不会立即反映新值
        # 因为 get_secure_cookie 读取的是当前请求的 Cookie
        self._redirect_by_role(username)

    def _redirect_by_role(self, username: str):
        """根据用户角色跳转到对应页面。"""
        role = UserRepository.get_user_role(username)
        if not role:
            self.redirect("/index")
            return

        # 普通用户只能去前台
        if role["name"] == "普通用户":
            self.redirect("/index")
            return

        # 系统管理员或有功能权限的角色的用户去后台
        funcs = UserRepository.get_user_functions(username)
        if funcs:
            self.redirect("/admin")
        else:
            self.redirect("/index")


class LogoutHandler(BaseHandler):
    """登出处理器"""

    def get(self):
        self.clear_cookie("username")
        self.redirect("/")
