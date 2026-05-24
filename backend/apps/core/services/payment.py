import uuid


def initiate_payment(amount: int, order_id: str, callback_url: str) -> dict:
    authority = f"dev-{uuid.uuid4().hex}"
    return {
        "payment_url": f"{callback_url}?authority={authority}&order_id={order_id}",
        "authority": authority,
        "amount": amount,
        "order_id": order_id,
        "status": "pending",
    }


def verify_payment(authority: str) -> dict:
    return {
        "status": "ok" if authority else "failed",
        "authority": authority,
        "ref_id": f"dev-ref-{authority[-12:]}" if authority else "",
    }
