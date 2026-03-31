"""
AIKAISYA — メインエントリーポイント
お試し版：ドキュメント作成部門 → 製造工程分解部門 の2部門連携
"""
from src.core.state import ProjectState
from src.agents import document_agent, decompose_agent, manage_agent


def run(request: str) -> ProjectState:
    """3部門を順番に実行する（お試し版完成形）"""
    state: ProjectState = {
        "request": request,
        "document_output": None,
        "decompose_output": None,
        "manage_output": None,
        "final_judgment": None,
        "final_summary": None,
    }

    # 部門1：ドキュメント作成
    state = document_agent.run(state)
    if state["document_output"]["judgment"] == "却下":
        print("\n[総合判定] ドキュメント作成部門で却下。処理を停止します。")
        state["final_judgment"] = "却下"
        return state

    # 部門2：製造工程分解
    state = decompose_agent.run(state)
    if state["decompose_output"]["judgment"] == "却下":
        print("\n[総合判定] 製造工程分解部門で却下。処理を停止します。")
        state["final_judgment"] = "却下"
        return state

    # 部門3：製造工程管理
    state = manage_agent.run(state)

    # 最終判定
    judgments = [
        state["document_output"]["judgment"],
        state["decompose_output"]["judgment"],
        state["manage_output"]["judgment"],
    ]
    final = "承認" if all(j == "承認" for j in judgments) else "再調整"
    state["final_judgment"] = final

    print(f"\n{'='*50}")
    print("[お試し版 完了] 3部門の連携処理が終わりました")
    print(f"  ドキュメント作成部門: {judgments[0]}")
    print(f"  製造工程分解部門:     {judgments[1]}")
    print(f"  製造工程管理部門:     {judgments[2]}")
    print(f"  ▶ 最終判定:          {final}")
    print(f"{'='*50}")

    return state


if __name__ == "__main__":
    run("ユーザー管理API。ユーザーの登録・取得・更新・削除ができること。")
