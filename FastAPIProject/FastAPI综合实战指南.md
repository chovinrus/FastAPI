# FastAPI 综合实战指南

## 一、框架选型：为什么选择 FastAPI？

### 1. 三大框架核心对比

| 维度          | Django            | Flask          | FastAPI               |
|-------------|-------------------|----------------|-----------------------|
| **定位**      | 全栈重型框架            | 微框架（灵活轻量）      | 现代异步高性能 API 框架        |
| **开发模式**    | 约定优于配置            | 完全自由           | 约定+类型提示驱动             |
| **异步支持**    | 3.1+ 部分支持（笨重）     | 需第三方扩展         | 原生 `async/await` 一等公民 |
| **类型系统**    | 无原生类型提示           | 无原生类型提示        | Pydantic 强类型校验        |
| **API 文档**  | 需额外插件（DRF）        | 需手写            | OpenAPI/Swagger 自动生成  |
| **性能（TPS）** | 低（约 500-1000）     | 中（约 2000-5000） | 极高（约 10000-50000+）    |
| **学习曲线**    | 陡峭（ORM、模板、中间件全家桶） | 平缓             | 中等（需理解类型提示+异步）        |
| **适用场景**    | 传统 CRUD、CMS、后台管理  | 小型项目、原型、灵活定制   | 高并发 API、微服务、AI/ML 接口  |

> **TPS（Transactions Per Second）**：每秒处理的事务数，衡量系统吞吐量的核心指标。同样配置下，FastAPI 一秒钟能处理的请求数是
> Django 的 10-50 倍。

### 2. 为什么 AI 应用开发首选 FastAPI？

AI 项目不是简单增删改查，而是**高延迟外部调用 + 严格数据契约 + 高并发网关**的典型场景。FastAPI 的设计哲学正好命中这些痛点：

- **异步原生**：AI 模型调用（尤其是 LLM API、向量数据库检索）本质上是 I/O 密集型任务。FastAPI 基于 `async/await`
  可以并发处理数百个请求而不阻塞，等待 LLM 响应时不阻塞其他请求。
- **类型驱动**：AI 应用需要频繁处理结构化数据（Prompt 模板、JSON Schema、工具调用参数）。Pydantic 强类型校验能减少幻觉风险。
- **生态兼容**：与 Python AI 生态（PyTorch、LangChain、LlamaIndex）零摩擦集成。LangChain 可以直接解析 FastAPI 的 OpenAPI
  Schema 实现自动工具注册。
- **高性能**：基于 Starlette（ASGI 框架），单节点支撑高并发推理请求。

## 二、核心概念与快速上手

### 1. 什么是 FastAPI？为什么它这么快？

FastAPI 是一个现代、高性能的 Python Web 框架，基于标准 Python 类型提示构建。它的"快"体现在两个层面：

1. **运行速度快**：底层基于 Starlette（ASGI 服务器）和 Pydantic（数据校验），性能可媲美 Node.js 和 Go 语言。
2. **开发效率高**：自动生成交互式 API 文档，减少约 40% 的样板代码。

**核心架构：**

- **Uvicorn**：ASGI 服务器，负责接收网络请求并启动事件循环。
- **Starlette**：轻量级 Web 框架，处理路由、请求/响应生命周期。
- **Pydantic**：数据校验库，负责将 JSON 转为 Python 对象并验证格式。

### 2. 项目初始化

```bash
# 使用 uv 推荐方式
uv add fastapi uvicorn[standard]

# 或使用 pip
pip install fastapi uvicorn[standard]
```

最小应用示例：

```python
# main.py
from fastapi import FastAPI

app = FastAPI(title="My API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Hello FastAPI"}

# 启动
# uvicorn main:app --reload
```

启动后自动提供：

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 三、路由系统：请求分发中心

### 1. 路由装饰器的工作原理

FastAPI 使用 Python 装饰器（`@app.get`, `@app.post`）将 URL 路径映射到具体的处理函数。当请求到达时，框架会：

1. 匹配 URL 路径和 HTTP 方法。
2. 提取路径参数、查询参数、请求体。
3. 进行类型转换和校验。
4. 调用处理函数并返回结果。

```python
@app.get("/items")
async def get_items():
    pass


@app.post("/items")
async def create_item(item: Item):
    pass


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    pass


@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    pass
```

### 2. 路径参数（Path Parameters）vs 查询参数（Query Parameters）

**路径参数**是 URL 中固定的动态部分，通常用于定位资源（如 `/users/123`）。它是 URL 路径的一部分。

**查询参数**是 URL `?` 后面的键值对，通常用于过滤、分页（如 `/users?status=active&page=1`）。

**最佳实践：**

- 资源标识符（ID、UUID）使用路径参数。
- 过滤条件、排序规则、分页信息使用查询参数。

```python
from fastapi import Path, Query
from typing import Optional

# 路径参数示例
@app.get("/users/{user_id}")
async def get_user(
    user_id: int = Path(..., ge=1, description="用户 ID"),
    username: str = Path(..., min_length=3)
):
    return {"user_id": user_id, "username": username}

# 查询参数示例
@app.get("/items/")
async def list_items(
    skip: int = Query(default=0, ge=0, description="跳过数量"),
    limit: int = Query(default=10, ge=1, le=100),
    category: Optional[str] = Query(None, description="分类筛选")
):
    return {"skip": skip, "limit": limit, "category": category}
```

### 3. `APIRouter` 与模块化

随着项目变大，所有路由写在 `main.py` 会导致代码臃肿。`APIRouter` 允许我们将路由拆分到不同模块，最后统一挂载。

**`tags` 的作用：**
`tags` 用于在 Swagger UI 和 ReDoc 文档中对接口进行**分组归类**。相同标签的接口会聚合显示在同一个折叠面板下，方便前端开发人员按业务模块查找
API。

```python
# router/users.py
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["用户管理"])

@router.get("/")
async def get_users():
    pass

# main.py
from router.users import router as users_router

app.include_router(users_router)
# 效果：在 Swagger UI 中，该路由下的所有接口都会显示在"用户管理"标签下
```

## 四、请求体与类型校验：Pydantic 的核心价值

### 1. 为什么需要强类型校验？

在 Java 中，Spring Boot 会通过注解（如 `@Valid`, `@NotNull`）进行校验。在 Python 中，FastAPI 利用 Python 3.6+ 的类型提示（Type
Hints）结合 Pydantic 实现**声明式校验**。

**优势：**

- **提前拦截错误**：无效数据在路由函数执行前就会被拒绝，返回 422 状态码。
- **自动类型转换**：客户端传来的字符串 `"123"` 会自动转为整数 `123`。
- **文档自动生成**：字段类型、校验规则会自动同步到 Swagger 文档中。

### 2. 请求体模型（Request Model）

使用 Pydantic 的 `BaseModel` 定义数据结构。FastAPI 会自动将请求体 JSON 解析为对应的模型实例。

```python
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    age: int = Field(default=18, ge=0, le=150)
    bio: Optional[str] = Field(None, max_length=500)
    
    class Config:
        str_strip_whitespace = True  # 自动去空格
        extra = "forbid"             # 禁止额外字段
```

接收请求体：

```python
@app.post("/users/", response_model=UserOut)
async def create_user(user: UserCreate):
    # user 已自动校验并转为 Python 对象
    return user
```

### 3. 高级校验（Validators）

**单字段验证器：**

```python
from pydantic import field_validator

class UserCreate(BaseModel):
    password: str
    
    @field_validator("password")
    @classmethod
    def check_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("密码至少 8 位")
        return v
```

**跨字段验证器：**

```python
from pydantic import model_validator

class UserCreate(BaseModel):
    password: str
    confirm_password: str
    
    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("两次密码不一致")
        return self
```

**ConfigDict 全局配置：**

```python
from pydantic import ConfigDict

class UserCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,  # 自动去除字符串空格
        validate_default=True,       # 验证默认值
        extra="forbid",              # 禁止额外字段（严格模式）
        arbitrary_types_allowed=True # 允许任意类型
    )
```

### 4. 校验的优先级与位置

**推荐将校验逻辑前置到模型层（Pydantic），而不是在服务层写 `if` 判断。**

- **声明式校验**（如 `min_length`, `regex`）：在 `Field` 中配置。
- **自定义校验**（如密码复杂度）：使用 `@field_validator`。
- **跨字段校验**（如确认密码）：使用 `@model_validator(mode="after")`。

### 5. 类型注解验证（Type Annotations）

除了使用装饰器，Pydantic 还支持通过 `Annotated` 类型注解进行验证，适合复用验证逻辑：

```python
from typing import Annotated
from pydantic import BeforeValidator, AfterValidator

# 自定义类型转换（类型转换前执行）
def normalize_username(v: str) -> str:
    return v.strip().lower()

Username = Annotated[str, BeforeValidator(normalize_username)]

# 自定义验证（类型转换后执行）
def validate_age(v: int) -> int:
    if v < 0 or v > 150:
        raise ValueError("年龄无效")
    return v

Age = Annotated[int, AfterValidator(validate_age)]

class User(BaseModel):
    username: Username  # 自动 strip + lower
    age: Age            # 自动验证范围
```

**BeforeValidator vs AfterValidator：**

- `BeforeValidator`：在类型转换之前执行，适合数据清洗和格式转换。
- `AfterValidator`：在类型转换之后执行，适合业务规则验证。

### 6. 预定义类型验证

Pydantic 提供了开箱即用的特殊类型，自动处理常见验证场景：

```python
from pydantic import (
    BaseModel, 
    EmailStr,         # 邮箱验证
    HttpUrl,          # URL 验证
    IPvAnyAddress,    # IP 地址验证
    SecretStr,        # 密钥（打印时隐藏）
    UUID4,            # UUID 验证
    PositiveInt,      # 正整数
    NegativeFloat,    # 负浮点数
    NonNegativeInt,   # 非负整数
    conint,           # 约束整数
    constr,           # 约束字符串
    conlist           # 约束列表
)

class User(BaseModel):
    email: EmailStr                    # 自动验证邮箱格式
    website: HttpUrl                   # 自动验证 URL
    ip: IPvAnyAddress                  # IPv4/IPv6
    api_key: SecretStr                 # 密钥字段
    user_id: UUID4                     # UUID v4
    age: PositiveInt                   # > 0
    tags: conlist(str, min_length=1, max_length=5)  # 1-5个标签
    code: constr(min_length=6, max_length=6, pattern=r"^\d{6}$")  # 6位数字
```

**常用预定义类型说明：**

- `EmailStr`：验证邮箱格式，需要安装 `email-validator` 包。
- `HttpUrl`：验证 HTTP/HTTPS URL 格式。
- `SecretStr`：敏感字段，打印或序列化时自动隐藏。
- `UUID4`：验证 UUID v4 格式。
- `conint`/`constr`：约束类型，可内联配置范围、长度、正则等。

### 7. 嵌套验证

Pydantic 会自动递归验证嵌套模型：

```python
class Address(BaseModel):
    city: str
    zip_code: str = Field(..., pattern=r"^\d{6}$")

class UserCreate(BaseModel):
    name: str
    addresses: list[Address]  # 自动递归验证列表中的每个 Address
    
    @field_validator("addresses")
    @classmethod
    def validate_addresses(cls, v):
        if len(v) == 0:
            raise ValueError("至少需要一个地址")
        return v
```

### 8. FastAPI Body 特殊参数

**Body 的 embed 参数：**

```python
from fastapi import Body


# embed=True 时，JSON 格式：{"user": {"username": "test", ...}}
# embed=False 时，JSON 格式：{"username": "test", ...}
async def create_user(user: UserCreate = Body(..., embed=True)):
    pass


# 多个 Body 参数（必须 embed）
async def create_order(
        user: UserCreate = Body(..., embed=True),
        product: ProductCreate = Body(..., embed=True)
):
    pass
```

**文件上传与混合表单：**

```python
from fastapi import File, UploadFile, Form

async def upload_file(
    file: UploadFile = File(...),
    description: str = Form(...)  # 混合表单字段
):
    pass
```

**Body 的描述性参数：**

```python
async def create_item(
    item: Item = Body(
        ...,
        title="创建项目",
        description="项目详细信息",
        examples=[{
            "name": "示例项目",
            "price": 99.9
        }]
    )
):
    pass
```

### 9. Union 类型校验

当接口需要接收多种类型的数据时，可以使用 Union：

```python
from typing import Union

class Cat(BaseModel):
    meow_volume: int

class Dog(BaseModel):
    bark_volume: int

Pet = Union[Cat, Dog]

class Owner(BaseModel):
    pet: Pet  # 自动根据字段判断类型
```

## 五、响应处理：数据输出控制

### 1. `response_model` 的作用

`response_model` 有两个核心功能：

1. **数据过滤**：返回给客户端的数据只包含 `response_model` 中定义的字段。即使你的数据库对象包含密码，只要 `response_model`
   没定义，密码就不会泄露。
2. **文档生成**：在 OpenAPI 文档中明确告知前端该接口返回的数据结构。

```python
class UserOut(BaseModel):
    id: int
    username: str
    email: str
    # password 不会返回（未定义）


@app.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: int):
    user = {"id": 1, "username": "john", "email": "john@test.com", "password": "secret"}
    return user  # 自动过滤 password
```

### 2. 自定义响应与标准化包装

```python
from fastapi.responses import JSONResponse

@app.post("/items/")
async def create_item(item: Item):
    return JSONResponse(
        content={"message": "创建成功", "data": item.model_dump()},
        status_code=201,
        headers={"X-Custom": "value"}
    )
```

企业级项目通常需要统一的 JSON 结构（如 `{code, message, data}`）：

```python
from typing import Generic, TypeVar, Any, Optional

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    code: int
    message: str
    data: Optional[T] = None


def success_response(data: Any = None, message: str = "成功"):
    return APIResponse(code=200, message=message, data=data)
```

## 六、依赖注入（Dependency Injection）

### 1. 什么是依赖注入？

依赖注入是 FastAPI 最强大的特性之一。它允许你声明路由函数所需的"依赖"（如数据库连接、当前登录用户），框架会自动解析并提供实例。

**与 Spring Boot 的对比：**

- Spring 使用 `@Autowired` 或构造器注入，依赖通常在应用启动时创建。
- FastAPI 的依赖是**请求级别**的，每次请求都会执行依赖函数，非常适合处理请求上下文（如获取当前 Token 对应的用户）。

### 2. 基础依赖与依赖链

```python
from fastapi import Depends


def get_db():
    db = "database_connection"
    try:
        yield db
    finally:
        db.close()


@app.get("/items/")
async def read_items(db: str = Depends(get_db)):
    return {"db": db}
```

依赖链示例：

```python
def get_current_user(token: str = Depends(oauth2_scheme)):
    return decode_token(token)


def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(403, "需要管理员权限")
    return current_user


@app.delete("/items/{item_id}")
async def delete_item(
        item_id: int,
        admin: User = Depends(get_admin_user)
):
    pass
```

### 3. 常见使用场景

- **数据库会话管理**：每个请求获取一个 DB Session，请求结束后自动关闭。
- **权限校验**：多个接口需要验证用户是否登录，提取为公共依赖。
- **分页参数解析**：将 `skip` 和 `limit` 的校验逻辑封装为依赖。

## 七、异常处理：标准化错误响应

### 1. HTTP 异常与业务异常

- **HTTP 异常**：使用 `raise HTTPException(status_code=404, detail="...")`，框架会自动返回标准错误 JSON。
- **业务异常**：建议自定义异常类（继承 `Exception`），包含业务状态码（如 `10001`），通过全局异常处理器统一转换为 JSON 响应。

```python
from fastapi import HTTPException


@app.get("/items/{item_id}")
async def get_item(item_id: int):
    item = db.get(item_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail=f"商品 {item_id} 不存在",
            headers={"X-Error": "Not Found"}
        )
    return item
```

### 2. 全局异常处理器

通过 `@app.exception_handler` 捕获特定类型的异常，将其转换为统一的业务响应格式。这能避免系统直接返回 500
原始堆栈信息，提升安全性与用户体验。

```python
from fastapi import Request
from fastapi.exceptions import RequestValidationError


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"code": 400, "message": "参数校验失败", "errors": exc.errors()}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误"}
    )
```

## 八、异步编程：高并发的关键

### 1. `async def` 与 `def` 的区别

- **`async def`**：声明协程函数。当遇到 `await`（如数据库查询、HTTP 请求）时，事件循环会挂起当前任务，去处理其他请求，直到 I/O
  完成再恢复。**这是高并发的核心。**
- **`def`**：同步函数。FastAPI 会将其放入线程池执行，避免阻塞事件循环。适用于 CPU 密集型任务或未提供异步支持的第三方库。

### 2. AI 场景下的异步优势

AI 应用通常涉及调用外部 LLM API 或向量数据库，这些操作耗时较长（几百毫秒到几秒）。使用异步路由可以在等待模型响应时处理成百上千个其他请求，极大提升系统吞吐量。

```python
import aiohttp

@app.get("/external-data")
async def get_external_data():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.example.com/data") as resp:
            return await resp.json()
```

### 3. 后台任务

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    # 发送邮件逻辑
    pass

@app.post("/send-notification")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email, email, "通知内容")
    return {"message": "通知已发送"}
```

## 九、文档集成：零成本维护

FastAPI 基于 OpenAPI 规范，启动后自动生成三套文档。

**文档丰富的技巧：**

```python
@app.post(
    "/items/",
    summary="创建商品",
    description="创建新商品，需要管理员权限",
    response_description="返回创建的商品信息",
    tags=["商品管理"],
    responses={
        201: {"description": "创建成功"},
        400: {"description": "参数错误"},
        401: {"description": "未授权"}
    }
)
async def create_item(item: Item):
    pass
```

字段文档：

```python
class Item(BaseModel):
    name: str = Field(..., description="商品名称", examples=["iPhone 15"])
    price: float = Field(..., gt=0, description="价格（元）", examples=[999.0])
```

## 十、中间件与生命周期

### 1. 中间件

```python
from starlette.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. 生命周期事件

```python
@app.on_event("startup")
async def startup_event():
    print("应用启动，初始化数据库连接")

@app.on_event("shutdown")
async def shutdown_event():
    print("应用关闭，释放资源")
```

## 十一、项目结构与最佳实践

### 1. 推荐的目录结构

合理的目录结构能降低维护成本：

```
myapp/
├── main.py              # 入口，配置中间件、挂载路由
├── core/                # 核心配置、异常、安全相关
│   ├── config.py        # 环境变量配置
│   ├── status_codes.py  # 业务状态码枚举
│   └── exceptions.py    # 自定义异常
├── models/              # Pydantic 数据模型（DTO）
│   └── user.py
├── router/              # 路由定义，尽量保持轻量
│   └── user.py
├── services/            # 业务逻辑层，处理复杂规则
│   └── user_service.py
└── utils/               # 工具函数、辅助类
```

### 2. 常用命令

```bash
# 开发环境启动（自动重载）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产环境启动
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. 避坑指南

1. **不要在路由函数中写复杂业务逻辑**：路由只负责参数接收和响应返回，业务逻辑应下沉到 `services` 层。
2. **警惕同步阻塞代码**：在 `async def` 中调用耗时同步函数（如 `time.sleep` 或 `requests.get`）会阻塞整个服务。
3. **配置外部化**：数据库地址、密钥等敏感信息务必通过环境变量注入，不要硬编码。
4. **统一时区处理**：涉及时间比较时，确保所有 `datetime` 对象都是 `aware`（带时区信息）类型，避免 `TypeError`。
5. **类型提示**：始终使用类型提示，让 FastAPI 自动校验。
6. **异步优先**：I/O 操作使用 `async/await`。
7. **依赖注入**：复用数据库连接、认证逻辑。
8. **Pydantic 校验**：在模型层做数据校验，服务层只处理业务。
9. **异常处理**：使用全局异常处理器统一错误格式。
10. **文档完善**：为每个接口添加 `summary`、`description`、`examples`。

## 十二、校验体系速查表

| 校验类型  | 参数                        | 说明              |
|-------|---------------------------|-----------------|
| 数值范围  | `gt`/`ge`/`lt`/`le`       | 大于/大于等于/小于/小于等于 |
| 字符串长度 | `min_length`/`max_length` | 最小/最大长度         |
| 列表长度  | `min_items`/`max_items`   | 最小/最大项数         |
| 正则匹配  | `pattern`                 | 正则表达式           |
| 唯一值   | `unique_items`            | 列表元素唯一          |
| 倍数校验  | `multiple_of`             | 必须是某数的倍数        |
| 日期范围  | `gt`/`ge`/`lt`/`le`       | 可用于 datetime    |

| 验证方式                     | 适用场景              | 示例                               |
|--------------------------|-------------------|----------------------------------|
| `Field`                  | 声明式基础校验（长度、范围、正则） | `Field(..., min_length=3, ge=0)` |
| `@field_validator`       | 单字段自定义逻辑          | 密码复杂度、格式转换                       |
| `@model_validator`       | 多字段联合验证           | 密码确认、日期范围                        |
| `ConfigDict`             | 全局配置              | 严格模式、自动去空格                       |
| `Annotated + Validators` | 类型级别验证            | 自定义类型转换                          |
| 预定义类型                    | 开箱即用              | `EmailStr`、`HttpUrl`、`UUID4`     |
| `Body(embed=True)`       | 多个 Body 参数        | 嵌套 JSON 结构                       |
| 依赖注入                     | 业务逻辑验证            | 权限校验、用户认证                        |

## 十三、实战案例：Todo 项目改造

### 改造前的问题

- 验证逻辑写在服务层（`_validate_todo` 方法）
- 手动判断空值、时间比较
- 抛出业务异常而非标准校验错误
- 更新接口使用全量模型，不支持部分更新

### 改造后的方案

**1. 模型层验证（TodoCreate）：**

```python
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from datetime import datetime, timezone

class TodoCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,  # 自动去除空格
        extra="forbid"              # 禁止额外字段
    )
    
    # 使用 Field 声明式校验
    task: str = Field(..., min_length=1, max_length=200, description="任务内容")
    deadline: datetime = Field(..., description="截止时间")
    assigned_to: str = Field(..., min_length=2, max_length=50, description="负责人")
    priority: int = Field(default=3, ge=1, le=5, description="优先级 1-5")
    
    # 单字段自定义验证
    @field_validator("task")
    @classmethod
    def task_cannot_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("任务内容不能为空")
        return v
    
    # 多字段联合验证（时间比较）
    @model_validator(mode="after")
    def validate_deadline_must_be_future(self):
        if self.deadline.tzinfo is None:
            deadline_utc = self.deadline.replace(tzinfo=timezone.utc)
        else:
            deadline_utc = self.deadline.astimezone(timezone.utc)
        
        if deadline_utc < datetime.now(timezone.utc):
            raise ValueError("截止时间不能早于当前时间")
        return self
```

**2. 部分更新模型（TodoUpdate）：**

```python
class TodoUpdate(BaseModel):
    """所有字段可选，支持部分更新"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )
    
    task: Optional[str] = Field(None, min_length=1, max_length=200)
    deadline: Optional[datetime] = None
    assigned_to: Optional[str] = Field(None, min_length=2, max_length=50)
    priority: Optional[int] = Field(None, ge=1, le=5)
    is_finished: Optional[bool] = None
    
    @field_validator("task")
    @classmethod
    def task_cannot_be_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("任务内容不能为空")
        return v
    
    @model_validator(mode="after")
    def validate_deadline_if_provided(self):
        """只在提供了 deadline 时验证"""
        if self.deadline is not None:
            # ... 时间验证逻辑
        return self
```

**3. 路由层增强：**

```python
from fastapi import APIRouter, Query, Path


@router.get('/todos/', response_model=list[Todo])
async def get_todos(
        skip: int = Query(default=0, ge=0, description="跳过记录数"),
        limit: int = Query(default=10, ge=1, le=100, description="返回记录上限")
):
    pass


@router.get('/todos/{id}', response_model=Todo)
async def get_todo(
        id: str = Path(..., min_length=1, description="Todo 唯一标识符")
):
    pass


@router.post('/todos/', response_model=Todo, status_code=201)
async def create_todo(todo_create: TodoCreate):
    pass
```

**4. 服务层简化：**

```python
# 改造前：服务层手动验证
async def create(self, todo_create: TodoCreate) -> Todo:
    self._validate_todo(todo_create)  # 手动验证
    # ...


# 改造后：服务层只处理业务逻辑
async def create(self, todo_create: TodoCreate) -> Todo:
    # Pydantic 已验证字段格式，这里只处理业务逻辑
    todo_id = str(uuid.uuid4())
    todo_model = Todo(
        id=todo_id,
        task=todo_create.task,
        deadline=todo_create.deadline,
        assigned_to=todo_create.assigned_to,
        priority=todo_create.priority,
        create_time=datetime.now()
    )
    self.todos[todo_id] = todo_model
    return todo_model


# 部分更新使用 model_dump(exclude_unset=True)
async def update(self, todo_id: str, todo_update: TodoUpdate) -> Todo:
    todo_origin = self.todos.get(todo_id)
    update_data = todo_update.model_dump(exclude_unset=True)  # 只获取客户端提供的字段

    updated_todo = Todo(
        id=todo_id,
        task=update_data.get('task', todo_origin.task),  # 未提供则保留原值
        deadline=update_data.get('deadline', todo_origin.deadline),
        # ...
    )
```

### 改造效果对比

| 维度     | 改造前           | 改造后                         |
|--------|---------------|-----------------------------|
| 验证位置   | 服务层手动判断       | 模型层自动验证                     |
| 错误返回   | 业务异常（500/400） | 标准 422 校验错误                 |
| API 文档 | 无字段说明         | 自动生成 description            |
| 更新接口   | 全量更新          | 支持部分更新                      |
| 代码行数   | 验证逻辑 30+ 行    | 验证逻辑 0 行（服务层）               |
| 字段过滤   | 无             | `extra="forbid"` 禁止非法字段     |
| 字符串处理  | 手动 `.strip()` | `str_strip_whitespace=True` |
| 响应过滤   | 无             | `response_model` 自动过滤       |

### 关键技巧总结

1. **验证前置**：把验证从服务层移到模型层，服务层只处理纯业务逻辑。
2. **部分更新**：使用 `model_dump(exclude_unset=True)` 只获取客户端提供的字段。
3. **响应过滤**：使用 `response_model` 自动剔除敏感字段或内部字段。
4. **严格模式**：`extra="forbid"` 防止客户端传入未定义字段。
5. **自动处理**：`str_strip_whitespace=True` 自动去除空格，无需手动处理。
