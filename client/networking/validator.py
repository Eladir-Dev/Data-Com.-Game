

MAX_USERNAME_LEN = 20

def is_valid_username(username: str) -> bool:
    return 0 < len(username) <= MAX_USERNAME_LEN


def assert_valid_username(username: str) -> str:
    if not is_valid_username(username):
        raise ValueError(f"username '{username}' is invalid")
    
    return username


def assert_field_amount_valid(fields: list[str], expected_length: int) -> list[str]:
    if len(fields) != expected_length:
        raise ValueError(f"expected {expected_length} fields, got {len(fields)} (the fields were `{fields}`)")
    
    return fields


def assert_field_min_amount_valid(fields: list[str], min_expected_length: int) -> list[str]:
    if len(fields) < min_expected_length:
        raise ValueError(f"expected at least {min_expected_length} fields, got {len(fields)} (the fields were `{fields}`)")
    
    return fields