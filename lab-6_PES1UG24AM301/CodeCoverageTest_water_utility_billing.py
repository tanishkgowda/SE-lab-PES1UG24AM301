"""
Lab 6 - Code (Line) Coverage tests for water_utility_billing.py

Goal: execute every line of the application at least once (>= 90% line coverage).

Run:
    coverage run -m pytest CodeCoverageTest_water_utility_billing.py
    coverage report -m
"""
import pytest
from water_utility_billing import calculate_water_bill, check_meter_tampering


def make_account(usage_blocks, is_active=True, is_commercial=False, has_leak_waiver=False):
    return {
        "is_active": is_active,
        "is_commercial": is_commercial,
        "has_leak_waiver": has_leak_waiver,
        "usage_blocks": usage_blocks,
    }


# ---------------------------------------------------------------- calculate_water_bill

def test_single_active_residential():
    # Starter example: 10 base + 30 * 1.5 = 55
    result = calculate_water_bill([make_account([30])], 10.0)
    assert result == {"total_billed": 55.0, "status": "NORMAL"}


def test_invalid_accounts_type_raises():
    # Line 3: accounts is not a list
    with pytest.raises(ValueError):
        calculate_water_bill("not-a-list", 10.0)


def test_inactive_account_is_skipped():
    # Line 10: inactive account -> continue
    result = calculate_water_bill([make_account([30], is_active=False)], 10.0)
    assert result["total_billed"] == 0.0


def test_non_positive_usage_is_flagged_and_skipped():
    # Lines 18-19: usage <= 0 is flagged and ignored
    result = calculate_water_bill([make_account([0, -5, 20])], 10.0)
    assert result["total_billed"] == pytest.approx(40.0)  # 10 + 20 * 1.5


def test_residential_high_usage_breaks_loop():
    # Lines 22-25: residential usage > 100 -> 4.5 rate, then break (later block ignored)
    result = calculate_water_bill([make_account([120, 10])], 10.0)
    assert result["total_billed"] == pytest.approx(550.0)  # 10 + 120 * 4.5


def test_commercial_high_usage_continues_loop():
    # Line 26: commercial usage > 100 -> 3.5 rate, loop continues
    result = calculate_water_bill([make_account([120, 60, 10], is_commercial=True)], 0.0)
    assert result["total_billed"] == pytest.approx(585.0)  # 420 + 150 + 15


def test_mid_tier_usage():
    # Line 28: 50 < usage <= 100 -> 2.5 rate
    result = calculate_water_bill([make_account([80])], 10.0)
    assert result["total_billed"] == pytest.approx(210.0)  # 10 + 80 * 2.5


def test_leak_waiver_deduction_applied():
    # Lines 33-34: waiver and total > 200 -> minus 50
    result = calculate_water_bill([make_account([80], has_leak_waiver=True)], 10.0)
    assert result["total_billed"] == pytest.approx(160.0)  # 210 - 50


def test_excessive_flags_status():
    # Line 40: more than 5 flagged usages
    result = calculate_water_bill([make_account([0, 0, 0, 0, 0, 0])], 10.0)
    assert result["status"] == "EXCESSIVE_FLAGS"


def test_no_activity_status():
    # Line 42: nothing billed at all
    result = calculate_water_bill([], 10.0)
    assert result == {"total_billed": 0.0, "status": "NO_ACTIVITY"}


# ---------------------------------------------------------------- check_meter_tampering

def test_tampering_no_data():
    # Line 49
    assert check_meter_tampering([]) == "NO_DATA"


def test_tampering_suspected_on_consecutive_backflow():
    # Lines 51-57
    assert check_meter_tampering([[5, -1, -2]]) == "TAMPER_SUSPECTED"


def test_tampering_clear():
    # Lines 58-60
    assert check_meter_tampering([[1, -1, 2, -1, 3]]) == "CLEAR"
