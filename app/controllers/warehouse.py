"""数据仓库控制器"""
import json
import tornado.web
from app.controllers.admin_base import AdminBaseHandler
from app.models.data_warehouse import DataWarehouseRepository


class WarehouseHandler(AdminBaseHandler):

    def get(self):
        page = int(self.get_query_argument("page", 1))
        keyword = self.get_query_argument("keyword", "")
        source_name = self.get_query_argument("source_name", "")
        result = DataWarehouseRepository.get_all(page=page, search=keyword, source_name=source_name)
        source_names = DataWarehouseRepository.get_source_names()
        self.render("admin/warehouse.html",
                    title="数据仓库",
                    username=self.current_user,
                    nav_menus=self.get_nav_menus(),
                    items=result["rows"],
                    total=result["total"],
                    page=page,
                    page_size=20,
                    keyword=keyword,
                    source_name=source_name,
                    source_names=source_names,
                    items_json=json.dumps(result["rows"], ensure_ascii=False))

    def post(self):
        action = self.get_argument("action", "")
        if action == "delete":
            wid = int(self.get_argument("id"))
            DataWarehouseRepository.delete(wid)
            self.write({"code": 200, "msg": "删除成功"})
        elif action == "batch_delete":
            ids = [int(i) for i in self.get_argument("ids", "").split(",") if i]
            DataWarehouseRepository.delete_batch(ids)
            self.write({"code": 200, "msg": f"批量删除 {len(ids)} 条成功"})
        elif action == "deep_collect":
            wid = int(self.get_argument("id"))
            item = DataWarehouseRepository.get_by_id(wid)
            if item:
                DataWarehouseRepository.mark_deep_collected(wid, {"content": "深度采集内容示例"})
                self.write({"code": 200, "msg": "深度采集完成", "data": {"content": "深度采集内容示例"}})
            else:
                self.write({"code": 400, "msg": "数据不存在"})
        else:
            self.write({"code": 400, "msg": "未知操作"})
