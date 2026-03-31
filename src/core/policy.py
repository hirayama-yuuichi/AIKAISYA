"""
AIKAISYA — 共通方針ローダー
config/policy.yaml を読み込み、各エージェントに渡す
"""
from pathlib import Path
import yaml


_POLICY_PATH = Path(__file__).parent.parent.parent / "config" / "policy.yaml"


def load_policy() -> dict:
    """共通方針をYAMLから読み込む"""
    with open(_POLICY_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_system_instruction(department_name: str, mission: str) -> str:
    """
    各エージェントに渡す System Instruction を生成する

    Layer A: 固有ミッション
    Layer B: 共通方針（policy.yaml から生成）
    """
    policy = load_policy()
    api = policy["api"]
    cost = policy["cost"]
    agent = policy["agent"]

    return f"""
あなたは「{department_name}」です。

【Layer A: 固有ミッション】
{mission}

【Layer B: 共通方針（全部門共通ルール）】
- API認証方式: {api["auth"]["method"]}
- 命名規則: フィールド={api["naming"]["style"]}, エンドポイント={api["naming"]["endpoint_style"]}
- ドキュメント形式: {api["documentation"]["format"]}（{api["documentation"]["language"]}で記述）
- セキュリティ: HTTPS必須、レート制限 {api["security"]["rate_limit_per_minute"]}回/分
- コスト: 1実行あたり上限 {cost["llm"]["alert_threshold_jpy"]}円、最大リクエスト数 {cost["llm"]["max_requests_per_run"]}回
- 利益率: 最低 {cost["profit_margin_min_percent"]}% を確保

【出力ルール】
必ず以下のフィールドを含めること:
- department_name: 部門名
- trend_check: トレンド確認係の所見（summary, is_modern）
- cost_check: API使用量確認係の所見（estimated_tokens, within_budget, notes）
- result: 本来の出力
- judgment: {agent["judgment"]["pass_label"]} / {agent["judgment"]["hold_label"]} / {agent["judgment"]["fail_label"]} のいずれか
""".strip()
