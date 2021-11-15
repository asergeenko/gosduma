from sqlalchemy import create_engine, Column, MetaData, literal, select

from clickhouse_sqlalchemy import Table, make_session, get_declarative_base, types, engines

uri = 'clickhouse://default:jimmypage60@84.201.143.194/gosduma_3nf'

engine = create_engine(uri)
session = make_session(engine)
metadata = MetaData(bind=engine)

Base = get_declarative_base(metadata=metadata)

class Position(Base):
    __tablename__ = 'positions'
    id = Column(types.UInt64, primary_key=True)
    name = Column(types.String)

    __table_args__ = (
        engines.Memory(),
    )

class Faction(Base):
    __tablename__ = 'factions'
    id = Column(types.UInt64, primary_key=True)
    name = Column(types.String)

    __table_args__ = (
        engines.Memory(),
    )


class Deputy(Base):
    __tablename__ = 'deputies'
    id = Column(types.UInt64, primary_key=True)
    name = Column(types.String)
    is_current = Column(types.UInt8)    

    __table_args__ = (
        engines.Memory(),
    )

def get_positions():
    return session.query(Position).all()#session.execute(select(Position.name)).all()

def get_factions():
    return session.query(Faction).all()

def get_deputies_by_name_regex(regex):
    return session.execute(r"select name,id from deputies where match(name,'(?i)%s')"%(regex))

def get_laws_by_deputy(deputy_id, regex):
    return session.execute(r"select votes.id, laws.name, laws.comments, toDate(votes.date),"
                           r"votes.for, votes.against, votes.abstain, votes.absent,"
                           r"vote_results.name from laws,"
                            r"votes,votes_deputies, vote_results where votes.law_id = laws.id and "
                            r"votes.id=votes_deputies.vote_id and votes_deputies.deputy_id=%d and "
                            r"vote_results.id = votes_deputies.result_id and"
                           r"(match(laws.name, '(?i)%s') or match(laws.comments, '(?i)%s'))"
                           r"order by last_event_date desc"%(deputy_id,regex,regex))

def get_law_by_id_for_deputy(deputy_id, law_id):
    return session.execute(r"select votes.id, laws.name, laws.comments, toDate(votes.date),"
                           r"votes.for, votes.against, votes.abstain, votes.absent,"
                           r"vote_results.name from laws,"
                           r"votes,votes_deputies, vote_results where votes.law_id = laws.id and "
                           r"votes.id=votes_deputies.vote_id and votes_deputies.deputy_id=%d and "
                           r"vote_results.id = votes_deputies.result_id and laws.id=%s "
                           r"order by last_event_date desc" % (deputy_id,law_id))

def get_laws_by_faction(faction_id, regex):
    return session.execute(r"select votes.id, laws.name, laws.comments, toDate(votes.date),"
                           r"votes.for, votes.against, votes.abstain, votes.absent,"
                           r"votes_factions.total, votes_factions.for, votes_factions.against,"
                           r"votes_factions.abstain, votes_factions.absent from laws,"
                            r"votes,votes_factions "
                            r"where votes.law_id = laws.id and "
                            r"votes.id=votes_factions.vote_id and votes_factions.faction_id=%d and "                            
                           r"(match(laws.name, '(?i)%s') or match(laws.comments, '(?i)%s'))"
                           r"order by last_event_date desc"%(faction_id,regex,regex))

def get_law_by_id_for_faction(faction_id, law_id):
    return session.execute(r"select votes.id, laws.name, laws.comments, toDate(votes.date),"
                           r"votes.for, votes.against, votes.abstain, votes.absent,"
                           r"votes_factions.total, votes_factions.for, votes_factions.against,"
                           r"votes_factions.abstain, votes_factions.absent from laws,"
                            r"votes,votes_factions "
                            r"where votes.law_id = laws.id and laws.id=%s and "
                            r"votes.id=votes_factions.vote_id and votes_factions.faction_id=%d "
                           r"order by last_event_date desc"%(law_id,faction_id))