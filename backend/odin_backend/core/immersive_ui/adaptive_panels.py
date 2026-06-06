def panels(*, count: int = 3) -> dict:
    return {"panels": min(count, 6), "draggable": True}
