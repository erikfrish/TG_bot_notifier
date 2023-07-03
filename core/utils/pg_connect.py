import psycopg2 as sql
import asyncio
from aiogram import Bot
# from aiogram.types import Message

from core.conf import conf
host = conf.pg.host
port = conf.pg.port
user = conf.pg.user
password = conf.pg.password
database = conf.pg.database


async def new_connection():
    try:
        connection = sql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database)
    except Exception as ex:
        print(ex)
    return connection



# Таблица Tasks_audit имеет следующую структуру:
    # 0 operation           char(10)   NOT NULL,
    # 1 task_id             BIGINT NOT NULL,
    # 2 stamp               timestamp with time zone DEFAULT now(),
    # 3 task_header         character varying(100),
    # 4 old_status          character varying(20),
    # 5 new_status          character varying(20),
    # 6 customer            integer,
    # 7 old_executor        integer,
    # 8 new_executor        integer,
    # 9 mentor              integer, 
    # 10 task_deadline      timestamp with time zone,
    # 11 task_body          text, 
    # 12 near_university    BOOLEAN,
    # 13 who_notify_in_tg   char(10)
# Поэтому в кортеже с ответом last_row будет с индексом 13 как раз who_notify_in_tg
async def get_last_row_from_tasks_audit() -> tuple:
    conn = await new_connection()
    with conn.cursor() as cursor:
        cursor.execute("""SELECT * FROM "Tasks_audit" ORDER BY stamp DESC""")
        last_row = cursor.fetchone()
        return last_row


# TODO добавить проверку на то, больше одной ли строки добавилось за 2 секунды
async def checking_for_new_row(bot: Bot):
    last_row = await get_last_row_from_tasks_audit()
    while True:
        await asyncio.sleep(2)
        if last_row != await get_last_row_from_tasks_audit():
            last_row = await get_last_row_from_tasks_audit()
            await notify_users_with_bot(bot, last_row[13], last_row[0])

async def get_tg_id_from_db(ids_s: str) -> list:
    conn = await new_connection()
    with conn.cursor() as cursor:
        user_ids = get_list_from_string(ids_s)
        res: list = []
        for id in user_ids:
            cursor.execute("""SELECT u.telegram as tg FROM "Users" u where u.id = %s;""", (id,))
            row = cursor.fetchone()
            if row[0] != None:
                res.append(row[0])
        return res

async def notify_users_with_bot(bot: Bot, whom_to_notify, what_about_to_notify):
    whom_to_notify_ids = await get_tg_id_from_db(whom_to_notify)
    for tg in whom_to_notify_ids:
        match what_about_to_notify.strip():
            case 'D':
                mes = """Удалено, блин!"""
                await bot.send_message(tg, mes)
                print("notification sent: ", mes)
            case 'I':
                mes = """Новая задача, пойди глянь!"""
                await bot.send_message(tg, mes)
                print("notification sent: ", mes)
            case 'U_executor':
                mes = """Ничего себе, у задачи новый исполнитель, пора проверить!"""
                await bot.send_message(tg, mes)
                print("notification sent: ", mes)
            case 'U_status':
                mes = """Новый статус!"""
                await bot.send_message(tg, mes)
                print("notification sent: ", mes)
            case 'U_deadline':
                mes = """Похоже срок задачи изменился, глянь."""
                await bot.send_message(tg, mes)
                print("notification sent: ", mes)
            case 'U_header':
                mes = """Новый заголовок у твоей задачи"""
                await bot.send_message(tg, mes)
                print("notification sent: ", mes)
            case 'U_mentor':
                mes = """Новый наставник"""
                await bot.send_message(tg, mes)
                print("notification sent: ", mes)
            case 'U_body':
                mes = """Описание задачи изменилось!"""
                await bot.send_message(tg, mes)
                print("notification sent: ", mes)
            case 'U':
                mes = """Твоя задача изменилась, проверь."""
                await bot.send_message(tg, mes)
                print("notification sent: ", mes)
            case _ :
                print("default_case in notifications")


async def is_user_registered(user_id: str) -> bool:
    conn = await new_connection()
    with conn.cursor() as cursor:
        sql_code = f"""SELECT telegram FROM
        "Users" WHERE telegram = '{user_id}';"""
        cursor.execute(sql_code)
        if cursor.fetchone() is None:
            print("user is NOT registered")
            return False
        else:
            print("user is registered")
            return True


async def register_user(user_id: str, username: str, phone_number: str):
    conn = await new_connection()
    with conn.cursor() as cursor:
        sql_code = """UPDATE "Users" SET "telegram"=%s WHERE "telephone"=%s"""
        cursor.execute(sql_code, (user_id, phone_number,))
        conn.commit()
        print("successfully inserted")


async def get_user_telegram_id_from_users_table(id: str) -> str:
    conn = await new_connection()
    with conn.cursor() as cursor:
        sql_code = """SELECT "telegram" FROM "Users" WHERE id = %s;"""
        cursor.execute(sql_code, id)
        user_id = cursor.fetchone()
        print(user_id)
        return user_id


def get_digits_from_sql_fetch(str: str) -> str:
    res: str = ""
    for char in str:
        if char.isdigit():
            res += char
    return res

# Принимает на входе строку формата "11 22 33 44" и
# возвращает список с отдельными числами как элементами
def get_list_from_string(str: str) -> list:
    str = str.strip()
    res: list = ['']
    cur: int = 0
    for char in str:
        if char ==' ':
            res.append('')
            cur+=1
            continue
        res[cur]+=char
    return res

# if __name__ == '__main__':
    # asyncio.run(check_new_row())
    # asyncio.run(register_user("user_id", "username", "phone_number"))
