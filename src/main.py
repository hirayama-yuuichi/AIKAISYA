"""
AIKAISYA — メインエントリーポイント
お試し版：ドキュメント作成部門 → 製造工程分解部門 の2部門連携
"""
from src.core.state import ProjectState
from src.agents import document_agent, decompose_agent


def run(request: str) -> ProjectState:
    """2部門を順番に実行する"""
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

    # 部門1が承認された場合のみ次へ
    if state["document_output"]["judgment"] == "却下":
        print("\n[総合判定] ドキュメント作成部門で却下。処理を停止します。")
        return state

    # 部門2：製造工程分解
    state = decompose_agent.run(state)

    # 最終サマリー
    print(f"\n{'='*50}")
    print("[完了] 2部門の連携処理が終わりました")
    print(f"  ドキュメント作成: {state['document_output']['judgment']}")
    print(f"  製造工程分解:     {state['decompose_output']['judgment']}")
    print(f"{'='*50}")

    return state


if __name__ == "__main__":
    run("ユーザー管理API。ユーザーの登録・取得・更新・削除ができること。")
