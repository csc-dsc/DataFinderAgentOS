"""模型引擎控制器"""
import json
import tornado.web
from app.controllers.admin_base import AdminBaseHandler
from app.models.model_engine import ModelEngineRepository


class ModelEngineHandler(AdminBaseHandler):

    def get(self):
        models = ModelEngineRepository.get_all()
        self.render("admin/model.html",
                    title="模型引擎",
                    username=self.current_user,
                    nav_menus=self.get_nav_menus(),
                    models=models)

    def post(self):
        action = self.get_argument("action", "")
        if action == "add":
            name = self.get_argument("name", "")
            model_name = self.get_argument("model_name", "")
            api_key = self.get_argument("api_key", "")
            api_url = self.get_argument("api_url", "")
            is_default = int(self.get_argument("is_default", 0))
            ModelEngineRepository.create(name, model_name, api_key, api_url, is_default)
            self.redirect("/admin/model?msg=新增成功")
        elif action == "edit":
            model_id = int(self.get_argument("id"))
            name = self.get_argument("name", "")
            model_name = self.get_argument("model_name", "")
            api_key = self.get_argument("api_key", "")
            api_url = self.get_argument("api_url", "")
            is_default = int(self.get_argument("is_default", 0))
            ModelEngineRepository.update(model_id, name, model_name, api_key, api_url, is_default)
            self.redirect("/admin/model?msg=编辑成功")
        elif action == "delete":
            model_id = int(self.get_argument("id"))
            ModelEngineRepository.delete(model_id)
            self.write({"code": 200, "msg": "删除成功"})
        elif action == "toggle":
            model_id = int(self.get_argument("id"))
            ModelEngineRepository.toggle_status(model_id)
            self.write({"code": 200, "msg": "状态切换成功"})
        elif action == "set_default":
            model_id = int(self.get_argument("id"))
            ModelEngineRepository.set_default(model_id)
            self.write({"code": 200, "msg": "设为默认成功"})
