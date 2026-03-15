import uuid

def generate_numeric_uuid():
    return str(uuid.uuid4().int % 10**18)


def validate_pnr(pnr):
    return len(pnr) == 6 and pnr.isalnum() and pnr.isupper()