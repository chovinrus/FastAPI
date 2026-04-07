"""Todo 业务服务模块

提供 Todo 事项的内存存储与业务逻辑处理
"""

import asyncio
import uuid
from datetime import datetime

from common.exceptions import TodoNotFoundException
from models import TodoCreate, Todo, TodoUpdate


class TodoService:
    """Todo 业务服务类
    
    负责 Todo 事项的业务逻辑处理，包括创建、查询、更新、删除等操作。
    当前使用内存存储（字典），后续可替换为数据库实现。
    """

    def __init__(self):
        """初始化服务实例
        
        Attributes:
            todos: 内存存储容器，使用字典存储 Todo 对象，键为 UUID
        """
        self.todos: dict[str, Todo] = {}

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Todo]:
        """获取 Todo 列表（支持分页）
        
        Args:
            skip: 跳过记录数，默认从第一条开始
            limit: 返回记录上限，默认最多 100 条
            
        Returns:
            list[Todo]: Todo 对象列表
        """
        await asyncio.sleep(0.05)
        all_todos = list(self.todos.values())
        return all_todos[skip: skip + limit]

    async def get_by_id(self, todo_id: str) -> Todo:
        """根据 ID 获取单个 Todo
        
        Args:
            todo_id: Todo 唯一标识符
            
        Returns:
            Todo: 对应的 Todo 对象
            
        Raises:
            TodoNotFoundException: 当指定 ID 的 Todo 不存在时
        """
        await asyncio.sleep(0.05)
        todo = self.todos.get(todo_id)
        if not todo:
            raise TodoNotFoundException(todo_id=todo_id)
        return todo

    async def create(self, todo_create: TodoCreate) -> Todo:
        """创建新的 Todo
        
        Args:
            todo_create: Todo 创建请求，包含任务内容、截止时间、负责人、优先级
            
        Returns:
            Todo: 创建成功的 Todo 对象
        """
        await asyncio.sleep(0.05)
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

    async def update(self, todo_id: str, todo_update: TodoUpdate) -> Todo:
        """更新现有 Todo（支持部分更新）
        
        Args:
            todo_id: 待更新的 Todo ID
            todo_update: 更新内容，所有字段可选
            
        Returns:
            Todo: 更新后的 Todo 对象
            
        Raises:
            TodoNotFoundException: 当指定 ID 的 Todo 不存在时
        """
        await asyncio.sleep(0.05)

        todo_origin = self.todos.get(todo_id)
        if not todo_origin:
            raise TodoNotFoundException(todo_id=todo_id)

        # Pydantic 已验证字段格式，这里只处理合并逻辑
        update_data = todo_update.model_dump(exclude_unset=True)

        updated_todo = Todo(
            id=todo_id,
            task=update_data.get('task', todo_origin.task),
            deadline=update_data.get('deadline', todo_origin.deadline),
            assigned_to=update_data.get('assigned_to', todo_origin.assigned_to),
            priority=update_data.get('priority', todo_origin.priority),
            create_time=todo_origin.create_time,
            is_finished=update_data.get('is_finished', todo_origin.is_finished)
        )
        self.todos[todo_id] = updated_todo
        return updated_todo

    async def delete(self, todo_id: str) -> Todo:
        """删除 Todo
        
        Args:
            todo_id: 待删除的 Todo ID
            
        Returns:
            Todo: 被删除的 Todo 对象
            
        Raises:
            TodoNotFoundException: 当指定 ID 的 Todo 不存在时
        """
        await asyncio.sleep(0.05)

        todo = self.todos.pop(todo_id, None)
        if not todo:
            raise TodoNotFoundException(todo_id=todo_id)
        return todo
