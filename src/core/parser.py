"""
AIKAISYA — JSONパーサーユーティリティ
LLMの出力から各フィールドをロバストに抽出する
"""
import re
import json


def extract_field(text: str, field: str) -> str:
    """正規表現で特定フィールドの値を抽出する"""
    pattern = rf'"{field}"\s*:\s*"((?:[^"\\]|\\.)*)\"'
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1) if match else ""


def extract_bool(text: str, field: str) -> bool:
    """boolフィールドを抽出する"""
    pattern = rf'"{field}"\s*:\s*(true|false)'
    match = re.search(pattern, text)
    return match.group(1) == "true" if match else True


def extract_int(text: str, field: str) -> int:
    """intフィールドを抽出する"""
    pattern = rf'"{field}"\s*:\s*(\d+)'
    match = re.search(pattern, text)
    return int(match.group(1)) if match else 0


def parse_department_output(raw_text: str, department_name: str) -> dict:
    """
    LLMの出力からDepartmentOutputを抽出する。
    JSON全体のパースを試み、失敗した場合は正規表現でフィールドを個別抽出する。
    """
    # まずJSON全体のパースを試みる
    start = raw_text.find("{")
    end = raw_text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(raw_text[start:end])
        except json.JSONDecodeError:
            pass

    # フォールバック：正規表現で個別抽出
    return {
        "department_name": department_name,
        "trend_check": {
            "summary": extract_field(raw_text, "summary"),
            "is_modern": extract_bool(raw_text, "is_modern"),
        },
        "cost_check": {
            "estimated_tokens": extract_int(raw_text, "estimated_tokens"),
            "within_budget": extract_bool(raw_text, "within_budget"),
            "notes": extract_field(raw_text, "notes"),
        },
        "result": extract_field(raw_text, "result").replace("\\n", "\n"),
        "judgment": extract_field(raw_text, "judgment") or "承認",
    }
