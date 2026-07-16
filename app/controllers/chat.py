"""AI 对话 API 控制器"""
import json
import random
import tornado.web
from app.controllers.base import BaseHandler
from app.models.user_conversation import UserConversationRepository
from app.models.model_engine import ModelEngineRepository
from app.models.digital_employee import DigitalEmployeeRepository
from app.models.data_warehouse import DataWarehouseRepository


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

            if conv_id == 0:
                title = message[:30] + ("..." if len(message) > 30 else "")
                conv_id = UserConversationRepository.create(user["id"], title, model_id, employee_id)

            conv = UserConversationRepository.get_by_id(conv_id)
            messages = json.loads(conv["messages"]) if conv and conv["messages"] else []
            messages.append({"role": "user", "content": message})

            model = ModelEngineRepository.get_by_id(model_id) if model_id else ModelEngineRepository.get_default()
            employee = DigitalEmployeeRepository.get_by_id(employee_id) if employee_id else None

            ai_reply = self._generate_reply(message, employee, model)
            messages.append({"role": "assistant", "content": ai_reply})

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

        elif action == "query_data":
            keyword = self.get_argument("keyword", "")
            if not keyword:
                self.write({"code": 400, "msg": "请输入查询关键词"})
                return
            result = DataWarehouseRepository.get_all(search=keyword, page_size=10)
            items = result["rows"]
            if items:
                reply = f"查询到 {len(items)} 条与「{keyword}」相关的数据：\n\n"
                for i, item in enumerate(items[:5], 1):
                    reply += f"{i}. {item['title']}\n   来源：{item['source_name']}\n   摘要：{item['summary'][:80]}...\n\n"
            else:
                reply = f"未找到与「{keyword}」相关的数据。"
            self.write({"code": 200, "data": {"content": reply}})

    def _generate_reply(self, message: str, employee=None, model=None) -> str:
        employee_name = employee["name"] if employee else "AI助手"
        model_name = model["name"] if model else "默认模型"
        emp_avatar = employee["avatar"] if employee else "🤖"

        # 天气数字员工
        if employee and employee["name"] in ["天气助手", "Weather"]:
            city = message.replace("天气", "").replace("查询", "").strip() or "成都"
            weathers = ["晴", "多云", "阴", "小雨", "大雨", "雷阵雨"]
            temp = random.randint(18, 35)
            weather = random.choice(weathers)
            return f"📍 {city}天气预报\n\n🌡 温度：{temp}°C\n☁ 天气：{weather}\n💧 湿度：{random.randint(40, 90)}%\n💨 风力：{random.randint(1, 5)}级\n\n数据来源：智能气象站"

        # 音乐数字员工
        if employee and employee["name"] in ["音乐助手", "Music"]:
            songs = [
                ("稻香", "周杰伦"), ("起风了", "买辣椒也用券"), ("晴天", "周杰伦"),
                ("七里香", "周杰伦"), ("夜曲", "周杰伦"), ("简单爱", "周杰伦"),
                ("青花瓷", "周杰伦"), ("告白气球", "周杰伦"), ("说好不哭", "周杰伦"),
                ("孤勇者", "陈奕迅"), ("十年", "陈奕迅"), ("富士山下", "陈奕迅"),
                ("成都", "赵雷"), ("南方姑娘", "赵雷"), ("理想", "赵雷"),
                ("平凡之路", "朴树"), ("生如夏花", "朴树"), ("那些花儿", "朴树"),
            ]
            song = random.choice(songs)
            return f"🎵 随机推荐\n\n歌曲：《{song[0]}》\n歌手：{song[1]}\n\n正在播放... 点击即可收听"

        # 新闻数字员工
        if employee and employee["name"] in ["新闻助手", "News"]:
            news = [
                ("2024年人工智能产业规模突破5000亿", "科技日报"),
                ("成渝双城经济圈建设取得新突破", "四川日报"),
                ("新能源汽车销量再创新高", "新华社"),
                ("5G商用全面推进，覆盖率达95%", "人民日报"),
                ("量子计算取得重大突破", "科技日报"),
                ("数字货币试点范围进一步扩大", "经济日报"),
                ("智慧城市建设项目在全国推广", "光明日报"),
                ("芯片自主研发取得关键进展", "科技日报"),
            ]
            selected = random.sample(news, 5)
            reply = "📰 今日热点新闻\n\n"
            for i, (title, source) in enumerate(selected, 1):
                reply += f"{i}. {title}\n   来源：{source}\n\n"
            return reply

        # 川哥助手
        if employee and employee["name"] in ["川哥", "ChuanGe"]:
            return f"嘿，兄弟！我是川哥，有啥子问题尽管问！\n\n不管是技术问题、学习困惑还是生活琐事，川哥都能给你摆一摆。\n\n记住，有问题找川哥，没得问题更要找川哥！"

        # 文案写作助手
        if employee and employee["name"] in ["文案写作", "Copywriter"]:
            return f"📝 文案写作助手已就绪\n\n我可以帮你：\n• 撰写营销文案\n• 润色文章内容\n• 翻译中英文本\n• 生成创意标题\n• 优化文字表达\n\n请告诉我你需要什么类型的文案帮助？"

        # 通用关键词匹配
        if "你好" in message or "hello" in message.lower():
            return f"{emp_avatar} 你好！我是{employee_name}，有什么可以帮助你的吗？"

        if "数据" in message or "查询" in message:
            return f"关于「{message}」的数据查询：\n\n{model_name}正在为您分析数据，请稍候...\n\n您也可以点击左侧面板的「数据仓库」查看完整数据。"

        if "天气" in message:
            city = message.replace("天气", "").replace("查询", "").strip() or "成都"
            return f"正在为您查询{city}天气...\n\n请使用 @天气助手 {city}天气 获取详细天气信息。"

        if "音乐" in message or "歌" in message:
            return f"正在为您推荐音乐...\n\n请使用 @音乐助手 获取随机音乐推荐。"

        if "新闻" in message:
            return f"正在为您获取新闻...\n\n请使用 @新闻助手 获取今日热点新闻。"

        return f"{emp_avatar} [{employee_name} · {model_name}]\n\n收到你的消息：「{message}」\n\n这是一个模拟回复，实际部署时需要配置真实的 AI 模型 API。"
