KRW_TO_USD = 0.00073

def krw_to_usd(amount_krw: float) -> float:
    return round(amount_krw * KRW_TO_USD, 2)