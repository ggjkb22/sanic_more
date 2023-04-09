# Sanic More
### 以此作为你的[Sanic](https://sanic.dev/zh/)项目的基础进行开发
<hr>

## 介绍

Sanic More 是一个帮助Sanic使用者进行快速开发的Sanic基础项目。它的功能还在逐步完善中，目前它能够为您提供以下便捷：
1. 提供了一个基础的项目结构
2. 提供 MTV 蓝图组用于开发前后端不分离式项目
    - 异步jinja2渲染
    - 配合sanic_session提供csrf保护
    - 配合pydantic进行表单解析与验证
3. 使用 Tortoise ORM 进行SQL操作，
    - ORM序列化器
<hr>

### 如何使用
将本项目克隆到本地即可开始使用
```python
git clone https://github.com/ggjkb22/sanic_more.git
```
<hr>

### 异步jinja2渲染
```python
from app.template import jinja2_async_render

class TestView(HTTPMethodView):
    async def get(self, request: Request):
        temp_context = {
            "request": request,
            "csrf": request.ctx.session["csrf_token"]
        }
        return await jinja2_async_render("test/bbb.html", temp_context)
```
<hr>

### 配合sanic_session提供csrf保护
只需要在路由上下文中加上 ```ctx_csrf=True``` 并将当前蓝图加入mtv蓝图组即可实现csrf保护
```python
from sanic import Blueprint
from app.exception import register_mtv_error_handler
from app.middles import register_mtv_middles
from app.extends import register_session_extends

ft = Blueprint("ft", url_prefix="/ft")

# 针对类视图的csrf保护
ft.add_route(TestFormView.as_view(), "/form-test/<test_field:str>", ctx_csrf=True, name="form_test")  

mtv = Blueprint.group(ft, url_prefix="/mtv")

# 注册MTV蓝图组全局错误验证处理器
register_mtv_error_handler(mtv)

# 将sanic_session注册到应用中
# 这个注册必须要在csrf中间件之前执行,因为csrf依赖于sanic_session
register_session_extends(mtv)

# 注册中间件
register_mtv_middles(mtv)
```
<hr>

### 配合pydantic进行表单解析与验证
表单需要继承 ```SanicBaseModel``` 类，使用该类的```validate_sanic_form```并传入```request.form```
```python
from app.form import SanicBaseModel

class TestForm(SanicBaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    tests: Optional[List[str]] = Field(None, description="测试多选字段")
    date: Optional[datetime] = Field(None, description="时间")

class TestFormView(HTTPMethodView):
    async def post(self, request: Request, test_field: str):
        result, data = TestForm.validate_sanic_form(request.form)
        if not result:
            temp_ctx = {
                "request": request,
                "test_field": test_field,
                "csrf": request.ctx.session["csrf_token"],
                "errors": data
            }
            return await jinja2_async_render("aaa/test.html", temp_ctx)
        return json(data.json())
```
<hr>

### ORM序列化器
使用```from_torm_instance``` 和 ```from_torm_queryset``` 分别对ORM实例与QuerySet进行序列化
```python
from app.orm import TOrmSerialize
from app.orm.models.article import Category

category = await Category.get_or_none(pk=1).prefetch_related("child_categories").select_related("parent_category")
# 初始化序列化器，传入需要序列化的模型
# 可以使用include、exclude和computed进行字段过滤与筛选
cs = TOrmSerialize(Category, include=("id", "child_categories"))

# 使用from_torm_instance对实例进行序列化
ins_result = await cs.from_torm_instance(category)

# 使用from_torm_queryset对QuerySet进行序列化
category_query_set = Category.filter(pk__lte=2).prefetch_related("child_categories").select_related("parent_category")
qs = await c.from_torm_queryset(category_query_set)
print(qs["__root__"])
```
<hr>

## 运行说明:
1. 使用前请先完善 app/conf/.your_env 文件,用于敏感信息配置,修改完毕后将其重命名为.env, python-dotenv将会读取其中的配置
2. 使用 python server.py 运行服务
3. 使用 python commands.py xxx 运行命令行工具

<style>
hr {
  border-width: 1px;
}
</style>
