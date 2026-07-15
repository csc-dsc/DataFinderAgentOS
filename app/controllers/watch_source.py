"""瞭源管理控制器"""
import json
import tornado.web
from app.controllers.admin_base import AdminBaseHandler
from app.models.watch_source import WatchSourceRepository


class WatchSourceHandler(AdminBaseHandler):

    def get(self):
        action = self.get_query_argument("action", "list")
        if action == "list":
            sources = WatchSourceRepository.get_all()
            self.render("admin/watch_source.html",
                        title="瞭源管理",
                        username=self.current_user,
                        nav_menus=self.get_nav_menus(),
                        sources=sources)
        else:
            self.render("admin/watch_source.html",
                        title="新增瞭源",
                        username=self.current_user,
                        nav_menus=self.get_nav_menus(),
                        source=None)

    def post(self):
        action = self.get_argument("action", "")
        if action == "add":
            name = self.get_argument("name", "")
            description = self.get_argument("description", "")
            base_url = self.get_argument("base_url", "")
            method = self.get_argument("method", "GET")
            headers = self.get_argument("headers", "{}")
            params_template = self.get_argument("params_template", "")
            WatchSourceRepository.create(name, description, base_url, method, headers, params_template)
            self.redirect("/admin/watch-source?msg=新增成功")
        elif action == "edit":
            source_id = int(self.get_argument("id"))
            name = self.get_argument("name", "")
            description = self.get_argument("description", "")
            base_url = self.get_argument("base_url", "")
            method = self.get_argument("method", "GET")
            headers = self.get_argument("headers", "{}")
            params_template = self.get_argument("params_template", "")
            WatchSourceRepository.update(source_id, name, description, base_url, method, headers, params_template)
            self.redirect("/admin/watch-source?msg=编辑成功")
        elif action == "delete":
            source_id = int(self.get_argument("id"))
            WatchSourceRepository.delete(source_id)
            self.write({"code": 200, "msg": "删除成功"})
        elif action == "toggle":
            source_id = int(self.get_argument("id"))
            WatchSourceRepository.toggle_status(source_id)
            self.write({"code": 200, "msg": "状态切换成功"})
