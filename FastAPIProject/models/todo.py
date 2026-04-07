"""Todo 数据模型模块

定义 Todo 事项的数据结构，包括请求模型与响应模型
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class TodoCreate(BaseModel):
    """Todo 创建请求模型
    
    Attributes:
        task: 任务内容描述（1-200字符）
        deadline: 任务截止时间（必须晚于当前时间）
        assigned_to: 任务负责人（2-50字符）
        priority: 优先级 1-5（可选，默认3）
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,  # 自动去除字符串首尾空格
        extra="forbid",  # 禁止额外字段
        json_schema_extra={
            "example": {
                "task": "完成项目文档",
                "deadline": "2026-12-31T23:59:59",
                "assigned_to": "张三",
                "priority": 3
            }
        }
    )

    task: str = Field(..., min_length=1, max_length=200, description="任务内容")
    deadline: datetime = Field(..., description="截止时间")
    assigned_to: str = Field(..., min_length=2, max_length=50, description="负责人")
    priority: int = Field(default=3, ge=1, le=5, description="优先级 1-5")

    @field_validator("task")
    @classmethod
    def task_cannot_be_blank(cls, v: str) -> str:
        """验证任务内容不能为空或纯空白"""
        if not v.strip():
            raise ValueError("任务内容不能为空")
        return v

    @model_validator(mode="after")
    def validate_deadline_must_be_future(self):
        """验证截止时间必须晚于当前时间"""
        if self.deadline.tzinfo is None:
            # 如果没有时区信息，假设为 UTC
            deadline_utc = self.deadline.replace(tzinfo=timezone.utc)
        else:
            deadline_utc = self.deadline.astimezone(timezone.utc)

        if deadline_utc < datetime.now(timezone.utc):
            raise ValueError("截止时间不能早于当前时间")
        return self


class TodoUpdate(BaseModel):
    """Todo 更新请求模型（所有字段可选）
    
    Attributes:
        task: 任务内容描述（可选）
        deadline: 任务截止时间（可选）
        assigned_to: 任务负责人（可选）
        priority: 优先级 1-5（可选）
        is_finished: 完成状态（可选）
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "task": "修改后的任务描述",
                "priority": 4,
                "is_finished": True
            }
        }
    )

    task: Optional[str] = Field(None, min_length=1, max_length=200)
    deadline: Optional[datetime] = None
    assigned_to: Optional[str] = Field(None, min_length=2, max_length=50)
    priority: Optional[int] = Field(None, ge=1, le=5)
    is_finished: Optional[bool] = None

    @field_validator("task")
    @classmethod
    def task_cannot_be_blank(cls, v: Optional[str]) -> Optional[str]:
        """验证任务内容不能为空或纯空白"""
        if v is not None and not v.strip():
            raise ValueError("任务内容不能为空")
        return v

    @model_validator(mode="after")
    def validate_deadline_if_provided(self):
        """如果提供了截止时间，验证必须晚于当前时间"""
        if self.deadline is not None:
            if self.deadline.tzinfo is None:
                deadline_utc = self.deadline.replace(tzinfo=timezone.utc)
            else:
                deadline_utc = self.deadline.astimezone(timezone.utc)

            if deadline_utc < datetime.now(timezone.utc):
                raise ValueError("截止时间不能早于当前时间")
        return self


class Todo(BaseModel):
    """Todo 完整响应模型
    
    Attributes:
        id: Todo 唯一标识符
        task: 任务内容描述
        deadline: 任务截止时间
        assigned_to: 任务负责人
        priority: 优先级
        create_time: 创建时间
        is_finished: 完成状态标记
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "task": "完成项目文档",
                "deadline": "2026-12-31T23:59:59",
                "assigned_to": "张三",
                "priority": 3,
                "is_finished": False
            }
        }
    )

    id: str
    task: str
    deadline: datetime
    assigned_to: str
    priority: int = 3
    create_time: datetime
    is_finished: bool = False
