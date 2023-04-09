# Author: Q
# Date:   2023-4-8
# Desc:   表单测试蓝图(无用需删)

from sanic import Blueprint, Request, json
from sanic.views import HTTPMethodView
from app.template import jinja2_async_render
from app.verify.test import TestForm

ft = Blueprint("ft", url_prefix="/ft")

# 类视图测试
class TestFormView(HTTPMethodView):

    async def get(self, request: Request, test_field: str):
        temp_ctx = {
            "request": request,
            "test_field": test_field,
            "csrf": request.ctx.session["csrf_token"]
        }
        return await jinja2_async_render("aaa/test.html", temp_ctx)

    async def post(self, request: Request, test_field: str):
        res, data = TestForm.validate_sanic_form(request.form)
        if not res:
            temp_ctx = {
                "request": request,
                "test_field": test_field,
                "csrf": request.ctx.session["csrf_token"],
                "errors": data
            }
            return await jinja2_async_render("aaa/test.html", temp_ctx)
        return json(data.json())
        

ft.add_route(TestFormView.as_view(), "/form-test/<test_field:str>", ctx_csrf=True, name="form_test")  # 针对类视图的csrf保护