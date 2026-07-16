"""
main.py — 智能耗望与智能问数系统 (DataFinderAgentOS) v0.3 主入口

基于 Tornado 异步 Web 框架 + SQLite + PBKDF2-SHA256 + 双体系 RBAC。
"""

import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer

from app.controllers.auth import LoginHandler, LogoutHandler
from app.controllers.home import IndexHandler
from app.controllers.chat import ChatHandler
from app.controllers.admin_home import AdminIndexHandler
from app.controllers.admin_user import (
    UserListHandler, UserFormHandler, UserDeleteHandler, UserToggleHandler,
)
from app.controllers.admin_role import (
    RoleListHandler, RoleFormHandler, RoleDeleteHandler,
    RoleFunctionHandler, RoleMenuHandler,
)
from app.controllers.admin_function import (
    FunctionListHandler, FunctionFormHandler, FunctionDeleteHandler, FunctionToggleHandler,
)
from app.controllers.admin_menu import (
    MenuListHandler, MenuFormHandler, MenuDeleteHandler, MenuToggleHandler,
)
from app.controllers.fingerprint import FingerprintHandler
from app.controllers.warehouse import WarehouseHandler
from app.controllers.watch import WatchHandler
from app.controllers.watch_source import WatchSourceHandler
from app.controllers.model_engine import ModelEngineHandler
from app.controllers.digital_employee import DigitalEmployeeHandler
from app.controllers.dashboard import DashboardHandler
from app.models.db import init_db, seed_default_data


def make_app() -> tornado.web.Application:
    return tornado.web.Application(
        [
            # 前台路由
            (r"/", LoginHandler),
            (r"/logout", LogoutHandler),
            (r"/index", IndexHandler),
            (r"/chat", ChatHandler),

            # Dashboard
            (r"/admin", AdminIndexHandler),

            # 用户管理
            (r"/admin/user", UserListHandler),
            (r"/admin/user/add", UserFormHandler),
            (r"/admin/user/edit", UserFormHandler),
            (r"/admin/user/delete", UserDeleteHandler),
            (r"/admin/user/toggle", UserToggleHandler),

            # 角色管理
            (r"/admin/role", RoleListHandler),
            (r"/admin/role/add", RoleFormHandler),
            (r"/admin/role/edit", RoleFormHandler),
            (r"/admin/role/delete", RoleDeleteHandler),
            (r"/admin/role/functions", RoleFunctionHandler),
            (r"/admin/role/menus", RoleMenuHandler),

            # 功能权限管理
            (r"/admin/function", FunctionListHandler),
            (r"/admin/function/add", FunctionFormHandler),
            (r"/admin/function/edit", FunctionFormHandler),
            (r"/admin/function/delete", FunctionDeleteHandler),
            (r"/admin/function/toggle", FunctionToggleHandler),

            # 菜单管理
            (r"/admin/menu", MenuListHandler),
            (r"/admin/menu/add", MenuFormHandler),
            (r"/admin/menu/edit", MenuFormHandler),
            (r"/admin/menu/delete", MenuDeleteHandler),
            (r"/admin/menu/toggle", MenuToggleHandler),

            # 数据仓库
            (r"/admin/warehouse", WarehouseHandler),

            # 瞭望管理
            (r"/admin/watch", WatchHandler),

            # 瞭源管理
            (r"/admin/watch-source", WatchSourceHandler),

            # 模型引擎
            (r"/admin/model", ModelEngineHandler),

            # 数字员工
            (r"/admin/employee", DigitalEmployeeHandler),

            # 数智大屏
            (r"/admin/dashboard", DashboardHandler),

            # 浏览器指纹
            (r"/fp", FingerprintHandler),
        ],
        template_path="app/templates",
        static_path="app/static",
        cookie_secret="datafinderagentos-token-2026",
        login_url="/",
        xsrf_cookies=True,
        debug=True,
    )


if __name__ == "__main__":
    init_db()
    seed_default_data()
    app = make_app()
    server = HTTPServer(app)
    server.listen(10010)
    print("=" * 50)
    print("  智能耗望与智能问数系统 (DataFinderAgentOS) v0.3")
    print("  Server Started: http://localhost:10010/")
    print("=" * 50)
    tornado.ioloop.IOLoop.current().start()
