import sqlite3
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from calculator import calculate_expression


# 创建 FastAPI 应用
app = FastAPI(title="Calculator API")


# 允许前端访问后端
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# SQLite 数据库文件
DATABASE_NAME = "calculator.db"


def get_database():
    """连接数据库。"""
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    """如果数据库表不存在，就自动创建。"""
    connection = get_database()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expression TEXT NOT NULL,
            result TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


# 启动程序时创建数据库
create_database()


# 前端发送过来的数据格式
class CalculationRequest(BaseModel):
    expression: str


# 测试后端是否正常运行
@app.get("/")
def root():
    return {
        "message": "Calculator backend is running"
    }


# 计算接口
@app.post("/api/calculate")
def calculate(request: CalculationRequest):
    expression = request.expression.strip()

    if expression == "":
        raise HTTPException(
            status_code=400,
            detail="表达式不能为空"
        )

    try:
        # 真正的数学计算在 calculator.py 中进行
        calculation_result = calculate_expression(expression)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    # 获取当前时间
    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # 把成功的计算保存到数据库
    connection = get_database()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO history (expression, result, created_at)
        VALUES (?, ?, ?)
        """,
        (
            expression,
            str(calculation_result),
            created_at
        )
    )

    connection.commit()
    connection.close()

    # 把计算结果返回给前端
    return {
        "success": True,
        "expression": expression,
        "result": calculation_result
    }


# 获取全部历史记录
@app.get("/api/history")
def get_history():
    connection = get_database()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, expression, result, created_at
        FROM history
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()
    connection.close()

    history = []

    for row in rows:
        history.append(
            {
                "id": row["id"],
                "expression": row["expression"],
                "result": row["result"],
                "created_at": row["created_at"]
            }
        )

    return history


# 删除指定的一条历史记录
@app.delete("/api/history/{history_id}")
def delete_history(history_id: int):
    connection = get_database()
    cursor = connection.cursor()

    # 先查询这条记录是否存在
    cursor.execute(
        """
        SELECT id
        FROM history
        WHERE id = ?
        """,
        (history_id,)
    )

    record = cursor.fetchone()

    if record is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="历史记录不存在"
        )

    # 删除指定记录
    cursor.execute(
        """
        DELETE FROM history
        WHERE id = ?
        """,
        (history_id,)
    )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "删除成功"
    }