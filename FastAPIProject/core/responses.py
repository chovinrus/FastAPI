"""统一响应模块

提供标准化的 HTTP 响应格式与响应体构建函数
"""

from typing import Generic, TypeVar, Any, Optional

from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.status_codes import BusinessCode, BUSINESS_CODE_MESSAGES, to_http_status

T = TypeVar('T')


class ResponseBody(BaseModel, Generic[T]):
    """标准化响应体模型
    
    Attributes:
        code: 业务状态码，200 表示成功，其他表示各类错误
        message: 响应消息，描述操作结果或错误原因
        data: 响应数据载体，支持任意类型，可选
    """
    code: int
    message: str
    data: Optional[T] = None
    
    class Config:
        from_attributes = True


def _get_http_status(code: BusinessCode) -> int:
    """将业务状态码转换为 HTTP 状态码（内部代理）"""
    return to_http_status(code)


def success_response(
    data: Any = None,
    message: str = '操作成功',
    code: BusinessCode = BusinessCode.SUCCESS
) -> JSONResponse:
    """构建成功响应
    
    Args:
        data: 响应数据，可选
        message: 成功消息，默认'操作成功'
        code: 业务状态码，默认 SUCCESS(200)
        
    Returns:
        JSONResponse: 标准化的 JSON 响应
    """
    response_body = ResponseBody(code=code, message=message, data=data)
    return JSONResponse(
        content=response_body.model_dump(mode='json'),
        status_code=200
    )


def error_response(
    code: BusinessCode,
    message: Optional[str] = None,
    data: Any = None
) -> JSONResponse:
    """构建错误响应
    
    Args:
        code: 业务状态码
        message: 错误消息，不传则使用默认消息
        data: 附加数据
        
    Returns:
        JSONResponse: 标准化的错误响应
    """
    from core.status_codes import BUSINESS_CODE_MESSAGES
    
    msg = message or BUSINESS_CODE_MESSAGES.get(code, '未知错误')
    response_body = ResponseBody(code=code, message=msg, data=data)
    http_status = to_http_status(code)
    return JSONResponse(
        content=response_body.model_dump(mode='json'),
        status_code=http_status
    )
