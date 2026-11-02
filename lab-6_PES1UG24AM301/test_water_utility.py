import pytest
from water_utility_billing import calculate_water_bill, check_meter_tampering

# Example test case:
def test_single_active_residential():
    accounts = [
        {
            "is_active": True,
            "is_commercial": False,
            "has_leak_waiver": False,
            "usage_blocks": [30]
        }
    ]
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 55.0
    assert result["status"] == "NORMAL"

# TODO: Add test cases to achieve 90-100% on both Line and Branch coverage!