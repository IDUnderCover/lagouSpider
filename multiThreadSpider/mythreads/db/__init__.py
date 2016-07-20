from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base


_Base = declarative_base()
_postgre_url = 'postgresql://dbuser:zettage@localhost:5432/lagoudb'
_engine = create_engine(_postgre_url, encoding='utf-8')

from . import mymodels
_Base.metadata.create_all(_engine)

db_session = sessionmaker(_engine)

