from pyspark.sql.types import ( StringType, IntegerType, DecimalType, DateType, TimestampType)

TYPE_MAPPING = {
    'integertype': IntegerType(),
    'stringtype': StringType(),
    'datetype': DateType(),
    'timestamptype': TimestampType(),
    'decimaltype': DecimalType(10,2)
}

def parse_type(type: str):
    if isinstance(type, str):
        base_type = type.lower().strip()
        return TYPE_MAPPING.get(base_type, StringType())
    return StringType()