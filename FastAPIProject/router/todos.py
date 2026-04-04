"""Todo 路由模块

定义 Todo API 的 HTTP 端点与请求处理
"""

from fastapi import APIRouter, Query, Path, Body

from core.status_codes import BusinessCode
from core.responses import success_response
from models import TodoCreate, Todo, TodoUpdate
from services import todo_service

# 创建路由对象
router = APIRouter()


@router.get('/todos/', response_model=list[Todo])
async def get_todos(
    skip: int = Query(default=0, ge=0, description="跳过记录数"),
    limit: int = Query(default=10, ge=1, le=100, description="返回记录上限")
):
    """获取 Todo 列表（支持分页查询）
    
    Args:
        skip: 跳过记录数，默认从第一条开始
        limit: 返回记录上限，默认最多 10 条
        
    Returns:
        标准化的成功响应，包含 Todo 列表
    """
    todos = await todo_service.get_all(skip=skip, limit=limit)
    return success_response(data=todos, message='查询成功')


@router.get('/todos/{id}', response_model=Todo)
async def get_todo(
    id: str = Path(..., min_length=1, description="Todo 唯一标识符")
):
    """获取单个 Todo 详情
    
    Args:
        id: Todo 唯一标识符
        
    Returns:
        标准化的成功响应，包含 Todo 对象
        
    Raises:
        TodoNotFoundException: 当指定 ID 的 Todo 不存在时
    """
    todo = await todo_service.get_by_id(id)
    return success_response(data=todo, message='查询成功')


@router.put('/todos/{id}', response_model=Todo)
async def update_todo(
    id: str = Path(..., min_length=1, description="待更新的 Todo ID"),
    todo_update: TodoUpdate = Body(
        None,
        example={
            "task": "修改后的任务描述",
            "priority": 4,
            "is_finished": True
        }
    )
):
    """更新 Todo 信息（支持部分更新）
    
    Args:
        id: 待更新的 Todo ID
        todo_update: 更新内容，所有字段可选
        
    Returns:
        标准化的成功响应，包含更新后的 Todo 对象
        
    Raises:
        TodoNotFoundException: 当指定 ID 的 Todo 不存在时
    """
    updated_todo = await todo_service.update(id, todo_update)
    return success_response(data=updated_todo, message='修改成功')


@router.delete('/todos/{id}', response_model=Todo)
async def delete_todo(
    id: str = Path(..., min_length=1, description="待删除的 Todo ID")
):
    """删除 Todo
    
    Args:
        id: 待删除的 Todo ID
        
    Returns:
        标准化的成功响应，包含被删除的 Todo 对象
        
    Raises:
        TodoNotFoundException: 当指定 ID 的 Todo 不存在时
    """
    deleted_todo = await todo_service.delete(id)
    return success_response(data=deleted_todo, message='删除成功')


@router.post('/todos/', response_model=Todo, status_code=201)
async def create_todo(
    todo_create: TodoCreate = Body(
        ...,
        example={
            "task": "完成项目文档",
            "deadline": "2026-12-31T23:59:59",
            "assigned_to": "张三",
            "priority": 3
        }
    )
):
    """创建新的 Todo
    
    Args:
        todo_create: 创建请求，包含任务、截止时间、负责人、优先级
        
    Returns:
        标准化的成功响应，包含新创建的 Todo 对象
    """
    new_todo = await todo_service.create(todo_create)
    return success_response(data=new_todo, message='添加成功', code=BusinessCode.CREATED)
