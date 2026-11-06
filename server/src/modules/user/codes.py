import sqlalchemy as sa
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert


def allocate_user_code(connection) -> str:
    from src.modules.user.models import UserCodeCounter

    counter = UserCodeCounter.__table__
    # 测试库直接用 ORM 建表，首次发号时补上计数行。
    if connection.dialect.name == "mysql":
        statement = mysql_insert(counter).values(id=1, next_value=1).on_duplicate_key_update(id=1)
    else:
        statement = sqlite_insert(counter).values(id=1, next_value=1).on_conflict_do_nothing(index_elements=["id"])
    connection.execute(statement)
    number = connection.execute(sa.select(counter.c.next_value).where(counter.c.id == 1).with_for_update()).scalar_one()
    connection.execute(counter.update().where(counter.c.id == 1).values(next_value=number + 1))
    return f"lw{number:03d}"
