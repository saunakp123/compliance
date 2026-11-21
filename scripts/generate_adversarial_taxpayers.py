#!/usr/bin/env python3
"""
generate_adversarial_taxpayers.py
=================================
Generates adversarial ITR-2 taxpayer JSON instances + ground-truth JSONL
for the LLM-judge vs. Lean proof experiment (ACL framing: LLM judge
reliability at rule-boundary conditions).

**Statute year:** All thresholds follow **FY 2024–25 / Finance Act 2024**
(matching `tax_rules_gold.jsonl` and `taxpayer_fields.json`). Finance Act
2025 raised several limits (e.g. §194 dividend to ₹10,000; §194A to
₹50,000 / ₹1,00,000 senior; new-regime §87A to ₹12 lakh) — those are
intentionally NOT used here. State "FY 2024–25 rules" in the paper.

**Case count:** 17 = original 5 + 8 new (adv_06–13) + 4 from splitting
adv_14/adv_15 into separate TDS-applicability and 20%-rate checks
(so each scores as a binary true/false like the other cases).

Field names follow the canonical Taxpayer schema in taxpayer_fields.json
(`is_pan_furnished`, not informal `has_pan`).
"""

from __future__ import annotations

import json
from pathlib import Path

BASE = json.loads(Path("data/tax/taxpayer_fields.json").read_text(encoding="utf-8"))

OUT_DIR = Path("data/tax/adversarial")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# FY 2024–25 statute year tag (surfaced in ground_truth.jsonl for the paper)
STATUTE_YEAR = "FY_2024_25"


def perturb(overrides: dict) -> dict:
    inst = dict(BASE)
    inst.update(overrides)
    return inst


CASES = [
    # ── Original 5 ──────────────────────────────────────────────────────────
    {
        "id": "adv_01_ltcg_boundary",
        "section": "112A",
        "type": "perturbation",
        "taxpayer": perturb({"ltcg_listed_equity_amount": 125000}),
        "rule_text_hint": (
            "Section 112A: long-term capital gains on listed equity exceeding "
            "Rs. 1,25,000 in a financial year are taxed at 12.5%; gains up to "
            "and including Rs. 1,25,000 are exempt."
        ),
        "ground_truth_verdict": False,
        "ground_truth_rationale": (
            "Statutory text is inclusive of the threshold ('up to Rs. 1,25,000'); "
            "exactly Rs. 1,25,000 is exempt, tax liability under 112A is nil."
        ),
        "lean_predicate": "adv_112a_taxable",
    },
    {
        "id": "adv_02_87a_boundary",
        "section": "87A",
        "type": "perturbation",
        "taxpayer": perturb({
            "total_income_amount": 500000,
            "is_new_tax_regime": False,
        }),
        "rule_text_hint": (
            "Section 87A: resident individuals with total income not exceeding "
            "Rs. 5,00,000 (old regime) are eligible for a rebate up to Rs. 12,500."
        ),
        "ground_truth_verdict": True,
        "ground_truth_rationale": (
            "'Not exceeding Rs. 5,00,000' includes exactly Rs. 5,00,000; "
            "taxpayer is rebate-eligible."
        ),
        "lean_predicate": "adv_87a_rebate_eligible",
    },
    {
        "id": "adv_03_stt_precondition_violation",
        "section": "111A",
        "type": "hand_crafted",
        "taxpayer": perturb({
            "stcg_listed_equity_amount": 80000,
            "is_stt_paid_on_transfer": False,
        }),
        "rule_text_hint": (
            "Section 111A: short-term capital gains on listed equity are taxed "
            "at the concessional rate of 20% ONLY WHERE securities transaction "
            "tax (STT) has been paid on the transaction. Absent STT payment, "
            "gains are taxed at the applicable slab rate, not the concessional rate."
        ),
        "ground_truth_verdict": False,
        "ground_truth_rationale": (
            "111A concessional rate has a hard STT-paid precondition. "
            "is_stt_paid_on_transfer=False means the composite predicate fails "
            "at the conjunction, regardless of the STCG amount."
        ),
        "lean_predicate": "adv_111a_concessional",
    },
    {
        "id": "adv_04_80d_senior_citizen_misclassification",
        "section": "80D",
        "type": "hand_crafted",
        "taxpayer": perturb({
            "health_insurance_premium_amount": 50000,
            "is_senior_citizen": False,
        }),
        "rule_text_hint": (
            "Section 80D: deduction for health insurance premium is capped at "
            "Rs. 25,000 for non-senior citizens and Rs. 50,000 for senior citizens "
            "(age 60 or above). Decide whether the full claimed premium is deductible."
        ),
        "ground_truth_verdict": False,
        "ground_truth_rationale": (
            "Deduction claimed (Rs. 50,000) exceeds the non-senior cap (Rs. 25,000). "
            "Allowable deduction is Rs. 25,000, not the full claimed amount."
        ),
        "lean_predicate": "adv_80d_full_deduction",
    },
    {
        "id": "adv_05_residency_day_count_boundary",
        "section": "6_1",
        "type": "hand_crafted",
        "taxpayer": perturb({
            "days_in_india_fy": 182,
            "is_resident": True,
        }),
        "rule_text_hint": (
            "Section 6(1): an individual is a resident in India in a financial "
            "year if present in India for 182 days or more in that year."
        ),
        "ground_truth_verdict": True,
        "ground_truth_rationale": (
            "'182 days or more' includes exactly 182; taxpayer is a resident."
        ),
        "lean_predicate": "adv_6_1_resident",
    },
    # ── Expansion: adv_06–13 ────────────────────────────────────────────────
    {
        "id": "adv_06_194_dividend_tds_threshold",
        "section": "194",
        "type": "perturbation",
        "taxpayer": perturb({"dividend_income_amount": 5000}),
        "rule_text_hint": (
            "Section 194 (FY 2024–25): TDS on dividend applies where the amount "
            "paid to a resident shareholder exceeds Rs. 5,000 in a financial year. "
            "No TDS is deductible at or below this threshold."
        ),
        "ground_truth_verdict": False,
        "ground_truth_rationale": (
            "'Exceeds Rs. 5,000' excludes the threshold value itself; "
            "TDS not applicable at exactly Rs. 5,000."
        ),
        "lean_predicate": "adv_194_tds_applies",
    },
    {
        "id": "adv_07_194a_senior_citizen_threshold",
        "section": "194A",
        "type": "hand_crafted",
        "taxpayer": perturb({
            "interest_income_bank_amount": 45000,
            "is_senior_citizen": False,
        }),
        "rule_text_hint": (
            "Section 194A (FY 2024–25): TDS on bank interest applies where interest "
            "paid exceeds Rs. 40,000 in a year for non-senior citizens, or Rs. "
            "50,000 for senior citizens (age 60+)."
        ),
        "ground_truth_verdict": True,
        "ground_truth_rationale": (
            "Taxpayer is non-senior; correct threshold is Rs. 40,000, not Rs. 50,000. "
            "Rs. 45,000 exceeds the applicable threshold."
        ),
        "lean_predicate": "adv_194a_tds_applies",
    },
    {
        "id": "adv_08_139_filing_obligation_boundary",
        "section": "139_1",
        "type": "perturbation",
        "taxpayer": perturb({
            "total_income_amount": 250000,
            "is_new_tax_regime": False,
            "is_return_filing_required": False,
        }),
        "rule_text_hint": (
            "Section 139(1): a return of income is mandatory where total "
            "income exceeds the basic exemption limit of Rs. 2,50,000 (old "
            "regime, non-senior)."
        ),
        "ground_truth_verdict": False,
        "ground_truth_rationale": (
            "'Exceeds' excludes the threshold itself; at exactly Rs. 2,50,000, "
            "filing is not mandatory under 139(1) alone."
        ),
        "lean_predicate": "adv_139_1_filing_required",
    },
    {
        "id": "adv_09_80c_investment_cap_exceeded",
        "section": "80C",
        "type": "hand_crafted",
        "taxpayer": perturb({
            "investment_80c_amount": 200000,
            "is_new_tax_regime": False,
        }),
        "rule_text_hint": (
            "Section 80C: deduction for specified investments is capped at "
            "Rs. 1,50,000 regardless of the amount actually invested. Decide "
            "whether the full invested amount is deductible."
        ),
        "ground_truth_verdict": False,
        "ground_truth_rationale": (
            "Allowable deduction is capped at Rs. 1,50,000; the claimed full "
            "amount (Rs. 2,00,000) is not fully deductible."
        ),
        "lean_predicate": "adv_80c_full_investment_deductible",
    },
    {
        "id": "adv_10_234b_90pct_boundary",
        "section": "234B",
        "type": "perturbation",
        "taxpayer": perturb({
            "assessed_tax_amount": 100000,
            "advance_tax_paid_amount": 90000,
        }),
        "rule_text_hint": (
            "Section 234B: interest for default in payment of advance tax "
            "applies where advance tax paid is less than 90% of assessed tax."
        ),
        "ground_truth_verdict": False,
        "ground_truth_rationale": (
            "'Less than 90%' excludes exactly 90%; at advance_tax_paid = 0.9 × "
            "assessed_tax, Section 234B interest does not apply."
        ),
        "lean_predicate": "adv_234b_interest_applies",
    },
    {
        "id": "adv_11_111a_112a_holding_period_edge",
        "section": "111A_112A",
        "type": "hand_crafted",
        "taxpayer": perturb({
            "stcg_listed_equity_amount": 60000,
            "ltcg_listed_equity_amount": 0,
            "holding_period_months_equity": 12,
            "is_stt_paid_on_transfer": True,
        }),
        "rule_text_hint": (
            "Listed equity held for NOT MORE THAN 12 months is short-term "
            "(Section 111A, 20% rate); held for MORE THAN 12 months is "
            "long-term (Section 112A, 12.5% rate above the exemption). "
            "Decide whether Section 111A (short-term concessional) applies."
        ),
        "ground_truth_verdict": True,
        "ground_truth_rationale": (
            "'Not more than 12 months' includes exactly 12; this is short-term "
            "and governed by 111A, not 112A."
        ),
        "lean_predicate": "adv_111a_short_term_at_12m",
    },
    {
        "id": "adv_12_80c_disallowed_under_new_regime",
        "section": "80C",
        "type": "hand_crafted",
        "taxpayer": perturb({
            "investment_80c_amount": 150000,
            "is_new_tax_regime": True,
        }),
        "rule_text_hint": (
            "Section 80C deductions are available only under the OLD tax "
            "regime. Under the NEW regime, most Chapter VI-A deductions, "
            "including 80C, are not allowed. Decide whether an 80C deduction "
            "is allowed for this taxpayer."
        ),
        "ground_truth_verdict": False,
        "ground_truth_rationale": (
            "Regime is a hard precondition on 80C eligibility; new regime ⇒ "
            "deduction not allowed regardless of amount."
        ),
        "lean_predicate": "adv_80c_deduction_allowed",
    },
    {
        "id": "adv_13_87a_new_regime_limit",
        "section": "87A",
        "type": "perturbation",
        "taxpayer": perturb({
            "total_income_amount": 700000,
            "is_new_tax_regime": True,
        }),
        "rule_text_hint": (
            "Section 87A rebate limit is Rs. 5,00,000 under the old regime "
            "and Rs. 7,00,000 under the new regime (FY 2024–25). Decide "
            "whether the taxpayer is rebate-eligible."
        ),
        "ground_truth_verdict": True,
        "ground_truth_rationale": (
            "Under the new regime the applicable limit is Rs. 7,00,000; "
            "exactly at the limit ⇒ eligible."
        ),
        "lean_predicate": "adv_87a_new_regime_eligible",
    },
    # ── Split adv_14 / adv_15: TDS applies vs 20% rate (binary each) ───────
    {
        "id": "adv_14_194_tds_applies",
        "section": "194",
        "type": "hand_crafted",
        "taxpayer": perturb({
            "dividend_income_amount": 10000,
            "is_pan_furnished": False,
            "tds_rate_194_dividend_pct": 20,  # elevated rate fact for LLM context
        }),
        "rule_text_hint": (
            "Section 194 (FY 2024–25): TDS on dividend applies where the amount "
            "paid exceeds Rs. 5,000. Decide whether TDS is deductible for this "
            "taxpayer (applicability only — ignore the rate)."
        ),
        "ground_truth_verdict": True,
        "ground_truth_rationale": (
            "Dividend Rs. 10,000 exceeds the Rs. 5,000 threshold ⇒ TDS applies."
        ),
        "lean_predicate": "adv_194_tds_applies",
    },
    {
        "id": "adv_14_194_rate_20pct",
        "section": "194",
        "type": "hand_crafted",
        "taxpayer": perturb({
            "dividend_income_amount": 10000,
            "is_pan_furnished": False,
            "tds_rate_194_dividend_pct": 20,
        }),
        "rule_text_hint": (
            "Section 194 / 206AA: TDS on dividend is 10% where PAN is furnished, "
            "or 20% where PAN is not furnished. Decide whether the elevated "
            "20% rate applies for this taxpayer."
        ),
        "ground_truth_verdict": True,
        "ground_truth_rationale": (
            "is_pan_furnished=False triggers the 20% rate under Section 206AA."
        ),
        "lean_predicate": "adv_194_rate_20pct",
    },
    {
        "id": "adv_15_194a_tds_applies",
        "section": "194A",
        "type": "hand_crafted",
        "taxpayer": perturb({
            "interest_income_bank_amount": 45000,
            "is_senior_citizen": False,
            "is_pan_furnished": False,
            "tds_rate_194a_pct": 20,
        }),
        "rule_text_hint": (
            "Section 194A (FY 2024–25): TDS on bank interest applies where "
            "interest exceeds Rs. 40,000 for non-senior citizens (Rs. 50,000 "
            "for seniors). Decide whether TDS is deductible (applicability "
            "only — ignore the rate)."
        ),
        "ground_truth_verdict": True,
        "ground_truth_rationale": (
            "Non-senior with Rs. 45,000 interest exceeds the Rs. 40,000 "
            "threshold ⇒ TDS applies."
        ),
        "lean_predicate": "adv_194a_tds_applies",
    },
    {
        "id": "adv_15_194a_rate_20pct",
        "section": "194A",
        "type": "hand_crafted",
        "taxpayer": perturb({
            "interest_income_bank_amount": 45000,
            "is_senior_citizen": False,
            "is_pan_furnished": False,
            "tds_rate_194a_pct": 20,
        }),
        "rule_text_hint": (
            "Section 194A / 206AA: TDS on interest is 10% where PAN is furnished, "
            "or 20% where PAN is not furnished. Decide whether the elevated "
            "20% rate applies for this taxpayer."
        ),
        "ground_truth_verdict": True,
        "ground_truth_rationale": (
            "is_pan_furnished=False triggers the 20% rate under Section 206AA."
        ),
        "lean_predicate": "adv_194a_rate_20pct",
    },
]


def main() -> None:
    gt_path = OUT_DIR / "ground_truth.jsonl"
    with gt_path.open("w", encoding="utf-8") as gt_f:
        for case in CASES:
            inst_path = OUT_DIR / f"{case['id']}.json"
            inst_path.write_text(
                json.dumps(case["taxpayer"], indent=2),
                encoding="utf-8",
            )
            gt_f.write(json.dumps({
                "id": case["id"],
                "section": case["section"],
                "type": case["type"],
                "statute_year": STATUTE_YEAR,
                "rule_text_hint": case["rule_text_hint"],
                "ground_truth_verdict": case["ground_truth_verdict"],
                "ground_truth_rationale": case["ground_truth_rationale"],
                "lean_predicate": case["lean_predicate"],
                "taxpayer_file": str(inst_path).replace("\\", "/"),
            }) + "\n")
    print(
        f"Wrote {len(CASES)} adversarial instances ({STATUTE_YEAR}) + {gt_path}"
    )


if __name__ == "__main__":
    main()
