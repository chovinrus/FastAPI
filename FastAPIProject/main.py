"""FastAPI 应用主入口

应用启动与配置入口，负责初始化 FastAPI 实例、注册中间件与路由
"""

from fastapi import FastAPI

from common.exception_handlers import global_exception_handler
from router import books_router
from service import shutdown_services


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例

    Returns:
        FastAPI: 配置完成的应用实例
    """
    application = FastAPI(
        title="Todo API",
        description="待办事项管理系统",
        version="0.1.0"
    )

    # 注册全局异常处理器
    application.add_exception_handler(Exception, global_exception_handler)

    # 注册路由
    # application.include_router(todos_router)
    application.include_router(books_router)

    @application.on_event("shutdown")
    async def shutdown_application():
        """应用关闭事件处理器

        在应用停止时自动调用，用于释放资源
        """
        shutdown_services()

    return application


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(create_app(), host="0.0.0.0", port=8000)
