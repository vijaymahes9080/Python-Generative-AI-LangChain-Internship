"""
Restricted AST-based Mathematical Calculator Tool for Task 3: Autonomous Agent.
Evaluates mathematical expressions strictly using abstract syntax tree (AST) traversal.
Zero eval(), zero exec(), zero arbitrary code execution vulnerabilities.
"""

import ast
import math
import operator
from typing import Dict, Any, Union
from pydantic import BaseModel, Field


class CalculatorInput(BaseModel):
    expression: str = Field(
        ...,
        description="Mathematical expression to evaluate (e.g. '1450 * 2 + sqrt(144)' or '(5200 - 1800) / 4')",
    )


class SafeCalculator:
    """Evaluates mathematical AST trees with strict node and function whitelisting."""

    # Allowed binary operators
    _BINARY_OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    # Allowed unary operators
    _UNARY_OPS = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    # Allowed mathematical functions and constants
    _MATH_FUNCS = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "abs": abs,
        "round": round,
        "floor": math.floor,
        "ceil": math.ceil,
        "pow": pow,
    }

    _MATH_CONSTS = {
        "pi": math.pi,
        "e": math.e,
    }

    @classmethod
    def _eval_node(cls, node: ast.AST) -> Union[int, float]:
        if isinstance(node, ast.Expression):
            return cls._eval_node(node.body)

        elif isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value).__name__}")

        elif isinstance(node, ast.BinOp):
            left = cls._eval_node(node.left)
            right = cls._eval_node(node.right)
            op_type = type(node.op)
            if op_type in cls._BINARY_OPS:
                # Guard against exponent blowup
                if op_type is ast.Pow and (right > 100 or left > 1000):
                    raise ValueError("Exponent or base exceeds safe calculation bounds.")
                try:
                    return cls._BINARY_OPS[op_type](left, right)
                except ZeroDivisionError:
                    raise ValueError("Division by zero is undefined.")
            raise ValueError(f"Unsupported binary operator: {op_type.__name__}")

        elif isinstance(node, ast.UnaryOp):
            operand = cls._eval_node(node.operand)
            op_type = type(node.op)
            if op_type in cls._UNARY_OPS:
                return cls._UNARY_OPS[op_type](operand)
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in cls._MATH_FUNCS:
                    args = [cls._eval_node(arg) for arg in node.args]
                    return cls._MATH_FUNCS[func_name](*args)
                raise ValueError(f"Forbidden or undefined function call: '{func_name}'")
            raise ValueError("Direct function expression calls are not permitted.")

        elif isinstance(node, ast.Name):
            if node.id in cls._MATH_CONSTS:
                return cls._MATH_CONSTS[node.id]
            raise ValueError(f"Forbidden or undefined variable: '{node.id}'")

        raise ValueError(f"Security restriction: AST node '{type(node).__name__}' is strictly disallowed.")

    @classmethod
    def calculate(cls, expression: str) -> str:
        """
        Safely parse and evaluate mathematical expression.
        
        Args:
            expression: Arithmetic expression string.
            
        Returns:
            Calculated result string or error diagnostic.
        """
        if not expression or not expression.strip():
            return "Error: Empty calculation expression."

        # Sanitize common punctuation
        clean_expr = expression.strip().rstrip("=").strip()

        try:
            tree = ast.parse(clean_expr, mode="eval")
            result = cls._eval_node(tree)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return str(round(result, 6) if isinstance(result, float) else result)
        except Exception as e:
            return f"Calculation Error: {str(e)}"


def run_calculator(expression: str) -> str:
    """Wrapper function conforming to agent tool signature."""
    return SafeCalculator.calculate(expression)
