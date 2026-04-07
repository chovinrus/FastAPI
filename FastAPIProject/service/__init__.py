"""服务层模块

提供业务逻辑处理与数据访问服务
"""

from service.books import BookService
from service.todos import TodoService

# 全局服务实例
todo_service = TodoService()
book_service = BookService()


def shutdown_services() -> None:
    """应用关闭时释放资源

    在 FastAPI 应用停止时自动调用
    """
    pass


__all__ = ['TodoService', 'todo_service', 'BookService', 'book_service', 'shutdown_services']
