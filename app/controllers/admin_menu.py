"""
admin_menu.py — 菜单管理控制器

菜单独立于功能权限，专用于 UI 导航展示。
支持树形菜单的 CRUD 操作。
"""

import tornado.web
from app.controllers.admin_base import AdminBaseHandler
from app.models.menu import MenuRepository


class MenuListHandler(AdminBaseHandler):
    """菜单列表页"""

    @tornado.web.authenticated
    def get(self):
        page = int(self.get_query_argument("page", 1))
        rows, total = MenuRepository.get_all(page=page, page_size=50)
        total_pages = max(1, (total + 50 - 1) // 50)

        self.render(
            "admin/menu_list.html",
            title="菜单管理 — 瞭望与问数系统",
            username=self.current_user,
            menus=rows,
            page=page,
            total=total,
            total_pages=total_pages,
            nav_menus=self.get_nav_menus(),
        )


class MenuFormHandler(AdminBaseHandler):
    """菜单新增/编辑表单页"""

    @tornado.web.authenticated
    def get(self):
        menu_id = self.get_query_argument("id", None)
        menu = None
        if menu_id:
            menu = MenuRepository.get_by_id(int(menu_id))
            if not menu:
                self.write('<script>alert("菜单不存在");window.history.back();</script>')
                return
        parents = MenuRepository.get_parent_options(exclude_id=int(menu_id) if menu_id else None)

        self.render(
            "admin/menu_form.html",
            title="编辑菜单" if menu else "新增菜单",
            username=self.current_user,
            menu=menu,
            parents=parents,
            nav_menus=self.get_nav_menus(),
        )

    @tornado.web.authenticated
    def post(self):
        menu_id = self.get_body_argument("id", None)
        code = self.get_body_argument("code", "").strip()
        name = self.get_body_argument("name", "").strip()
        path = self.get_body_argument("path", "").strip()
        icon = self.get_body_argument("icon", "").strip()
        sort_order = int(self.get_body_argument("sort_order", 99))
        parent_id_raw = self.get_body_argument("parent_id", "").strip()
        parent_id = int(parent_id_raw) if parent_id_raw else None

        if not code or not name:
            self.write('<script>alert("菜单编码和名称不能为空");window.history.back();</script>')
            return

        if menu_id:
            ok = MenuRepository.update(
                int(menu_id), code=code, name=name, path=path,
                icon=icon, sort_order=sort_order, parent_id=parent_id,
            )
            if ok:
                self.redirect("/admin/menu?msg=更新成功")
            else:
                self.write('<script>alert("更新失败");window.history.back();</script>')
        else:
            MenuRepository.create(code, name, path, icon, sort_order, parent_id)
            self.redirect("/admin/menu?msg=创建成功")


class MenuDeleteHandler(AdminBaseHandler):
    """删除菜单"""

    @tornado.web.authenticated
    def post(self):
        menu_id = int(self.get_body_argument("id", 0))
        MenuRepository.delete(menu_id)
        self.redirect("/admin/menu?msg=已删除")


class MenuToggleHandler(AdminBaseHandler):
    """启用/禁用菜单"""

    @tornado.web.authenticated
    def post(self):
        menu_id = int(self.get_body_argument("id", 0))
        status = MenuRepository.toggle_enabled(menu_id)
        if status == -1:
            self.write('<script>alert("菜单不存在");window.history.back();</script>')
        else:
            self.redirect(f"/admin/menu?msg={'已启用' if status == 1 else '已禁用'}")
