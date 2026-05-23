from .sms import send_sms


def send_otp(phone: str, code: str) -> bool:
    return send_sms(phone, f"کد ورود دکترگیم: {code}")
