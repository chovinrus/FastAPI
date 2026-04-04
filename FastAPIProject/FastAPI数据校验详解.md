# FastAPI 数据校验详解

## 一、核心组件

### 1. Query 参数校验
```python
from fastapi import Query

async def read_items(
    q: str | None = Query(default=None, max_length=50, min_length=3),
    skip: int = Query(default=0, ge=0, le=100),  # ge: >=, le: <=
    limit: int = Query(default=10, gt=0),  # gt: >, lt: <
    tags: list[str] = Query(default=[])  # 数组参数：?tags=python&tags=fastapi
):
    pass
```

**常用参数：**
- `default`: 默认值
- `alias`: 参数别名（URL 中使用）
- `title/description`: API 文档说明
- `gt/ge/lt/le`: 数值范围（大于/大于等于/小于/小于等于）
- `min_length/max_length`: 字符串长度
- `regex`: 正则表达式校验
- `deprecated`: 标记废弃参数

### 2. Path 参数校验
```python
from fastapi import Path

async def get_user(
    user_id: int = Path(..., ge=1, le=10000),  # ... 表示必填
    username: str = Path(..., min_length=3, pattern=r"^[a-z]+$")  # pattern 正则
):
    pass
```

### 3. Body 参数校验（配合 Pydantic）

#### 基础 Field 声明
```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="用户名，只能包含字母数字下划线"
    )
    
    email: EmailStr = Field(..., description="邮箱地址")
    
    age: int = Field(
        default=18,
        ge=0,
        le=150,
        description="年龄"
    )
    
    password: str = Field(..., min_length=8)
    
    tags: list[str] = Field(default=[], max_items=5)
    
    # 嵌套模型
    address: Optional["Address"] = None

class Address(BaseModel):
    city: str = Field(..., max_length=50)
    zip_code: str = Field(..., pattern=r"^\d{6}$")
```

#### Pydantic 验证器（Validators）
```python
from pydantic import BaseModel, field_validator, model_validator

class UserCreate(BaseModel):
    password: str
    confirm_password: str
    birth_date: datetime
    
    # 单字段验证器
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("密码至少8位")
        if not any(c.isdigit() for c in v):
            raise ValueError("密码必须包含数字")
        return v
    
    # 多字段联合验证器
    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("两次密码不一致")
        return self
    
    # 字段级别的 before 验证（类型转换前）
    @field_validator("birth_date", mode="before")
    @classmethod
    def parse_birth_date(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v
```

#### ConfigDict 全局配置
```python
from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,  # 自动去除字符串空格
        validate_default=True,       # 验证默认值
        extra="forbid",              # 禁止额外字段（严格模式）
        # extra="ignore"             # 忽略额外字段
        # extra="allow"              # 允许额外字段
        arbitrary_types_allowed=True # 允许任意类型
    )
    
    username: str
    email: str
```

#### 类型注解验证（Type Annotations）
```python
from typing import Annotated
from pydantic import BeforeValidator, AfterValidator

# 自定义类型转换
def normalize_username(v: str) -> str:
    return v.strip().lower()

Username = Annotated[str, BeforeValidator(normalize_username)]

# 自定义验证
def validate_age(v: int) -> int:
    if v < 0 or v > 150:
        raise ValueError("年龄无效")
    return v

Age = Annotated[int, AfterValidator(validate_age)]

class User(BaseModel):
    username: Username  # 自动 strip + lower
    age: Age            # 自动验证范围
```

#### FastAPI Body 特殊参数
```python
from fastapi import Body, File, UploadFile, Form

# 基础 Body
async def create_user(user: UserCreate = Body(..., embed=True)):
    # embed=True 时，JSON 格式：{"user": {"username": "test", ...}}
    # embed=False 时，JSON 格式：{"username": "test", ...}
    pass

# 多个 Body 参数（必须 embed）
async def create_order(
    user: UserCreate = Body(..., embed=True),
    product: ProductCreate = Body(..., embed=True)
):
    pass

# 文件上传
async def upload_file(
    file: UploadFile = File(...),
    description: str = Form(...)  # 混合表单字段
):
    pass

# Body 的描述性参数
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

#### 预定义类型验证
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

#### 嵌套验证
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

## 二、高级校验场景

### 1. 动态验证（依赖注入）
```python
from fastapi import Depends, Body, HTTPException

async def validate_user_permission(
    user_id: int = Body(...),
    current_user: User = Depends(get_current_user)
):
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(403, "无权限")
    return user_id

@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    validated_id: int = Depends(validate_user_permission),
    user_data: UserUpdate = Body(...)
):
    pass
```

### 2. Union 类型校验
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

## 三、实际项目应用示例

### 完整 Body 验证示例

```python
from fastapi import APIRouter, Query, Path, Body
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

router = APIRouter()

class TodoCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )
    
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: int = Field(default=1, ge=1, le=5)
    due_date: Optional[datetime] = None
    tags: list[str] = Field(default_factory=list, max_items=5)
    
    @field_validator("title")
    @classmethod
    def title_cannot_be_blank(cls, v):
        if not v.strip():
            raise ValueError("标题不能为空白")
        return v
    
    @field_validator("tags")
    @classmethod
    def tags_must_be_unique(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("标签不能重复")
        return [tag.lower() for tag in v]  # 自动转小写
    
    @model_validator(mode="after")
    def due_date_must_be_future(self):
        if self.due_date and self.due_date < datetime.now():
            raise ValueError("截止日期必须是未来时间")
        return self

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Optional[int] = Field(None, ge=1, le=5)
    is_completed: Optional[bool] = None
    due_date: Optional[datetime] = None

@router.get("/todos")
async def get_todos(
    skip: int = Query(default=0, ge=0, description="跳过的记录数"),
    limit: int = Query(default=10, ge=1, le=100, description="每页数量"),
    priority: Optional[int] = Query(None, ge=1, le=5),
    is_completed: Optional[bool] = Query(None),
    search: Optional[str] = Query(None, max_length=50)
):
    """查询待办事项列表（支持分页、筛选、搜索）"""
    pass

@router.post("/todos")
async def create_todo(todo: TodoCreate):
    """创建待办事项"""
    pass

@router.put("/todos/{todo_id}")
async def update_todo(
    todo_id: int = Path(..., ge=1, description="待办事项ID"),
    todo: TodoUpdate = Body(..., description="更新内容")
):
    """更新待办事项"""
    pass
```

## 四、校验体系总结

| 验证方式 | 适用场景 | 示例 |
|---------|---------|------|
| `Field` | 声明式基础校验（长度、范围、正则） | `Field(..., min_length=3, ge=0)` |
| `@field_validator` | 单字段自定义逻辑 | 密码复杂度、格式转换 |
| `@model_validator` | 多字段联合验证 | 密码确认、日期范围 |
| `ConfigDict` | 全局配置 | 严格模式、自动去空格 |
| `Annotated + Validators` | 类型级别验证 | 自定义类型转换 |
| 预定义类型 | 开箱即用 | `EmailStr`、`HttpUrl`、`UUID4` |
| `Body(embed=True)` | 多个 Body 参数 | 嵌套 JSON 结构 |
| 依赖注入 | 业务逻辑验证 | 权限校验、用户认证 |

## 五、校验错误响应示例

FastAPI 自动返回 422 错误，格式如下：
```json
{
  "detail": [
    {
      "type": "greater_than_equal",
      "loc": ["body", "priority"],
      "msg": "Input should be greater than or equal to 1",
      "input": 0,
      "ctx": {"ge": 1}
    },
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 characters",
      "input": ""
    }
  ]
}
```

## 六、校验规则速查表

| 校验类型 | 参数 | 说明 |
|---------|------|------|
| 数值范围 | `gt`/`ge`/`lt`/`le` | 大于/大于等于/小于/小于等于 |
| 字符串长度 | `min_length`/`max_length` | 最小/最大长度 |
| 列表长度 | `min_items`/`max_items` | 最小/最大项数 |
| 正则匹配 | `pattern` | 正则表达式 |
| 唯一值 | `unique_items` | 列表元素唯一 |
| 倍数校验 | `multiple_of` | 必须是某数的倍数 |
| 日期范围 | `gt`/`ge`/`lt`/`le` | 可用于 datetime |

## 七、核心优势

这些校验会自动：
1. **生成 OpenAPI 文档**（Swagger UI 自动展示校验规则）
2. **返回标准化错误**（422 Unprocessable Entity）
3. **类型自动转换**（字符串 `"123"` → 整数 `123`）

## 八、实战案例：Todo 项目改造

### 改造前的问题
- 验证逻辑写在服务层（`_validate_todo` 方法）
- 手动判断空值、时间比较
- 抛出业务异常而非标准校验错误
- 更新接口使用全量模型，不支持部分更新

### 改造后的方案

#### 1. 模型层验证（TodoCreate）
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

#### 2. 部分更新模型（TodoUpdate）
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

#### 3. 路由层增强
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

#### 4. 服务层简化
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

| 维度 | 改造前 | 改造后 |
|------|--------|--------|
| 验证位置 | 服务层手动判断 | 模型层自动验证 |
| 错误返回 | 业务异常（500/400） | 标准 422 校验错误 |
| API 文档 | 无字段说明 | 自动生成 description |
| 更新接口 | 全量更新 | 支持部分更新 |
| 代码行数 | 验证逻辑 30+ 行 | 验证逻辑 0 行（服务层） |
| 字段过滤 | 无 | `extra="forbid"` 禁止非法字段 |
| 字符串处理 | 手动 `.strip()` | `str_strip_whitespace=True` |
| 响应过滤 | 无 | `response_model` 自动过滤 |

### 关键技巧总结

1. **验证前置**：把验证从服务层移到模型层，服务层只处理纯业务逻辑
2. **部分更新**：使用 `model_dump(exclude_unset=True)` 只获取客户端提供的字段
3. **响应过滤**：使用 `response_model` 自动剔除敏感字段或内部字段
4. **严格模式**：`extra="forbid"` 防止客户端传入未定义字段
5. **自动处理**：`str_strip_whitespace=True` 自动去除空格，无需手动处理
