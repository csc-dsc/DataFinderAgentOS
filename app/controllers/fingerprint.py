"""
fingerprint.py — 浏览器指纹采集接口
"""

import json
import tornado.web

from app.models.fingerprint import FingerprintRepository


class FingerprintHandler(tornado.web.RequestHandler):
    """接收并存储浏览器指纹。"""

    def check_xsrf_cookie(self):
        """宽松 XSRF — 允许 JSON POST 通过 X-XSRFToken 头或直接放行。"""
        pass

    def post(self):
        try:
            data = json.loads(self.request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.set_status(400)
            return

        fp = data.get("fingerprint", "")
        if not fp:
            self.set_status(400)
            return

        # 尝试获取登录用户名
        username = self.get_secure_cookie("username")
        if username:
            data["userId"] = username.decode("utf-8")

        FingerprintRepository.save(data)
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps({"status": "ok"}))
