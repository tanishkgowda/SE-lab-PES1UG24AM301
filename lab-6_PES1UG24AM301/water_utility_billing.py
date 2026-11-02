def calculate_water_bill(accounts, base_fee):
    if not isinstance(accounts, list) or base_fee < 0:
        raise ValueError("Invalid accounts list or base fee")

    total_billed = 0.0
    flagged_accounts = 0

    for account in accounts:
        if not account.get("is_active", False):
            continue

        usage_blocks = account.get("usage_blocks", [])
        is_commercial = account.get("is_commercial", False)
        acct_total = float(base_fee)

        for usage in usage_blocks:
            if usage <= 0:
                flagged_accounts += 1
                continue

            if usage > 100:
                flagged_accounts += 1
                if not is_commercial:
                    acct_total += usage * 4.5
                    break  
                acct_total += usage * 3.5
            elif usage > 50:
                acct_total += usage * 2.5
            else:
                acct_total += usage * 1.5

        if account.get("has_leak_waiver", False):
            if acct_total > 200.0:
                acct_total -= 50.0

        total_billed += acct_total

    status = "NORMAL"
    if flagged_accounts > 5:
        status = "EXCESSIVE_FLAGS"
    elif total_billed == 0.0:
        status = "NO_ACTIVITY"

    return {"total_billed": round(total_billed, 2), "status": status}


def check_meter_tampering(readings_matrix):
    if not readings_matrix:
        return "NO_DATA"

    for meter in readings_matrix:
        backward_flow_count = 0
        for delta in meter:
            if delta < 0:
                backward_flow_count += 1
                if backward_flow_count >= 2:
                    return "TAMPER_SUSPECTED"
            else:
                backward_flow_count = 0
    return "CLEAR"