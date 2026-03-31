"""
AIKAISYA — 製造工程分解部門
ドキュメント作成部門の仕様書を受け取り、タスク（WBS）に分解する
"""
import json
import boto3
from src.core.policy import get_system_instruction
from src.core.state import ProjectState, DepartmentOutput
from src.core.parser import parse_department_output


DEPARTMENT_NAME = "製造工程分解部門"
MISSION = """
あなたはAPI仕様書をもとに、実装タスクをWBS（作業分解構造）として分解します。
エンドポイントごとに必要な実装ステップを具体的に列挙してください。
トレンド確認係として最新の実装手法を提案し、
API使用量確認係として各タスクの想定工数とコストを見積もってください。
"""

MODEL_ID = "jp.anthropic.claude-haiku-4-5-20251001-v1:0"
REGION = "ap-northeast-1"


def run(state: ProjectState) -> ProjectState:
    """製造工程分解部門の処理"""
    print(f"\n{'='*50}")
    print(f"[{DEPARTMENT_NAME}] 開始")
    print(f"{'='*50}")

    # 前部門（ドキュメント作成部門）の出力を受け取る
    doc_result = state.get("document_output", {})
    spec = doc_result.get("result", "仕様書なし") if doc_result else "仕様書なし"

    client = boto3.client("bedrock-runtime", region_name=REGION)
    system_instruction = get_system_instruction(DEPARTMENT_NAME, MISSION)

    prompt = f"""
以下のAPI仕様書をもとに、実装タスクをWBSとして分解してください。

【API仕様書】
{spec}

必ず以下のJSON形式のみで回答してください（コードブロック不要）：
{{
  "department_name": "{DEPARTMENT_NAME}",
  "trend_check": {{
    "summary": "実装手法のトレンドに関する所見を1文で",
    "is_modern": true
  }},
  "cost_check": {{
    "estimated_tokens": 500,
    "within_budget": true,
    "notes": "工数・コストの見積もりを1文で"
  }},
  "result": "タスク一覧をテキストで記述（改行は\\nで表現）",
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

    print(f"\n[トレンド確認係] {output['trend_check']['summary']}")
    print(f"[使用量確認係]  {output['cost_check']['notes']}")
    print(f"[判定]          {output['judgment']}")
    print(f"\n--- タスク一覧（WBS）---")
    print(output["result"])

    state["decompose_output"] = output
    return state
