# Author: Q
# Date:   2023-4-8
# Desc:   后台管理蓝图

from sanic import Blueprint
from .index import *
from .user import *
from .system import *
from .role import *

admin_bp = Blueprint("admin", url_prefix="/admin")

# 注册蓝图路由
# 首页
admin_bp.add_route(AdminIndexView.as_view(), "/index", name="index")
admin_bp.add_route(AdminIndexMenuView.as_view(), "/index/menu", name="index_menu")

# 用户
admin_bp.add_route(UserMenuView.as_view(), "/user/menu", name="user_menu")
admin_bp.add_route(UserTableView.as_view(), "/user/table", name="user_table")
admin_bp.add_route(UserAddView.as_view(), "/user/add", name="user_add")
admin_bp.add_route(UserDelView.as_view(), "/user/del", name="user_del")
admin_bp.add_route(UserModifyView.as_view(), "/user/modify", name="user_modify")
admin_bp.add_route(UserAdminModifyView.as_view(), "/user/admin/modify", name="user_admin_modify")
admin_bp.add_route(UserInfoModifyView.as_view(), "/user/info/modify", name="user_info_modify")
admin_bp.add_route(UserInfoAdminModifyView.as_view(), "/user/info/admin/modify", name="user_info_admin_modify")
admin_bp.add_route(UserPswModifyView.as_view(), "/user/psw/modify", name="user_psw_modify")
admin_bp.add_route(UserPswAdminModifyView.as_view(), "/user/psw/admin/modify", name="user_psw_admin_modify")

# 角色
admin_bp.add_route(RoleTableView.as_view(), "/role/table", name="role_table")
admin_bp.add_route(RoleAddView.as_view(), "/role/add", name="role_add")
admin_bp.add_route(RoleDelView.as_view(), "/role/del", name="role_del")
admin_bp.add_route(RoleModifyView.as_view(), "/role/modify", name="role_modify")

# 系统设置
admin_bp.add_route(SystemSettingsMenuView.as_view(), "/system/menu", name="system_menu")
admin_bp.add_route(SystemAuthSettingsView.as_view(), "/system/auth/modify", name="system_auth_modify")
