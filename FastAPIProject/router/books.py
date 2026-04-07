"""Book 路由模块

定义 Book API 的 HTTP 端点与请求处理
"""

from fastapi import APIRouter, Query, Path, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from common.response import success_response
from common.status_codes import BusinessCode
from db.db_config import async_session
from models.book import Book
from service.books import book_service

# 创建路由对象
books_router = APIRouter()


async def get_session() -> AsyncSession:
    """数据库会话依赖注入
    
    每次请求创建一个新 Session，请求结束后自动关闭
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@books_router.get('/books/', response_model=list[Book])
async def get_books(
        skip: int = Query(default=0, ge=0, description="跳过记录数"),
        limit: int = Query(default=10, ge=1, le=100, description="返回记录上限"),
        session: AsyncSession = Depends(get_session)
):
    """获取图书列表（支持分页查询）
    
    Args:
        skip: 跳过记录数，默认从第一条开始
        limit: 返回记录上限，默认最多 10 条
        session: 数据库会话（依赖注入）
        
    Returns:
        标准化的成功响应，包含图书列表
    """
    books = await book_service.get_all(session, skip=skip, limit=limit)
    return success_response(data=books, message='查询成功')


@books_router.get('/books/{id}', response_model=Book)
async def get_book(
        id: int = Path(..., gt=0, description="图书唯一标识符"),
        session: AsyncSession = Depends(get_session)
):
    """获取单本图书详情
    
    Args:
        id: 图书唯一标识符
        session: 数据库会话（依赖注入）
        
    Returns:
        标准化的成功响应，包含图书对象
        
    Raises:
        HTTPException: 当指定 ID 的图书不存在时（404）
    """
    book = await book_service.get_by_id(session, book_id=id)
    if not book:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"ID 为 {id} 的图书不存在")
    return success_response(data=book, message='查询成功')


@books_router.post('/books/', response_model=Book, status_code=201)
async def create_book(
        book_create: Book = Body(
            ...,
            json_schema_extra={
                "examples": [{
                    "title": "FastAPI 实战指南",
                    "author": "张三",
                    "price": 88.0,
                    "description": "一本关于 FastAPI 的实战教程"
                }]
            }
        ),
        session: AsyncSession = Depends(get_session)
):
    """创建新的图书记录
    
    Args:
        book_create: 创建请求，包含书名、作者、价格、描述（id 由数据库自增）
        session: 数据库会话（依赖注入）
        
    Returns:
        标准化的成功响应，包含新创建的图书对象（含自增 ID）
    """
    new_book = await book_service.create(session, new_book=book_create)
    return success_response(data=new_book, message='添加成功', code=BusinessCode.CREATED)


@books_router.put('/books/{id}', response_model=Book)
async def update_book(
        id: int = Path(..., gt=0, description="待更新的图书 ID"),
        update_data: dict = Body(
            ...,
            json_schema_extra={
                "examples": [{
                    "title": "修改后的书名",
                    "price": 99.0
                }]
            }
        ),
        session: AsyncSession = Depends(get_session)
):
    """更新图书信息（支持部分更新）
    
    Args:
        id: 待更新的图书 ID
        update_data: 需要更新的字段字典（如 {"title": "新书名", "price": 99.0}）
        session: 数据库会话（依赖注入）
        
    Returns:
        标准化的成功响应，包含更新后的图书对象
        
    Raises:
        HTTPException: 当指定 ID 的图书不存在时（404）
    """
    updated_book = await book_service.update(session, book_id=id, update_data=update_data)
    if not updated_book:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"ID 为 {id} 的图书不存在")
    return success_response(data=updated_book, message='修改成功')


@books_router.delete('/books/{id}', response_model=Book)
async def delete_book(
        id: int = Path(..., gt=0, description="待删除的图书 ID"),
        session: AsyncSession = Depends(get_session)
):
    """删除指定图书
    
    Args:
        id: 待删除的图书 ID
        session: 数据库会话（依赖注入）
        
    Returns:
        标准化的成功响应，包含被删除的图书对象
        
    Raises:
        HTTPException: 当指定 ID 的图书不存在时（404）
    """
    deleted_book = await book_service.delete(session, book_id=id)
    if not deleted_book:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"ID 为 {id} 的图书不存在")
    return success_response(data=deleted_book, message='删除成功')
