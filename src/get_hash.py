import hashlib

def calculate_hash(business_columns):
    row_string = '|'.join(col for col in business_columns)
    return hashlib.sha256(row_string.encode('UTF-8')).hexdigest()
