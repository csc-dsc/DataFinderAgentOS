"""AI 对话 API 控制器"""
import json
import tornado.web
from app.controllers.base import BaseHandler
from app.models.user_conversation import UserConversationRepository
from app.models.model_engine import ModelEngineRepository
from app.models.digital_employee import DigitalEmployeeRepository


class ChatHandler(BaseHandler):

    def get(self):
        username = self.get_current_user()
        if not username:
            self.redirect("/")
            return
        from app.models.user import UserRepository
        user = UserRepository.get_user_by_username(username)
        if not user:
            self.redirect("/")
            return
        conversations = UserConversationRepository.get_by_user(user["id"])
        models = ModelEngineRepository.get_enabled()
        employees = DigitalEmployeeRepository.get_enabled()
        default_model = ModelEngineRepository.get_default()
        self.render("index.html",
                    title="智能瞭望与问数",
                    username=username,
                    conversations=conversations,
                    models=models,
                    employees=employees,
                    default_model=default_model,
                    models_json=json.dumps(models, ensure_ascii=False),
                    employees_json=json.dumps(employees, ensure_ascii=False))

    def post(self):
        username = self.get_current_user()
        if not username:
            self.write({"code": 401, "msg": "未登录"})
            return

        from app.models.user import UserRepository
        user = UserRepository.get_user_by_username(username)
        if not user:
            self.write({"code": 401, "msg": "用户不存在"})
            return

        action = self.get_argument("action", "")

        if action == "chat":
            message = self.get_argument("message", "")
            conv_id = int(self.get_argument("conv_id", 0))
            model_id = int(self.get_argument("model_id", 0))
            employee_id = int(self.get_argument("employee_id", 0))

            if not message:
                self.write({"code": 400, "msg": "消息不能为空"})
                return

            # 获取或创建对话
            if conv_id == 0:
                title = message[:30] + ("..." if len(message) > 30 else "")
                conv_id = UserConversationRepository.create(user["id"], title, model_id, employee_id)

            # 获取历史消息
            conv = UserConversationRepository.get_by_id(conv_id)
            messages = json.loads(conv["messages"]) if conv and conv["messages"] else []

            # 添加用户消息
            messages.append({"role": "user", "content": message})

            # 模拟 AI 回复（实际应调用模型 API）
            model = ModelEngineRepository.get_by_id(model_id) if model_id else ModelEngineRepository.get_default()
            employee = DigitalEmployeeRepository.get_by_id(employee_id) if employee_id else None

            ai_reply = self._generate_reply(message, employee, model)
            messages.append({"role": "assistant", "content": ai_reply})

            # 保存对话
            UserConversationRepository.update_messages(conv_id, messages)

            model_name = model["name"] if model else ""
            employee_name = employee["name"] if employee else ""

            self.write({
                "code": 200,
                "msg": "success",
                "data": {
                    "content": ai_reply,
                    "conv_id": conv_id,
                    "model_name": model_name,
                    "employee_name": employee_name,
                }
            })

        elif action == "get_conversation":
            conv_id = int(self.get_argument("id"))
            conv = UserConversationRepository.get_by_id(conv_id)
            if conv:
                self.write({"code": 200, "data": conv})
            else:
                self.write({"code": 404, "msg": "对话不存在"})

        elif action == "delete_conversation":
            conv_id = int(self.get_argument("id"))
            UserConversationRepository.delete(conv_id)
            self.write({"code": 200, "msg": "删除成功"})

    def _generate_reply(self, message: str, employee=None, model=None) -> str:
        """生成 AI 回复（模拟）"""
        employee_name = employee["name"] if employee else "AI助手"
        model_name = model["name"] if model else "默认模型"

        # 简单的关键词匹配回复
        if "你好" in message or "hello" in message.lower():
            return f"你好！我是{employee_name}，使用 {model_name} 模型。有什么可以帮助你的吗？"
        elif "数据" in message or "查询" in message:
            return f"关于「{message}」的分析：\n\n根据 {model_name} 模型的分析，这是一个很好的问题。数据查询功能可以帮助你从数据仓库中获取相关信息。"
        elif "天气" in message:
            return f"天气查询功能开发中，敬请期待！\n\n目前你可以通过 @天气成都 等方式召唤天气数字员工。"
        else:
            return f"[{employee_name} · {model_name}]\n\n收到你的消息：「{message}」\n\n这是一个模拟回复，实际部署时需要配置真实的 AI 模型 API。"
