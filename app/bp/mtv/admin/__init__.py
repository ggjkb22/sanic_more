# Author: Q
# Date:   2023-4-8
# Desc:   后台管理蓝图

from sanic import Blueprint
from .index import AdminIndexView
from .user import *

admin_bp = Blueprint("admin", url_prefix="/admin")

admin_bp.add_route(AdminIndexView.as_view(), "/index", name="index")
admin_bp.add_route(UserTableView.as_view(), "/user/table", name="user_table")
admin_bp.add_route(UserAddView.as_view(), "/user/add", name="user_add")
admin_bp.add_route(UserDelView.as_view(), "/user/del", name="user_del")
admin_bp.add_route(UserModifyView.as_view(), "/user/modify", name="user_modify")
admin_bp.add_route(UserModifyView.as_view(), "/user/info/modify", name="user_info_modify")
admin_bp.add_route(UserModifyView.as_view(), "/user/psw/modify", name="user_psw_modify")
admin_bp.add_route(UserModifyView.as_view(), "/user/psw/admin/modify", name="user_psw_admin_modify")





