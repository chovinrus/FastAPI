"""业务状态码模块

定义业务状态码枚举、消息映射表与 HTTP 状态码转换逻辑
"""

from enum import IntEnum


class BusinessCode(IntEnum):
    """业务状态码枚举
    
    状态码规范：
    - 2xx: 成功
    - 4xxxx: 客户端错误
    - 5xxxx: 服务端错误
    """
    # 成功状态码
    SUCCESS = 200
    CREATED = 201
    NO_CONTENT = 204

    # 客户端错误 (4xxxx)
    BAD_REQUEST = 40000
    VALIDATION_ERROR = 40001
    NOT_FOUND = 40400
    UNAUTHORIZED = 40100
    FORBIDDEN = 40300
    CONFLICT = 40900

    # 服务端错误 (5xxxx)
    INTERNAL_ERROR = 50000
    DATABASE_ERROR = 50001
    SERVICE_UNAVAILABLE = 50300


# 业务状态码消息映射表
BUSINESS_CODE_MESSAGES: dict[BusinessCode, str] = {
    BusinessCode.SUCCESS: '操作成功',
    BusinessCode.CREATED: '创建成功',
    BusinessCode.NO_CONTENT: '无内容',
    BusinessCode.BAD_REQUEST: '请求参数错误',
    BusinessCode.VALIDATION_ERROR: '参数验证失败',
    BusinessCode.NOT_FOUND: '资源不存在',
    BusinessCode.UNAUTHORIZED: '未授权访问',
    BusinessCode.FORBIDDEN: '禁止访问',
    BusinessCode.CONFLICT: '资源冲突',
    BusinessCode.INTERNAL_ERROR: '服务器内部错误',
    BusinessCode.DATABASE_ERROR: '数据库操作失败',
    BusinessCode.SERVICE_UNAVAILABLE: '服务暂时不可用',
}


def to_http_status(code: BusinessCode) -> int:
    """将业务状态码转换为 HTTP 状态码
    
    Args:
        code: 业务状态码
        
    Returns:
        int: 对应的 HTTP 状态码
    """
    if code < 300:
        return 200
    elif 40000 <= code < 41000:
        return 400
    elif 40100 <= code < 40200:
        return 401
    elif 40300 <= code < 40400:
        return 403
    elif 40400 <= code < 40500:
        return 404
    elif 40900 <= code < 41000:
        return 409
    else:
        return 500
