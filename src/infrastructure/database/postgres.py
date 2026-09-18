from dotenv import load_dotenv
import os

load_dotenv()


# returns the parameters for connection to Postgres
def get_jdbc_options(config: dict, layer_name: str):
    for layer in config['layers']:
        if layer_name == layer['name']:

            host = os.getenv("POSTGRES_HOST_DWH")
            port = os.getenv("POSTGRES_PORT_DWH")
            user = os.getenv("POSTGRES_USER_DWH")
            password = os.getenv("POSTGRES_PASS_DWH")

            missing = []
            
            if not host: missing.append('host')
            if not port: missing.append('port')
            if not user: missing.append('user')
            if not password: missing.append('password')

            if missing:
                raise ValueError (f"Отсутствуют переменные окружения для {layer_name}: {', '.join(missing)}")

            return {
                "url": f"jdbc:postgresql://{host}:{port}/{layer_name}",
                "user": user,
                "password": password,
                "driver": "org.postgresql.Driver"
            }

    raise ValueError (f"JDBC-конфиг для {layer_name} не найден по данному конфигу")