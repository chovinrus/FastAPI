from pprint import pprint

import pytest

from db.db_config import init_db, async_session
from models import Book
from service import book_service


@pytest.mark.asyncio
async def test_database_initialization():
    """
    测试数据库表结构初始化
    运行此测试将自动在数据库中创建所有定义的表
    """
    await init_db()
    print("✅ 数据库表结构初始化成功！")


# 测试新增图书
@pytest.mark.asyncio
async def test_create_book():
    async with async_session() as session:
        new_book = await book_service.create(session, new_book=Book(title="测试图书", author="测试作者", price=29.9))
        pprint(new_book)
        assert new_book.id is not None #布尔表达式



# 测试查询图书列表
@pytest.mark.asyncio
async def test_get_books():
    async with async_session() as session:
        books = await book_service.get_all(session, skip=0, limit=10)
        pprint(books)
        assert len(books) > 0


# 测试查询单个图书
@pytest.mark.asyncio
async def test_get_book_by_id():
    async with async_session() as session:
        # 注意：请确保 ID=1 的图书存在，或者替换为实际存在的 ID
        book = await book_service.get_by_id(session, book_id=1)
        pprint(book)
        assert book is not None
        assert book.title == "测试图书"


# 测试更新图书
@pytest.mark.asyncio
async def test_update_book():
    async with async_session() as session:
        updated_book = await book_service.update(session, book_id=1,
                                                 update_data={"price": 39.9, "description": "更新后的描述"})
        pprint(updated_book)
        assert updated_book is not None
        assert updated_book.price == 39.9


# 测试删除图书
@pytest.mark.asyncio
async def test_delete_book():
    async with async_session() as session:
        deleted_book = await book_service.delete(session, book_id=1)
        pprint(deleted_book)
        assert deleted_book is not None
        # 验证删除后查不到
        book = await book_service.get_by_id(session, book_id=1)
        assert book is None


# 测试查询图书列表
@pytest.mark.asyncio
async def test_get_books():
    async with async_session() as session:
        books = await book_service.get_all(session, skip=0, limit=10)
        pprint(books)
        assert len(books) > 0


# 测试查询单个图书
@pytest.mark.asyncio
async def test_get_book_by_id():
    async with async_session() as session:
        # 假设 ID 为 1 的书存在（根据实际数据库情况调整）
        book = await book_service.get_by_id(session, book_id=1)
        pprint(book)
        if book:
            assert book.title == "测试图书"


# 测试更新图书
@pytest.mark.asyncio
async def test_update_book():
    async with async_session() as session:
        updated_book = await book_service.update(session, book_id=3,
                                                 update_data={"price": 39.9, "description": "更新后的描述"})
        pprint(updated_book)
        assert updated_book is not None
        assert updated_book.price == 39.9


# 测试删除图书
@pytest.mark.asyncio
async def test_delete_book():
    async with async_session() as session:
        deleted_book = await book_service.delete(session, book_id=3)
        pprint(deleted_book)
        assert deleted_book is not None
        # 验证删除后查不到
        book = await book_service.get_by_id(session, book_id=3)
        assert book is None
