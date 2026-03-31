"""
AIKAISYA — コード生成部門
API仕様書をもとに、実際に動くFastAPIのコードを生成してファイルに保存する
"""
import json
import boto3
from pathlib import Path
from src.core.policy import get_system_instruction
from src.core.state import ProjectState, DepartmentOutput
from src.core.parser import parse_department_output


DEPARTMENT_NAME = "コード生成部門"
MISSION = """
あなたはAPI仕様書をもとに、実際に動くPython（FastAPI）のコードを生成します。
エンドポイントごとにルーター・スキーマ・基本的なCRUD処理を実装してください。
コードはそのまま実行できる品質にしてください。
トレンド確認係として最新のPython/FastAPI実装パターンを使用し、
API使用量確認係としてコード生成に使ったトークン数を見積もってください。
"""

MODEL_ID = "jp.anthropic.claude-haiku-4-5-20251001-v1:0"
REGION = "ap-northeast-1"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "output"


def run(state: ProjectState) -> ProjectState:
    """コード生成部門の処理"""
    print(f"\n{'='*50}")
    print(f"[{DEPARTMENT_NAME}] 開始")
    print(f"{'='*50}")

    doc_result = state.get("document_output", {})
    spec = doc_result.get("result", "仕様書なし") if doc_result else "仕様書なし"
    # 仕様書を先頭600文字に絞る
    spec = spec[:600] + ("…" if len(spec) > 600 else "")

    client = boto3.client("bedrock-runtime", region_name=REGION)
    system_instruction = get_system_instruction(DEPARTMENT_NAME, MISSION)

    # Step1: コードを生成
    code_prompt = f"""
以下のAPI仕様書をもとに、FastAPI（Python）のコードを生成してください。

【API仕様書】
{spec}

【出力ルール】
- コードのみを出力してください（説明文不要）
- ```python ``` のコードブロックで囲んでください
- OAuth2.0認証・HTTPS・レート制限（slowapi）・camelCaseを遵守してください
"""
    code_response = client.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 3000,
            "system": system_instruction,
            "messages": [{"role": "user", "content": code_prompt}]
        })
    )
    code_raw = json.loads(code_response["body"].read())["content"][0]["text"]

    # コードブロックを抽出
    import re
    code_match = re.search(r"```python\n(.*?)```", code_raw, re.DOTALL)
    code = code_match.group(1).strip() if code_match else code_raw.strip()

    # コードをファイルに保存
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / "main_api.py"
    output_path.write_text(code, encoding="utf-8")

    # Step2: メタ情報を取得
    meta_prompt = f"""
コード生成が完了しました。以下のJSON形式で評価してください（コードブロック不要）：
{{
  "department_name": "{DEPARTMENT_NAME}",
  "trend_check": {{
    "summary": "使用したFastAPIパターンのトレンド所見を1文で",
    "is_modern": true
  }},
  "cost_check": {{
    "estimated_tokens": 1200,
    "within_budget": true,
    "notes": "コード生成のトークン使用量の所見を1文で"
  }},
  "result": "output/main_api.py に保存済み",
  "judgment": "承認"
}}
"""
    meta_response = client.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "system": system_instruction,
            "messages": [{"role": "user", "content": meta_prompt}]
        })
    )
    meta_raw = json.loads(meta_response["body"].read())["content"][0]["text"]
    output: DepartmentOutput = parse_department_output(meta_raw, DEPARTMENT_NAME)

    print(f"\n[トレンド確認係] {output['trend_check']['summary']}")
    print(f"[使用量確認係]  {output['cost_check']['notes']}")
    print(f"[判定]          {output['judgment']}")
    print(f"\n--- 生成コード（{output_path}）---")
    print(code)

    state["code_output"] = output
    return state
