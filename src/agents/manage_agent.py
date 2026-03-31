"""
AIKAISYA — 製造工程管理部門
製造工程分解部門のWBSを受け取り、進捗管理・優先順位・納期予測を行う
"""
import json
import boto3
from src.core.policy import get_system_instruction
from src.core.state import ProjectState, DepartmentOutput
from src.core.parser import parse_department_output


DEPARTMENT_NAME = "製造工程管理部門"
MISSION = """
あなたはWBS（タスク一覧）をもとに、進捗管理計画を策定します。
各フェーズの優先順位・依存関係・並行実行可否を整理し、
スケジュール（ガントチャート的な順序）と納期予測を提示してください。
トレンド確認係として最新のプロジェクト管理手法を提案し、
API使用量確認係として管理コスト・リソースを見積もってください。
また、ボトルネックになりそな工程を特定し、対策を提案してください。
"""

MODEL_ID = "jp.anthropic.claude-haiku-4-5-20251001-v1:0"
REGION = "ap-northeast-1"


def run(state: ProjectState) -> ProjectState:
    """製造工程管理部門の処理"""
    print(f"\n{'='*50}")
    print(f"[{DEPARTMENT_NAME}] 開始")
    print(f"{'='*50}")

    decompose_result = state.get("decompose_output", {})
    wbs_full = decompose_result.get("result", "WBSなし") if decompose_result else "WBSなし"
    # トークン節約のため先頭800文字に絞る
    wbs = wbs_full[:800] + ("…（以下省略）" if len(wbs_full) > 800 else "")

    client = boto3.client("bedrock-runtime", region_name=REGION)
    system_instruction = get_system_instruction(DEPARTMENT_NAME, MISSION)

    prompt = f"""
以下のWBSをもとに、進捗管理計画を策定してください。

【WBS】
{wbs}

必ず以下のJSON形式のみで回答してください（コードブロック不要）：
{{
  "department_name": "{DEPARTMENT_NAME}",
  "trend_check": {{
    "summary": "プロジェクト管理手法のトレンドに関する所見を1文で",
    "is_modern": true
  }},
  "cost_check": {{
    "estimated_tokens": 500,
    "within_budget": true,
    "notes": "管理コスト・リソースの見積もりを1文で"
  }},
  "result": "進捗管理計画（優先順位・スケジュール・ボトルネック対策）をテキストで記述（改行は\\nで表現）",
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
    print(f"\n--- 進捗管理計画 ---")
    print(output["result"])

    state["manage_output"] = output
    return state
