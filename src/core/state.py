"""
AIKAISYA — 共有Stateオブジェクト
部門間で受け渡されるデータ構造を定義する
"""
from typing import TypedDict, Optional


class TrendCheck(TypedDict):
    """トレンド確認係の所見"""
    summary: str          # トレンドの要約
    is_modern: bool       # 現在のトレンドに合っているか


class CostCheck(TypedDict):
    """API使用量確認係の所見"""
    estimated_tokens: int     # 推定トークン数
    within_budget: bool       # 予算内か
    notes: str                # 備考


class DepartmentOutput(TypedDict):
    """各部門の出力の共通フォーマット"""
    department_name: str      # 部門名
    trend_check: TrendCheck   # トレンド確認係の所見
    cost_check: CostCheck     # API使用量確認係の所見
    result: str               # 本来の出力（仕様書・タスクリスト等）
    judgment: str             # 承認 / 再調整 / 却下


class ProjectState(TypedDict):
    """
    プロジェクト全体の状態
    LangGraphのノード間で受け渡されるState
    """
    # 入力
    request: str                          # 最初のAPI作成依頼

    # 各部門の出力（順番に積み上がる）
    document_output: Optional[DepartmentOutput]    # ドキュメント作成部門
    decompose_output: Optional[DepartmentOutput]   # 製造工程分解部門
    manage_output: Optional[DepartmentOutput]      # 製造工程管理部門

    # 最終判定
    final_judgment: Optional[str]         # 承認 / 再調整 / 却下
    final_summary: Optional[str]          # 最終サマリー
