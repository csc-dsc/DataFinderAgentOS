"""
admin_base.py — 管理后台公共基类

提供管理后台通用的权限校验、导航菜单注入。
"""

import tornado.web
from app.controllers.base import BaseHandler
from app.models.user import UserRepository
from app.models.menu import MenuRepository
from app.models.function import FunctionRepository


class AdminBaseHandler(BaseHandler):
    """管理后台基础 Handler。所有管理页面继承此类。"""

    def has_permission(self, code: str) -> bool:
        if not self.current_user:
            return False
        return code in FunctionRepository.get_user_function_codes(self.current_user)

    def get_nav_menus(self) -> list:
        if not self.current_user:
            return []
        return MenuRepository.get_user_menu_tree(self.current_user)

    def prepare(self):
        super().prepare()
        if not self.current_user:
            self.redirect(self.settings.get("login_url", "/"))
            return

        user = UserRepository.get_user_by_username(self.current_user)
        if not user or user["is_enabled"] == 0:
            self.clear_cookie("username")
            self.redirect(self.settings.get("login_url", "/"))
            return

        role = UserRepository.get_user_role(self.current_user)
        if not role:
            self.set_status(403)
            self.write("""
            <div style="text-align:center;padding:60px 20px;">
                <i class="layui-icon layui-icon-close-fill" style="font-size:60px;color:#FF5722;"></i>
                <h2 style="margin-top:20px;">403 权限不足</h2>
                <p style="color:#999;margin-top:10px;">您没有分配角色，请联系系统管理员。</p>
                <a href="/logout" style="margin-top:20px;display:inline-block;">返回登录</a>
            </div>
            """)
            return

        if role["name"] == "普通用户":
            self.set_status(403)
            self.write("""
            <div style="text-align:center;padding:60px 20px;">
                <i class="layui-icon layui-icon-close-fill" style="font-size:60px;color:#FF5722;"></i>
                <h2 style="margin-top:20px;">403 权限不足</h2>
                <p style="color:#999;margin-top:10px;">您没有权限访问管理后台，请联系系统管理员。</p>
                <a href="/logout" style="margin-top:20px;display:inline-block;">返回登录</a>
            </div>
            """)
            return

        funcs = UserRepository.get_user_functions(self.current_user)
        if not funcs:
            self.set_status(403)
            self.write("""
            <div style="text-align:center;padding:60px 20px;">
                <i class="layui-icon layui-icon-close-fill" style="font-size:60px;color:#FF5722;"></i>
                <h2 style="margin-top:20px;">403 权限不足</h2>
                <p style="color:#999;margin-top:10px;">您的角色没有分配任何功能权限，请联系系统管理员。</p>
                <a href="/logout" style="margin-top:20px;display:inline-block;">返回登录</a>
            </div>
            """)
            return
