def ambient(*, idle: bool) -> dict:
    return {"idle": idle, "glow": not idle, "simulated": True}
