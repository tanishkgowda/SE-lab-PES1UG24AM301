"""
Lab 6 - Branch Coverage tests for water_utility_billing.py

Goal: make every decision (if / elif / else / loop) evaluate to BOTH True and False
(>= 90% branch coverage).

Run:
    coverage run --branch -m pytest BranchCoverageTest_water_utility_billing.py
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


# ---------------------------------------------------------------- input validation

@pytest.mark.parametrize("accounts, base_fee", [
    ("not-a-list", 10.0),   # first operand of the `or` is True
    ({}, 10.0),             # dict is not a list
    ([], -1.0),             # list is valid, negative base fee -> second operand True
])
def test_invalid_input_raises(accounts, base_fee):
    with pytest.raises(ValueError):
        calculate_water_bill(accounts, base_fee)


def test_valid_input_zero_base_fee_does_not_raise():
    # Both operands False (list, base_fee == 0 is not < 0)
    assert calculate_water_bill([], 0.0)["status"] == "NO_ACTIVITY"


# ---------------------------------------------------------------- active / inactive

def test_inactive_account_skipped():
    result = calculate_water_bill([make_account([30], is_active=False)], 10.0)
    assert result == {"total_billed": 0.0, "status": "NO_ACTIVITY"}


def test_missing_is_active_defaults_to_inactive():
    result = calculate_water_bill([{"usage_blocks": [30]}], 10.0)
    assert result["total_billed"] == 0.0


def test_active_account_billed():
    result = calculate_water_bill([make_account([30])], 10.0)
    assert result == {"total_billed": 55.0, "status": "NORMAL"}


def test_active_account_without_usage_blocks_pays_base_fee_only():
    # Loop body never entered (empty iterable)
    result = calculate_water_bill([{"is_active": True}], 10.0)
    assert result == {"total_billed": 10.0, "status": "NORMAL"}


# ---------------------------------------------------------------- usage tiers

@pytest.mark.parametrize("usage", [0, -5])
def test_non_positive_usage_flagged_and_skipped(usage):
    result = calculate_water_bill([make_account([usage, 20])], 10.0)
    assert result["total_billed"] == pytest.approx(40.0)


def test_low_tier_boundary_50():
    # usage == 50 is NOT > 50 -> low tier (1.5)
    result = calculate_water_bill([make_account([50])], 0.0)
    assert result["total_billed"] == pytest.approx(75.0)


def test_mid_tier_just_above_50():
    result = calculate_water_bill([make_account([51])], 0.0)
    assert result["total_billed"] == pytest.approx(127.5)


def test_mid_tier_boundary_100():
    # usage == 100 is NOT > 100 -> mid tier (2.5), not flagged
    result = calculate_water_bill([make_account([100])], 0.0)
    assert result["total_billed"] == pytest.approx(250.0)


def test_residential_over_100_breaks_loop():
    result = calculate_water_bill([make_account([120, 10])], 10.0)
    assert result["total_billed"] == pytest.approx(550.0)  # later block ignored


def test_commercial_over_100_continues_loop():
    result = calculate_water_bill([make_account([120, 60, 10], is_commercial=True)], 0.0)
    assert result["total_billed"] == pytest.approx(585.0)


# ---------------------------------------------------------------- leak waiver

def test_leak_waiver_applied_when_total_over_200():
    result = calculate_water_bill([make_account([80], has_leak_waiver=True)], 10.0)
    assert result["total_billed"] == pytest.approx(160.0)


def test_leak_waiver_not_applied_when_total_at_most_200():
    # waiver True, but total <= 200 -> inner if False
    result = calculate_water_bill([make_account([30], has_leak_waiver=True)], 10.0)
    assert result["total_billed"] == pytest.approx(55.0)


def test_leak_waiver_boundary_exactly_200():
    # 200.0 is NOT > 200.0 -> no deduction
    result = calculate_water_bill([make_account([80], has_leak_waiver=True)], 0.0)
    assert result["total_billed"] == pytest.approx(200.0)


def test_no_leak_waiver_means_no_deduction():
    result = calculate_water_bill([make_account([80])], 10.0)
    assert result["total_billed"] == pytest.approx(210.0)


# ---------------------------------------------------------------- status

def test_status_excessive_flags():
    result = calculate_water_bill([make_account([0, 0, 0, 0, 0, 0])], 10.0)
    assert result["status"] == "EXCESSIVE_FLAGS"


def test_status_five_flags_is_still_normal():
    # Boundary: flagged_accounts == 5 is NOT > 5
    result = calculate_water_bill([make_account([0, 0, 0, 0, 0])], 10.0)
    assert result["status"] == "NORMAL"


def test_status_no_activity():
    result = calculate_water_bill([make_account([30], is_active=False)], 10.0)
    assert result["status"] == "NO_ACTIVITY"


def test_status_normal():
    assert calculate_water_bill([make_account([30])], 10.0)["status"] == "NORMAL"


def test_multiple_accounts_accumulate():
    accounts = [make_account([30]), make_account([80]), make_account([30], is_active=False)]
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == pytest.approx(265.0)  # 55 + 210


# ---------------------------------------------------------------- check_meter_tampering

@pytest.mark.parametrize("readings", [[], None])
def test_tampering_no_data(readings):
    assert check_meter_tampering(readings) == "NO_DATA"


def test_tampering_suspected_two_consecutive_negatives():
    assert check_meter_tampering([[5, -1, -2]]) == "TAMPER_SUSPECTED"


def test_single_negative_is_not_tamper():
    # delta < 0 True but count < 2 (inner if False)
    assert check_meter_tampering([[5, -1, 5]]) == "CLEAR"


def test_negative_count_resets_on_non_negative():
    assert check_meter_tampering([[1, -1, 2, -1, 3]]) == "CLEAR"


def test_zero_delta_resets_count():
    # 0 is not < 0 -> goes to else branch and resets the counter
    assert check_meter_tampering([[-1, 0, -1]]) == "CLEAR"


def test_empty_meter_is_clear():
    # inner loop never entered
    assert check_meter_tampering([[]]) == "CLEAR"


def test_tamper_found_on_later_meter():
    assert check_meter_tampering([[1, 2, 3], [-1, -1]]) == "TAMPER_SUSPECTED"


def test_count_resets_between_meters():
    # one negative at the end of meter 1 and one at the start of meter 2 must NOT combine
    assert check_meter_tampering([[1, -1], [-1, 1]]) == "CLEAR"
