#!/usr/bin/python
# -*- coding: utf8 -*-

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()
postgre_url = 'postgresql://dbuser:zettage@localhost:5432/lagoudb'
engine = create_engine(postgre_url, encoding='utf-8')
Base.metadata.create_all(engine)
Session = sessionmaker(engine)

class Position(Base):
    __tablename__ = 'positions'
    id = Column(Integer, primary_key=True)
    keyword = Column(String)
    # time stamp
    time = Column(Integer)
    doc = Column(JSONB)

    def __repr__(self):
        return "<Position(id='%d', keyword='%s', time='%d', doc='%s')>" % (
            self.id, self.keyword, self.time, self.doc)


def create_table():
    Base.metadata.create_all(engine)




if __name__ == '__main__':
    # make sure the table is created
    create_table()
    # configure session maker

    # instantiate a session
    session = Session()

    # create a position instance
    import json, time
    data = json.loads('{"orderBy": 38, "leaderName": "\u9093\u5fb3\u6e90", "relScore": 156, "calcScore": false, "companySize": "15-50\u4eba", "appShow": 204, "deliverCount": 0, "countAdjusted": false, "flowScore": 160, "positionName": "\u4e91\u5e73\u53f0(Kubernetes/Docker\u5bb9\u5668\u65b9\u5411)\u9ad8\u7ea7\u5de5\u7a0b\u5e08", "education": "\u672c\u79d1", "financeStage": "\u521d\u521b\u578b(\u5929\u4f7f\u8f6e)", "pvScore": 22.101973189144726, "city": "\u676d\u5dde", "companyLogo": "i/image/M00/00/53/Cgp3O1ZBgPOAGbSmAAHP3OBSoDc260.jpg", "createTimeSort": 1467609449000, "district": "\u6ee8\u6c5f\u533a", "companyId": 85122, "industryField": "\u4f01\u4e1a\u670d\u52a1 \u00b7 \u6570\u636e\u670d\u52a1", "createTime": "2016-07-04 13:17:29", "adjustScore": 0, "score": 453, "publisherId": 2044322, "loginTime": 1467891890000, "formatCreateTime": "2016-07-04", "showOrder": 0, "positionId": 1170730, "workYear": "3-5\u5e74", "companyName": "CaiCloud", "jobNature": "\u5168\u804c", "positonTypesMap": null, "totalCount": 0, "positionFirstType": "\u6280\u672f", "adWord": 0, "companyLabelList": ["\u80a1\u7968\u671f\u6743", "\u4e13\u9879\u5956\u91d1", "\u5e26\u85aa\u5e74\u5047", "\u7ee9\u6548\u5956\u91d1"], "salary": "20k-40k", "randomScore": 0, "companyShortName": "\u676d\u5dde\u624d\u4e91\u79d1\u6280\u6709\u9650\u516c\u53f8", "showCount": 52, "businessZones": null, "haveDeliver": false, "hrScore": 100, "plus": "\u5426", "positionType": "\u540e\u7aef\u5f00\u53d1", "searchScore": 0.0, "positionAdvantage": "\u85aa\u8d44\uff0b\u671f\u6743", "imstate": "disabled", "approve": 1}')

    pos = Position(
        keyword='docker',
        time=time.time(),
        doc=data
    )
    session.add(pos)
    session.commit()

