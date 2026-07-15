"""
admin_home.py — 管理后台 Dashboard 控制器

后台首页展示概览数据和统计卡片。
"""

import tornado.web
from app.controllers.admin_base import AdminBaseHandler
from app.models.user import UserRepository
from app.models.role import RoleRepository
from app.models.function import FunctionRepository
from app.models.menu import MenuRepository


class AdminIndexHandler(AdminBaseHandler):
    """管理后台 Dashboard"""

    @tornado.web.authenticated
    def get(self):
        user_count = UserRepository.get_user_count()
        role_count = RoleRepository.get_count()
        func_count = FunctionRepository.get_count()
        menu_count = MenuRepository.get_count()

        self.render(
            "admin/index.html",
            title="管理后台 — 瞭望与问数系统",
            username=self.current_user,
            user_count=user_count,
            role_count=role_count,
            func_count=func_count,
            menu_count=menu_count,
            nav_menus=self.get_nav_menus(),
            is_admin=True,
        )
