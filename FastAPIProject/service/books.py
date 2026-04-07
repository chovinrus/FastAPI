"""Book 业务服务模块
提供 Book 表的数据库 CRUD 操作封装
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from models.book import Book


class BookService:
    """Book 数据库操作服务类
    
    负责 Book 表的增删改查，所有方法均接收 AsyncSession 作为参数
    由路由层通过依赖注入提供 Session 实例
    """

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 10) -> list[Book]:
        """分页查询所有图书
        
        Args:
            db: 数据库会话
            skip: 跳过的记录数（用于分页）
            limit: 返回的最大记录数
            
        Returns:
            list[Book]: 图书列表
        """
        stmt = select(Book).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, book_id: int) -> Book | None:
        """根据 ID 查询单本图书
        
        Args:
            db: 数据库会话
            book_id: 图书唯一标识
            
        Returns:
            Book | None: 找到的图书对象，不存在则返回 None
        """
        stmt = select(Book).where(Book.id == book_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, new_book: Book) -> Book:
        """创建新图书记录
        
        Args:
            db: 数据库会话
            new_book: 待创建的图书对象（id 可为 None，由数据库自增）
            
        Returns:
            Book: 创建成功并刷新后的图书对象（包含自增 ID）
        """
        db.add(new_book)
        await db.commit()
        await db.refresh(new_book)  # 刷新对象，获取数据库生成的自增 ID
        return new_book

    async def update(self, db: AsyncSession, book_id: int, update_data: dict) -> Book | None:
        """部分更新图书信息
        
        Args:
            db: 数据库会话
            book_id: 待更新的图书 ID
            update_data: 需要更新的字段字典（如 {"title": "新书名", "price": 99.0}）
            
        Returns:
            Book | None: 更新后的图书对象，若图书不存在则返回 None
        """

        db_book = await self.get_by_id(db, book_id)
        if not db_book:
            return None

        # 动态更新字段
        for key, value in update_data.items():
            if hasattr(db_book, key):
                setattr(db_book, key, value)

        await db.commit()  # 刷新会话绑定的orm，更新表记录
        await db.refresh(db_book)
        return db_book

    async def delete(self, db: AsyncSession, book_id: int) -> Book | None:
        """删除指定图书
        
        Args:
            db: 数据库会话
            book_id: 待删除的图书 ID
            
        Returns:
            Book | None: 被删除的图书对象，若不存在则返回 None
        """
        db_book = await self.get_by_id(db, book_id)
        if not db_book:
            return None

        await db.delete(db_book)
        await db.commit()
        return db_book


# 全局服务单例
book_service = BookService()
