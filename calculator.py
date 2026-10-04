import ast
import operator


# 允许使用的二元运算符
BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


# 允许使用的一元运算符
UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def calculate_expression(expression: str):
    """
    安全计算数学表达式。

    支持：
    + - * /
    括号
    小数
    正负号

    不使用 eval。
    """

    # 表达式不能为空
    if not expression:
        raise ValueError("表达式不能为空")

    # 防止输入特别长的内容
    if len(expression) > 200:
        raise ValueError("表达式过长")

    try:
        # 把字符串解析成 AST
        tree = ast.parse(
            expression,
            mode="eval"
        )

    except SyntaxError:
        raise ValueError("表达式格式错误")

    try:
        # 开始计算表达式
        result = evaluate_node(tree.body)

    except ZeroDivisionError:
        raise ValueError("除数不能为 0")

    # 防止计算结果特别大
    if isinstance(result, (int, float)):
        if abs(result) > 1e100:
            raise ValueError("计算结果过大")

    return result


def evaluate_node(node):
    """
    递归计算 AST 中的数学表达式。
    """

    # -----------------------------
    # 数字
    # -----------------------------

    if isinstance(node, ast.Constant):

        # Python 中 bool 也属于 int，
        # 所以这里单独禁止 True / False
        if isinstance(node.value, bool):
            raise ValueError("不支持该表达式")

        if isinstance(node.value, (int, float)):
            return node.value

        raise ValueError("只允许输入数字")

    # -----------------------------
    # 二元运算
    # 例如：1 + 2、3 * 4
    # -----------------------------

    if isinstance(node, ast.BinOp):

        operator_type = type(node.op)

        # 检查是不是允许的运算符
        if operator_type not in BINARY_OPERATORS:
            raise ValueError("包含不支持的运算符")

        # 分别计算左右两边
        left_value = evaluate_node(node.left)
        right_value = evaluate_node(node.right)

        # 找到对应的计算方法
        operation = BINARY_OPERATORS[operator_type]

        return operation(left_value, right_value)

    # -----------------------------
    # 一元运算
    # 例如：-5、+5
    # -----------------------------

    if isinstance(node, ast.UnaryOp):

        operator_type = type(node.op)

        if operator_type not in UNARY_OPERATORS:
            raise ValueError("包含不支持的运算符")

        value = evaluate_node(node.operand)

        operation = UNARY_OPERATORS[operator_type]

        return operation(value)

    # 除了上面的内容，其他全部拒绝
    raise ValueError("表达式包含不允许的内容")