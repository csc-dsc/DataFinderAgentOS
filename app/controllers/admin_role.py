"""
admin_role.py — 角色管理控制器

系统管理员管理角色（新增/编辑/删除），支持双体系权限分配：
- 角色→功能码（role_functions）：后端权限
- 角色→菜单（role_menus）：前端导航
"""

import tornado.web
from app.controllers.admin_base import AdminBaseHandler
from app.models.role import RoleRepository
from app.models.function import FunctionRepository
from app.models.menu import MenuRepository


class RoleListHandler(AdminBaseHandler):
    """角色列表页"""

    @tornado.web.authenticated
    def get(self):
        page = int(self.get_query_argument("page", 1))
        rows, total = RoleRepository.get_all(page=page, page_size=20)
        total_pages = max(1, (total + 20 - 1) // 20)

        self.render(
            "admin/role_list.html",
            title="角色管理 — 瞭望与问数系统",
            username=self.current_user,
            roles=rows,
            page=page,
            total=total,
            total_pages=total_pages,
            nav_menus=self.get_nav_menus(),
        )


class RoleFormHandler(AdminBaseHandler):
    """角色新增/编辑表单页"""

    @tornado.web.authenticated
    def get(self):
        role_id = self.get_query_argument("id", None)
        role = None
        if role_id:
            role = RoleRepository.get_by_id(int(role_id))
            if not role:
                self.write('<script>alert("角色不存在");window.history.back();</script>')
                return
            if role["is_system"] == 1:
                self.write('<script>alert("系统默认角色不可编辑");window.history.back();</script>')
                return

        self.render(
            "admin/role_form.html",
            title="编辑角色" if role else "新增角色",
            username=self.current_user,
            role=role,
            nav_menus=self.get_nav_menus(),
        )

    @tornado.web.authenticated
    def post(self):
        role_id = self.get_body_argument("id", None)
        name = self.get_body_argument("name", "").strip()
        description = self.get_body_argument("description", "").strip()

        if not name:
            self.write('<script>alert("角色名称不能为空");window.history.back();</script>')
            return

        if role_id:
            role_id = int(role_id)
            role = RoleRepository.get_by_id(role_id)
            if role and role["is_system"] == 1:
                self.write('<script>alert("系统默认角色不可编辑");window.history.back();</script>')
                return
            ok = RoleRepository.update(role_id, name, description)
            if ok:
                self.redirect("/admin/role?msg=更新成功")
            else:
                self.write('<script>alert("更新失败，角色名可能重复");window.history.back();</script>')
        else:
            ok = RoleRepository.create(name, description)
            if ok:
                self.redirect("/admin/role?msg=创建成功")
            else:
                self.write('<script>alert("角色名已存在");window.history.back();</script>')


class RoleDeleteHandler(AdminBaseHandler):
    """删除角色"""

    @tornado.web.authenticated
    def post(self):
        role_id = int(self.get_body_argument("id", 0))
        role = RoleRepository.get_by_id(role_id)
        if role and role["is_system"] == 1:
            self.write('<script>alert("系统默认角色不可删除");window.history.back();</script>')
            return
        RoleRepository.delete(role_id)
        self.redirect("/admin/role?msg=已删除")


class RoleFunctionHandler(AdminBaseHandler):
    """角色功能权限分配页"""

    @tornado.web.authenticated
    def get(self):
        role_id = int(self.get_query_argument("id", 0))
        role = RoleRepository.get_by_id(role_id)
        if not role:
            self.redirect("/admin/role")
            return

        funcs = FunctionRepository.get_enabled()
        checked = set(RoleRepository.get_function_ids(role_id))

        self.render(
            "admin/role_functions.html",
            title=f"功能授权 — {role['name']}",
            username=self.current_user,
            role=role,
            functions=funcs,
            checked_func_ids=checked,
            nav_menus=self.get_nav_menus(),
        )

    @tornado.web.authenticated
    def post(self):
        role_id = int(self.get_query_argument("id", 0))
        func_ids = [int(x) for x in self.get_body_arguments("function_ids") if x]
        RoleRepository.set_functions(role_id, func_ids)
        self.redirect(f"/admin/role/functions?id={role_id}&msg=功能权限已更新")


class RoleMenuHandler(AdminBaseHandler):
    """角色菜单权限分配页"""

    @tornado.web.authenticated
    def get(self):
        role_id = int(self.get_query_argument("id", 0))
        role = RoleRepository.get_by_id(role_id)
        if not role:
            self.redirect("/admin/role")
            return

        menus, _ = MenuRepository.get_all(page=1, page_size=100)
        checked = set(RoleRepository.get_menu_ids(role_id))

        self.render(
            "admin/role_menus.html",
            title=f"菜单授权 — {role['name']}",
            username=self.current_user,
            role=role,
            menus=menus,
            checked_menu_ids=checked,
            nav_menus=self.get_nav_menus(),
        )

    @tornado.web.authenticated
    def post(self):
        role_id = int(self.get_query_argument("id", 0))
        menu_ids = [int(x) for x in self.get_body_arguments("menu_ids") if x]
        RoleRepository.set_menus(role_id, menu_ids)
        self.redirect(f"/admin/role/menus?id={role_id}&msg=菜单权限已更新")
