from sqlmodel import SQLModel, Field



# 定义模型，继承 SQLModel，table=True 表示该模型对应数据库中的表
class Book(SQLModel, table=True):
    # FIeld是sqlmodel的属性，Field(...)是pydantic的属性
    id: int | None = Field(primary_key=True, default=None, description='图书id')

    # index=True 表示该字段在数据库中创建索引，nullable=False 表示该字段不能为空
    title: str = Field(index=True, nullable=False, description='图书名称')

    author: str = Field(description='图书作者')

    price: float = Field(gt=0.0, description='图书价格')

    description: str | None = Field(default=None, description='图书描述')
