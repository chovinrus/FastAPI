"""简易计算器 API

提供加减乘除四则运算的 RESTful 接口
"""
from enum import Enum
from typing import TypeVar, Generic

from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel, Field, model_validator
from starlette.requests import Request
from starlette.responses import JSONResponse

app = FastAPI(
    title="简易计算器 API",
    version="1.0.0",
    description="提供加减乘除四则运算的 RESTful 接口",
)


class Operation(str, Enum):
    """支持的运算类型枚举"""
    add = "+"
    subtract = "-"
    multiply = "*"
    divide = "/"


class CalcRequest(BaseModel):
    """计算器请求模型
    
    Attributes:
        a: 第一个操作数
        b: 第二个操作数（除法时不能为 0）
        op: 运算类型（加、减、乘、除）
    """
    a: float = Field(..., description="第一个操作数", examples=[10.5])
    b: float = Field(..., description="第二个操作数（除法时不能为 0）", examples=[2.0])
    op: Operation = Field(..., description="运算类型")

    model_config = {
        "json_schema_extra": {
            "example": {
                "a": 10.0,
                "b": 5.0,
                "op": "+"
            }
        }
    }

    @model_validator(mode="after")
    def validate_division_by_zero(self) -> "CalcRequest":
        """验证除法运算时除数不能为 0"""
        if self.op == Operation.divide and self.b == 0:
            raise HTTPException(status_code=400, detail="除数不能为 0")
        return self


T = TypeVar('T')


class StandardResponse(BaseModel, Generic[T]):
    code: int = Field(200, description="HTTP 状态码")
    message: str = Field("操作成功", description="响应消息")
    data: T | None = Field(None, description="响应数据")


def success_response(data: T | None = None) -> JSONResponse:
    """构建成功响应

    Args:
        data: 响应数据，可选

    Returns:
        StandardResponse: 标准化的成功响应
    """
    return JSONResponse(StandardResponse(code=200, message="运算成功", data=data).model_dump(mode="json"))


def error_response(message: str, code: int = 400, data: any = None) -> JSONResponse:
    """构建错误响应

    Args:
        message: 错误消息

    Returns:
        StandardResponse: 标准化的错误响应
    """
    return JSONResponse(
        status_code=code,
        content=StandardResponse(code=code, message=message, data=data).model_dump(mode="json")
    )


@app.exception_handler(HTTPException)
async def global_exception_handler(request: Request, http_exception: HTTPException) -> JSONResponse:
    """全局异常处理器

    Args:
        request: 请求对象
        http_exception: 异常对象

    Returns:
        StandardResponse: 标准化的错误响应
    """
    return error_response(http_exception.detail)


@app.post(
    "/calculate",
    summary="执行计算",
    description="根据提供的操作数和运算符执行四则运算",
    tags=["计算器"],
    response_model=StandardResponse[float]
)
async def calculate(request: CalcRequest = Body(..., description="计算请求参数")) -> JSONResponse:
    """执行四则运算
    
    Args:
        request: 计算请求，包含操作数 a、b 和运算符 op
        
    Returns:
        json_response: 计算结果
    """
    # 使用字典映射替代冗长的 if/else
    operation_map = {
        Operation.add: lambda x, y: x + y,
        Operation.subtract: lambda x, y: x - y,
        Operation.multiply: lambda x, y: x * y,
        Operation.divide: lambda x, y: x / y
    }

    calc_func = operation_map[request.op]
    result = calc_func(request.a, request.b)

    return success_response(result)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
