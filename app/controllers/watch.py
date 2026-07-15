"""瞭望管理控制器"""
import json
import tornado.web
import tornado.httpclient
from app.controllers.admin_base import AdminBaseHandler
from app.models.watch_source import WatchSourceRepository
from app.models.data_warehouse import DataWarehouseRepository


class WatchHandler(AdminBaseHandler):

    def get(self):
        sources = WatchSourceRepository.get_enabled()
        self.render("admin/watch.html",
                    title="瞭望管理",
                    username=self.current_user,
                    nav_menus=self.get_nav_menus(),
                    sources=sources)

    def post(self):
        keyword = self.get_argument("keyword", "")
        source_ids = self.get_argument("source_ids", "")
        page = int(self.get_argument("page", 0))

        if not keyword:
            self.write({"code": 400, "msg": "请输入关键词"})
            return

        results = []
        errors = []

        for sid in source_ids.split(","):
            if not sid:
                continue
            try:
                req = WatchSourceRepository.build_request(int(sid), keyword, page)
                if req:
                    results.append({
                        "title": f"{keyword} - {req['source_name']} 结果",
                        "url": req["url"],
                        "summary": f"来自 {req['source_name']} 的搜索结果",
                        "source_name": req["source_name"],
                        "source_id": int(sid),
                    })
            except Exception as e:
                errors.append(str(e))

        self.write({"code": 0, "msg": "采集完成", "data": results, "errors": errors})
