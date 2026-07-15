"""数字员工控制器"""
import json
import tornado.web
from app.controllers.admin_base import AdminBaseHandler
from app.models.digital_employee import DigitalEmployeeRepository
from app.models.model_engine import ModelEngineRepository


class DigitalEmployeeHandler(AdminBaseHandler):

    def get(self):
        employees = DigitalEmployeeRepository.get_all()
        models = ModelEngineRepository.get_enabled()
        self.render("admin/employee.html",
                    title="数字员工",
                    username=self.current_user,
                    nav_menus=self.get_nav_menus(),
                    employees=employees,
                    models=models)

    def post(self):
        action = self.get_argument("action", "")
        if action == "add":
            name = self.get_argument("name", "")
            description = self.get_argument("description", "")
            avatar = self.get_argument("avatar", "🤖")
            system_prompt = self.get_argument("system_prompt", "")
            model_id = int(self.get_argument("model_id", 0))
            DigitalEmployeeRepository.create(name, description, avatar, system_prompt, model_id)
            self.redirect("/admin/employee?msg=新增成功")
        elif action == "edit":
            emp_id = int(self.get_argument("id"))
            name = self.get_argument("name", "")
            description = self.get_argument("description", "")
            avatar = self.get_argument("avatar", "🤖")
            system_prompt = self.get_argument("system_prompt", "")
            model_id = int(self.get_argument("model_id", 0))
            DigitalEmployeeRepository.update(emp_id, name, description, avatar, system_prompt, model_id)
            self.redirect("/admin/employee?msg=编辑成功")
        elif action == "delete":
            emp_id = int(self.get_argument("id"))
            DigitalEmployeeRepository.delete(emp_id)
            self.write({"code": 200, "msg": "删除成功"})
        elif action == "toggle":
            emp_id = int(self.get_argument("id"))
            DigitalEmployeeRepository.toggle_status(emp_id)
            self.write({"code": 200, "msg": "状态切换成功"})
