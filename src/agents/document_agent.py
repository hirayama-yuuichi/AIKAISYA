"""
AIKAISYA — ドキュメント作成部門
API仕様書（OpenAPI形式）のドラフトを生成する
"""
import json
import boto3
from pathlib import Path
from src.core.policy import get_system_instruction
from src.core.state import ProjectState, DepartmentOutput
from src.core.parser import parse_department_output


DEPARTMENT_NAME = "ドキュメント作成部門"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "output"
MISSION = """
あなたはAPI仕様書の作成を担当します。
入力されたAPI作成依頼を元に、OpenAPI 3.0形式の仕様書ドラフトをJSON形式で作成してください。
また、トレンド確認係としてこの設計が現在のトレンドに合っているか確認し、
API使用量確認係として想定リクエスト数とコストを見積もってください。
"""

MODEL_ID = "jp.anthropic.claude-haiku-4-5-20251001-v1:0"
REGION = "ap-northeast-1"


def run(state: ProjectState) -> ProjectState:
    """ドキュメント作成部門の処理"""
    print(f"\n{'='*50}")
    print(f"[{DEPARTMENT_NAME}] 開始")
    print(f"依頼内容: {state['request']}")
    print(f"{'='*50}")

    client = boto3.client("bedrock-runtime", region_name=REGION)
    system_instruction = get_system_instruction(DEPARTMENT_NAME, MISSION)

    prompt = f"""
以下のAPI作成依頼に対して、エンドポイント一覧と説明をまとめてください。

【依頼内容】
{state['request']}

必ず以下のJSON形式のみで回答してください（コードブロック不要）：
{{
  "department_name": "{DEPARTMENT_NAME}",
  "trend_check": {{
    "summary": "トレンドに関する所見を1文で",
    "is_modern": true
  }},
  "cost_check": {{
    "estimated_tokens": 500,
    "within_budget": true,
    "notes": "コストに関する所見を1文で"
  }},
  "result": "エンドポイント一覧をテキストで記述（改行は\\nで表現）",
  "judgment": "承認"
}}
"""

    response = client.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "system": system_instruction,
            "messages": [{"role": "user", "content": prompt}]
        })
    )

    body = json.loads(response["body"].read())
    raw_text = body["content"][0]["text"]
    output: DepartmentOutput = parse_department_output(raw_text, DEPARTMENT_NAME)

    # 仕様書をファイルに保存
    OUTPUT_DIR.mkdir(exist_ok=True)
    spec_text = output["result"].replace("\\n", "\n")
    (OUTPUT_DIR / "spec.md").write_text(
        f"# API仕様書\n\n依頼: {state['request']}\n\n{spec_text}",
        encoding="utf-8"
    )

    print(f"\n[トレンド確認係] {output['trend_check']['summary']}")
    print(f"[使用量確認係]  {output['cost_check']['notes']}")
    print(f"[判定]          {output['judgment']}")
    print(f"\n--- 仕様書ドラフト → output/spec.md ---")
    print(spec_text)

    state["document_output"] = output
    return state


if __name__ == "__main__":
    initial_state: ProjectState = {
        "request": "ユーザー管理API。ユーザーの登録・取得・更新・削除ができること。",
        "document_output": None,
        "decompose_output": None,
        "manage_output": None,
        "final_judgment": None,
        "final_summary": None,
    }
    run(initial_state)
