#!/usr/bin/python
# -*- coding:utf8 -*-

import sqlite3
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, JSONB
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

sqlite_string = 'sqlite:///:memory:'
connection_string = 'postgresql://dbuser:zettage@localhost:5432/lagoudb'

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    def __repr__(self):
       return "<User(name='%s', fullname='%s', password='%s')>" % (
                            self.name, self.fullname, self.password)


def create_table():
    tbl = sqlalchemy.Table("jsontable", meta,
                     Column('id', Integer),
                     Column('name', Text),
                     Column('email', Text),
                     Column('doc', JSON))
    meta.create_all()
    return tbl



# SQLAlchemy has two layers - the core and the ORM.

if __name__ == '__main__':
    print 'version:', sqlalchemy.__version__

    db = create_engine(connection_string, echo=True, encoding='utf-8')
    print dir(db)
    engine = db.connect()
    meta = sqlalchemy.MetaData(engine)
    result = engine.execute("SELECT 1")
    print(result.rowcount)
    j_table = create_table()
    statement = j_table.insert().values(
        id=3,
        name="MR. params",
        email="user@go.com",
        doc={
            "dialect": "params",
            "address": {"street": "Main St.", "zip": 12345}
        }
    )
    engine.execute(statement)
    print str(statement)

    find_user = j_table.select().where(j_table.c.name == "MR. params")
    engine.execute(find_user).fetchone()

    # 在 PostgreSQL 中, 我们使用  ->> 操作符 where doc->>'dialect' = 'params'
    # 在 SQLAlchemy 中, 我们必须使用 j_table.c.doc['dialect'].astext == 'params'


    find_zip = j_table.select().where(
        j_table.c.doc[
            ('address', 'zip')   # path to the key
        ].cast(
            sqlalchemy.Integer
        ) == 12345
    )

    print engine.execute(find_user).fetchall()

# https://www.compose.com/articles/using-json-extensions-in-postgresql-from-python-2/

