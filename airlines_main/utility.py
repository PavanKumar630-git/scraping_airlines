import uuid

def generate_numeric_uuid():
    return str(uuid.uuid4().int % 10**18)

