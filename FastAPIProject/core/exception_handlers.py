"""全局异常处理模块

负责统一拦截和处理应用中的各类异常，返回标准化响应
"""

import traceback

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from core.status_codes import BusinessCode
from core.exceptions import BusinessException
from core.responses import error_response


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器
    
    处理优先级：
    1. 业务异常 (BusinessException)
    2. Pydantic 验证错误 (ValidationError)
    3. FastAPI 请求验证错误 (RequestValidationError)
    4. 其他未捕获异常
    
    Args:
        request: FastAPI 请求对象
        exc: 异常实例
        
    Returns:
        JSONResponse: 标准化的错误响应
    """
    # 业务异常
    if isinstance(exc, BusinessException):
        return error_response(code=exc.code, message=exc.message, data=exc.data)
    
    # Pydantic 验证错误
    if isinstance(exc, ValidationError):
        return error_response(
            code=BusinessCode.VALIDATION_ERROR,
            message='数据验证失败',
            data={'errors': exc.errors()}
        )
    
    # FastAPI 请求验证错误
    if isinstance(exc, RequestValidationError):
        return error_response(
            code=BusinessCode.VALIDATION_ERROR,
            message='请求参数验证失败',
            data={'errors': exc.errors()}
        )
    
    # 其他未捕获的异常（生产环境应该记录日志）
    print(f"[ERROR] Unhandled exception: {type(exc).__name__}: {str(exc)}")
    print(traceback.format_exc())
    
    return error_response(
        code=BusinessCode.INTERNAL_ERROR,
        message='服务器内部错误',
        data={'detail': str(exc)} if str(exc) else None
    )
