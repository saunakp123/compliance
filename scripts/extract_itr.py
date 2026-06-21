#!/usr/bin/env python3
"""
extract_itr.py
==============
Extract structured fields from an ITR-2 XML file.
Maps XML paths → taxpayer_fields.json consumable by generate_taxpayer_lean.py.

Usage:
    python scripts/extract_itr.py \
        --itr   data/tax/sample_itr2.xml \
        --rules data/tax/tax_rules_gold.jsonl \
        --out   data/tax/taxpayer_fields.json
"""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from datetime import date, datetime
from pathlib import Path


def _local_tag(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def _find_child_by_tag(el: ET.Element, tag: str) -> ET.Element | None:
    for child in el:
        if _local_tag(child.tag) == tag:
            return child
    return None


def _itr2_root(root: ET.Element) -> ET.Element:
    """Return the ITR2 element if present, else root."""
    itr2 = _find_child_by_tag(root, "ITR2")
    return itr2 if itr2 is not None else root


def _text(root, path: str, default: str = "") -> str:
    """Get text at a dot-separated tag path, stripping namespace prefixes."""
    el = root
    for tag in path.split("/"):
        found = None
        for child in el:
            local = _local_tag(child.tag)
            if local == tag:
                found = child
                break
        if found is None:
            return default
        el = found
    return (el.text or "").strip()


def _int(root, path: str, default: int = 0) -> int:
    raw = _text(root, path, str(default))
    try:
        return int(float(raw.replace(",", "")))
    except (ValueError, AttributeError):
        return default


def _bool_from_flag(root, path: str, true_values: tuple = ("Y", "YES", "1", "true")) -> bool:
    raw = _text(root, path, "N").strip().upper()
    return raw in true_values


def _age_from_dob(root, path: str, fy_start_year: int) -> int:
    """Compute age as of 1st April of the FY."""
    dob_str = _text(root, path, "")
    if not dob_str:
        return 0
    try:
        dob = datetime.strptime(dob_str, "%d/%m/%Y").date()
        reference = date(fy_start_year, 4, 1)
        age = (reference - dob).days // 365
        return max(0, age)
    except ValueError:
        return 0


def extract_fields(root, fy_start_year: int = 2024) -> dict:
    """
    Extract all taxpayer fields relevant to tax_rules_gold.jsonl.
    Returns a dict of field_name → value (Python native types).
    """
    age = _age_from_dob(root, "PartAGEN1/PersonalInfo/DOB", fy_start_year)

    residential_status = _text(root, "PartAGEN1/ResidentialStatus/ResidentialStatusDrop", "RES")
    days_in_india_fy = _int(root, "PartAGEN1/ResidentialStatus/DaysInIndia", 365)
    is_resident = residential_status in ("RES", "RNOR") or days_in_india_fy >= 182

    new_tax_regime_flag = _text(root, "PartAGEN1/FilingStatus/OptingNewTaxRegime", "Y")
    is_new_tax_regime = new_tax_regime_flag.upper() in ("Y", "YES", "1")

    pan = _text(root, "PartAGEN1/PersonalInfo/PAN", "")
    is_pan_furnished = len(pan) == 10

    is_senior_citizen = age >= 60
    is_super_senior_citizen = age >= 80

    total_income_amount = _int(root, "PartBTTI/TotalIncome", 0)

    stcg_listed_equity_amount = _int(
        root, "ScheduleCG/ShortTermCapGain15Per/EquityMFAmount", 0
    )
    is_stt_paid_on_transfer = _bool_from_flag(
        root, "ScheduleCG/ShortTermCapGain15Per/STTPaid"
    )
    stcg_tax_rate_pct = 20

    ltcg_listed_equity_amount = _int(
        root, "ScheduleCG/LongTermCapGain10Per/EquityMFAmount", 0
    )
    is_stt_paid_at_acquisition = _bool_from_flag(
        root, "ScheduleCG/LongTermCapGain10Per/STTPaidAcquisition"
    )
    holding_period_months_equity = _int(
        root, "ScheduleCG/LongTermCapGain10Per/HoldingPeriodMonths", 13
    )
    ltcg_exempt_limit = 125000
    ltcg_tax_rate_pct_x10 = 125

    dividend_income_amount = _int(root, "ScheduleOS/DividendGross", 0)
    tds_rate_194_dividend_pct = 10
    tds_rate_no_pan_pct = 20

    interest_income_bank_amount = _int(root, "ScheduleOS/IntrstFrmSavingBank", 0)
    interest_income_bank_amount += _int(root, "ScheduleOS/IntrstFrmTermDep", 0)
    interest_threshold_bank = 40000
    interest_threshold_senior_bank = 50000
    tds_rate_194a_pct = 10

    investment_80c_amount = _int(root, "ScheduleVIA/DeductUndChapVIA/Section80C", 0)
    max_80c_deduction = 150000

    health_insurance_premium_amount = _int(
        root, "ScheduleVIA/DeductUndChapVIA/Section80DSelfFamily", 0
    )
    max_80d_deduction_self = 25000
    max_80d_deduction_senior = 50000

    rebate_87a_threshold = 500000
    max_rebate_87a = 12500
    rebate_87a_new_threshold = 700000
    max_rebate_87a_new = 25000

    advance_tax_paid_amount = _int(root, "TaxPaid/TaxesPaid/AdvanceTax", 0)
    assessed_tax_amount = _int(root, "PartBTTI/ComputationOfTaxLiability/TaxPayable", 0)
    advance_tax_threshold_pct = 90

    basic_exemption_limit = 250000
    basic_exemption_limit_senior = 300000
    basic_exemption_limit_super_senior = 500000
    is_return_filing_required = total_income_amount > basic_exemption_limit

    return {
        "days_in_india_fy": days_in_india_fy,
        "is_resident": is_resident,
        "age_years": age,
        "is_senior_citizen": is_senior_citizen,
        "is_super_senior_citizen": is_super_senior_citizen,
        "is_pan_furnished": is_pan_furnished,
        "is_new_tax_regime": is_new_tax_regime,
        "total_income_amount": total_income_amount,
        "stcg_listed_equity_amount": stcg_listed_equity_amount,
        "is_stt_paid_on_transfer": is_stt_paid_on_transfer,
        "stcg_tax_rate_pct": stcg_tax_rate_pct,
        "ltcg_listed_equity_amount": ltcg_listed_equity_amount,
        "is_stt_paid_at_acquisition": is_stt_paid_at_acquisition,
        "holding_period_months_equity": holding_period_months_equity,
        "ltcg_exempt_limit": ltcg_exempt_limit,
        "ltcg_tax_rate_pct_x10": ltcg_tax_rate_pct_x10,
        "dividend_income_amount": dividend_income_amount,
        "tds_rate_194_dividend_pct": tds_rate_194_dividend_pct,
        "tds_rate_no_pan_pct": tds_rate_no_pan_pct,
        "interest_income_bank_amount": interest_income_bank_amount,
        "interest_threshold_bank": interest_threshold_bank,
        "interest_threshold_senior_bank": interest_threshold_senior_bank,
        "tds_rate_194a_pct": tds_rate_194a_pct,
        "investment_80c_amount": investment_80c_amount,
        "max_80c_deduction": max_80c_deduction,
        "health_insurance_premium_amount": health_insurance_premium_amount,
        "max_80d_deduction_self": max_80d_deduction_self,
        "max_80d_deduction_senior": max_80d_deduction_senior,
        "rebate_87a_threshold": rebate_87a_threshold,
        "max_rebate_87a": max_rebate_87a,
        "rebate_87a_new_threshold": rebate_87a_new_threshold,
        "max_rebate_87a_new": max_rebate_87a_new,
        "advance_tax_paid_amount": advance_tax_paid_amount,
        "assessed_tax_amount": assessed_tax_amount,
        "advance_tax_threshold_pct": advance_tax_threshold_pct,
        "basic_exemption_limit": basic_exemption_limit,
        "basic_exemption_limit_senior": basic_exemption_limit_senior,
        "basic_exemption_limit_super_senior": basic_exemption_limit_super_senior,
        "is_return_filing_required": is_return_filing_required,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--itr", required=True, type=Path, help="ITR-2 XML file from income tax portal")
    parser.add_argument("--rules", required=True, type=Path, help="tax_rules_gold.jsonl (used to validate coverage)")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--fy", type=int, default=2024, help="FY start year (e.g. 2024 for FY 2024-25)")
    args = parser.parse_args()

    tree = ET.parse(args.itr)
    root = _itr2_root(tree.getroot())
    fields = extract_fields(root, fy_start_year=args.fy)

    missing = []
    with open(args.rules, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rule = json.loads(line)
            for m in rule.get("maps_to") or []:
                field = m.get("field", "")
                if field and field not in fields:
                    missing.append(f"{rule['rule_id']}.{field}")

    if missing:
        print(f"[extract_itr] WARNING: {len(missing)} fields not extracted:")
        for m in missing:
            print(f"  {m}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(fields, f, indent=2)

    print(f"[extract_itr] Extracted {len(fields)} fields -> {args.out}")
    if not missing:
        print("[extract_itr] Coverage: 100% of rules JSONL fields present")


if __name__ == "__main__":
    main()
