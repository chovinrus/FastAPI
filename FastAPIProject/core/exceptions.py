"""异常处理模块

定义业务异常类，提供统一的异常处理机制
"""

from typing import Any, Optional

from core.status_codes import BusinessCode, BUSINESS_CODE_MESSAGES


class BusinessException(Exception):
    """业务异常基类
    
    用于封装业务规则验证失败的场景，区别于基础格式验证
    
    Attributes:
        code: 业务状态码
        message: 错误消息
        data: 附加数据
    """
    def __init__(self, code: BusinessCode, message: Optional[str] = None, data: Any = None):
        self.code = code
        self.message = message or BUSINESS_CODE_MESSAGES.get(code, '未知错误')
        self.data = data
        super().__init__(self.message)


class ResourceNotFoundException(BusinessException):
    """资源不存在异常基类
    
    Attributes:
        resource_name: 资源名称
        identifier: 资源标识符
    """
    def __init__(self, resource_name: str, identifier: Optional[str] = None):
        message = f'{resource_name}不存在'
        if identifier:
            message = f'ID 为 {identifier} 的{resource_name}不存在'
        super().__init__(code=BusinessCode.NOT_FOUND, message=message)


class TodoNotFoundException(ResourceNotFoundException):
    """Todo 资源不存在异常"""
    def __init__(self, todo_id: Optional[str] = None):
        super().__init__(resource_name='Todo', identifier=todo_id)


class ValidationException(BusinessException):
    """参数验证异常
    
    用于封装业务层面的参数验证失败场景
    
    Attributes:
        message: 错误消息
        field: 验证失败的字段名
    """
    def __init__(self, message: str, field: Optional[str] = None):
        data = {'field': field} if field else None
        super().__init__(code=BusinessCode.VALIDATION_ERROR, message=message, data=data)


class UnauthorizedException(BusinessException):
    """未授权访问异常"""
    def __init__(self, message: str = '未授权访问'):
        super().__init__(code=BusinessCode.UNAUTHORIZED, message=message)


class ForbiddenException(BusinessException):
    """禁止访问异常"""
    def __init__(self, message: str = '禁止访问'):
        super().__init__(code=BusinessCode.FORBIDDEN, message=message)


class InternalErrorException(BusinessException):
    """服务器内部错误异常
    
    Attributes:
        message: 错误消息
        detail: 错误详情
    """
    def __init__(self, message: str = '服务器内部错误', detail: Optional[str] = None):
        data = {'detail': detail} if detail else None
        super().__init__(code=BusinessCode.INTERNAL_ERROR, message=message, data=data)
