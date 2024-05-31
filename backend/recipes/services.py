import uuid


def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))
        return value
    except ValueError:
        return

