"""
AIKAISYA — メインエントリーポイント
お試し版：ドキュメント作成部門 → 製造工程分解部門 の2部門連携
"""
from src.core.state import ProjectState
from src.core.cost_tracker import CostReport
from src.agents import document_agent, decompose_agent, manage_agent, code_agent


def run(request: str) -> ProjectState:
    """お試し版：ドキュメント作成 → コード生成 + コストアラート表示"""
    state: ProjectState = {
        "request": request,
        "document_output": None,
        "decompose_output": None,
        "manage_output": None,
        "code_output": None,
        "final_judgment": None,
        "final_summary": None,
    }
    cost = CostReport()

    # 部門1：ドキュメント作成
    state = document_agent.run(state)
    cost.add("ドキュメント作成部門", state["document_output"]["cost_check"])
    if state["document_output"]["judgment"] == "却下":
        print("\n[総合判定] ドキュメント作成部門で却下。処理を停止します。")
        state["final_judgment"] = "却下"
        cost.display()
        return state

    # 部門2：コード生成
    state = code_agent.run(state)
    cost.add("コード生成部門", state["code_output"]["cost_check"])

    # 部門3：製造工程分解（参考情報として実行）
    state = decompose_agent.run(state)
    cost.add("製造工程分解部門", state["decompose_output"]["cost_check"])

    # 最終判定
    judgments = [
        state["document_output"]["judgment"],
        state["code_output"]["judgment"],
        state["decompose_output"]["judgment"],
    ]
    final = "承認" if all(j == "承認" for j in judgments) else "再調整"
    state["final_judgment"] = final

    print(f"\n{'='*50}")
    print("[お試し版 完了]")
    print(f"  ドキュメント作成部門: {judgments[0]}")
    print(f"  コード生成部門:       {judgments[1]}  → output/main_api.py に保存")
    print(f"  製造工程分解部門:     {judgments[2]}")
    print(f"  ▶ 最終判定:          {final}")
    print(f"{'='*50}")

    # コストレポート表示
    cost.display()

    return state


if __name__ == "__main__":
    run("ユーザー管理API。ユーザーの登録・取得・更新・削除ができること。")
