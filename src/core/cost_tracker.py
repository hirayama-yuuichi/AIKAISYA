"""
AIKAISYA — コストトラッカー
各部門のトークン使用量とコストを集計・アラート表示する
"""
from dataclasses import dataclass, field
from typing import List


# AWS Bedrock claude-haiku-4-5 の料金（2026年3月時点・概算）
# input: $0.001 / 1K tokens, output: $0.005 / 1K tokens → 平均 $0.003/1K
COST_PER_1K_TOKENS_USD = 0.003
USD_TO_JPY = 150  # 為替レート（概算）
ALERT_THRESHOLD_JPY = 100  # policy.yamlと合わせる


@dataclass
class DepartmentCost:
    name: str
    estimated_tokens: int
    within_budget: bool
    notes: str

    @property
    def cost_jpy(self) -> float:
        return (self.estimated_tokens / 1000) * COST_PER_1K_TOKENS_USD * USD_TO_JPY


@dataclass
class CostReport:
    departments: List[DepartmentCost] = field(default_factory=list)

    def add(self, name: str, cost_check: dict):
        self.departments.append(DepartmentCost(
            name=name,
            estimated_tokens=cost_check.get("estimated_tokens", 0),
            within_budget=cost_check.get("within_budget", True),
            notes=cost_check.get("notes", ""),
        ))

    @property
    def total_tokens(self) -> int:
        return sum(d.estimated_tokens for d in self.departments)

    @property
    def total_cost_jpy(self) -> float:
        return sum(d.cost_jpy for d in self.departments)

    @property
    def has_alert(self) -> bool:
        return self.total_cost_jpy > ALERT_THRESHOLD_JPY or any(not d.within_budget for d in self.departments)

    def display(self):
        print(f"\n{'='*50}")
        print("【コスト状況レポート】")
        print(f"{'='*50}")
        print(f"{'部門':<20} {'トークン':>8} {'コスト(円)':>10} {'予算内':>6}")
        print(f"{'-'*50}")
        for d in self.departments:
            budget_mark = "  ✓" if d.within_budget else "  ✗"
            print(f"{d.name:<20} {d.estimated_tokens:>8,} {d.cost_jpy:>9.2f}円 {budget_mark}")
        print(f"{'-'*50}")
        print(f"{'合計':<20} {self.total_tokens:>8,} {self.total_cost_jpy:>9.2f}円")
        print(f"上限: {ALERT_THRESHOLD_JPY}円")
        print()

        if self.has_alert:
            print("⚠️  【アラート】")
            if self.total_cost_jpy > ALERT_THRESHOLD_JPY:
                print(f"   コスト合計 {self.total_cost_jpy:.2f}円 が上限 {ALERT_THRESHOLD_JPY}円 を超えています")
            for d in self.departments:
                if not d.within_budget:
                    print(f"   [{d.name}] 予算超過: {d.notes}")
        else:
            print("✓ コスト正常（上限内）")
        print(f"{'='*50}")
