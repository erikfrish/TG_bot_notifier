from dataclasses import dataclass
from environs import Env


@dataclass()
class Bots:
    bot_token: str
    admin_id: str


@dataclass()
class db_config:
    host: str
    port: int
    user: str
    password: str
    database: str


@dataclass()
class conf:
    bots: Bots
    pg: db_config


def get_conf(path: str):
    env = Env()
    env.read_env(path)

    return conf(
        bots=Bots(
            bot_token=env.str("API_TOKEN"),
            admin_id=env.str("ADMIN_ID"),
        ),
        pg=db_config(
            host=env.str('pg_host'),
            port=env.int('pg_port'),
            user=env.str('pg_user'),
            password=env.str('pg_password'),
            database=env.str('pg_database'),
        ),
    )


# conf = get_conf('.env')
conf = get_conf('./core/.env')

# ./core/
