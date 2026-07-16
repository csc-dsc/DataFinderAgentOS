"""数智大屏控制器"""
import json
import tornado.web
from app.controllers.admin_base import AdminBaseHandler
from app.models.data_warehouse import DataWarehouseRepository
from app.models.watch_source import WatchSourceRepository
from app.models.digital_employee import DigitalEmployeeRepository
from app.models.model_engine import ModelEngineRepository
from app.models.user import UserRepository


class DashboardHandler(AdminBaseHandler):

    def get(self):
        user_count = UserRepository.get_user_count()
        warehouse = DataWarehouseRepository.get_all(page_size=1000)
        sources = WatchSourceRepository.get_all()
        employees = DigitalEmployeeRepository.get_all()
        models = ModelEngineRepository.get_all()

        total_data = warehouse["total"]

        # 按来源统计
        source_stats = {}
        for item in warehouse["rows"]:
            src = item["source_name"]
            source_stats[src] = source_stats.get(src, 0) + 1

        # 关键词统计
        keyword_stats = {}
        for item in warehouse["rows"]:
            kw = item["keyword"]
            if kw:
                keyword_stats[kw] = keyword_stats.get(kw, 0) + 1

        # 生成词云数据
        wordcloud_data = [{"name": k, "value": v} for k, v in sorted(keyword_stats.items(), key=lambda x: -x[1])[:30]]

        # 生成图表数据
        chart_data = {
            "source_pie": [{"name": k, "value": v} for k, v in source_stats.items()],
            "keyword_bar": [{"name": k, "value": v} for k, v in sorted(keyword_stats.items(), key=lambda x: -x[1])[:10]],
            "daily_line": [
                {"date": "周一", "value": random.randint(5, 20)},
                {"date": "周二", "value": random.randint(5, 20)},
                {"date": "周三", "value": random.randint(5, 20)},
                {"date": "周四", "value": random.randint(5, 20)},
                {"date": "周五", "value": random.randint(5, 20)},
                {"date": "周六", "value": random.randint(5, 20)},
                {"date": "周日", "value": random.randint(5, 20)},
            ],
        }

        self.render("admin/dashboard.html",
                    title="数智大屏",
                    username=self.current_user,
                    nav_menus=self.get_nav_menus(),
                    user_count=user_count,
                    total_data=total_data,
                    source_count=len(sources),
                    employee_count=len(employees),
                    model_count=len(models),
                    active_source_count=len([s for s in sources if s["status"] == 1]),
                    wordcloud_json=json.dumps(wordcloud_data, ensure_ascii=False),
                    chart_json=json.dumps(chart_data, ensure_ascii=False),
                    recent_items=warehouse["rows"][:10])


import random
