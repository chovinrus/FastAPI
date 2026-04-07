import asyncio
import sys

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

# # Windows 平台兼容性修复：必须在导入任何异步库之前设置
# if sys.platform == "win32":
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 数据库连接URL
# DATABASE_URL = "sqlite+aiosqlite:///db/books.db"  # SQLite
# "postgresql+asyncpg://user:pass@localhost/db"  # PostgreSQL
DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/db"  # MySQL

# 创建异步引擎(注意驱动必须是异步的)
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # 打印 SQL 语句(开发环境)
    pool_pre_ping=True,  # 连接健康检查
)

# 创建异步会话
async_session = async_sessionmaker(
    engine,  # 数据库引擎
    class_=AsyncSession,  # 指定会话类型为异步会话，必须与异步引擎匹配
    expire_on_commit=False  # 默认情况下，会话提交（commit）后，查询出来的对象会“过期”（无法再访问属性），设为FaLse后，提交后对象仍可正常使用（开发更友好）
)

# 确保模型被加载，否则 create_all 找不到表定义
from models.book import Book  # noqa: F401


# 初始化数据库表结构
async def init_db():
    # 通过异步引擎开启一个事务连接（engine.begin（）会自动管理事务，退出上下文时提交）
    async with engine.begin() as conn:
        # 如果需要重建表，可以先删除
        # await conn.run_sync(SQLModel.metadata.drop_all)
        # 创建所有表 (如果不存在)，把同步的create_all方法适配到异步连接中执行
        await conn.run_sync(SQLModel.metadata.create_all)

# if __name__ == '__main__':
#     async def main():
#         await init_db()
#         print("数据库表结构初始化完成！")
#         # 在同一个循环内显式释放引擎，避免 GC 在循环关闭后清理
#         await engine.dispose()
#     asyncio.run(main())

# pytest.mark.asyncio会创建一个可复用的事件循环（Event Loop）运行你的异步函数。等待函数执行完毕并处理结果。
# 为了提供快速测试，所有测试db创建和CRUD的代码都保存在test_db文件
