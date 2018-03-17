from sqlalchemy import Column, Table, Integer, Float, String, Date, DateTime, Boolean
from datetime import datetime

# get the declarative base from __init__.py
try:
  from __main__ import Base
except ImportError:
  from __init__ import Base
  
# define tables
class KpiEvolution(Base):
  __tablename__ = 'kpi_evolutions'
  __table_args__ = {'schema' : 'alerts'}
  series = Column('series', String, primary_key=True, nullable=False)
  client_name = Column('client_name', String, primary_key=True)
  client_id = Column('client_id', Integer, primary_key=True)
  global_account_name = Column('global_account_name', String, primary_key=True)
  RTC_vertical = Column('RTC_vertical', String, primary_key=True)
  vertical_name = Column('vertical_name', String, primary_key=True)
  partner_id = Column('partner_id', Integer, primary_key=True)
  partner_name = Column('partner_name', String, primary_key=True)
  campaign_id = Column('campaign_id', Integer, primary_key=True)
  campaign_name = Column('campaign_name', String, primary_key=True)
  campaign_scenario = Column('campaign_scenario', String, primary_key=True)
  campaign_type_name = Column('campaign_type_name', String, primary_key=True)
  campaign_revenue_type = Column('campaign_revenue_type', Integer, primary_key=True)
  campaign_funnel_id = Column('campaign_funnel_id', Integer, primary_key=True)
  cost_center = Column('cost_center', String, primary_key=True)
  ranking = Column('ranking', String, nullable=False, primary_key=True)
  country = Column('country', String, nullable=False, primary_key=True)
  subregion = Column('subregion', String, nullable=False, primary_key=True)
  region = Column('region', String, nullable=False, primary_key=True)
  site_type = Column('site_type', String, primary_key=True)
  event_name = Column('event_name', String, primary_key=True)
  day = Column('day', Date, primary_key=True)
  run_date = Column('run_date', Date, primary_key=True)
  kpi = Column('kpi', String, primary_key=True)
  value = Column('value', Float)

class Classification(Base):
  __tablename__ = 'classifications'
  __table_args__ = {'schema' : 'alerts'}
  series = Column('series', String, primary_key=True, nullable=False)
  run_date = Column('run_date', Date, primary_key=True)
  kpi = Column('kpi', String, primary_key=True)
  is_alert = Column('is_alert', Boolean)
  
class FilesWritten(Base):
  __tablename__ = 'files_already_used'
  __table_args__ = {'schema' : 'alerts'}
  file_name = Column('file_name', String, primary_key=True, nullable=False)

class Logs(Base):
  __tablename__ = 'classification_logs'
  __table_args__ = {'schema' : 'alerts'}
  source = Column('source', String, primary_key=True, nullable=False)
  username = Column('username', String, primary_key=True, nullable=False)
  datetime = Column('datetime_utc', DateTime, primary_key=True, nullable=False)
  series = Column('series', String, primary_key=True, nullable=False)
  client_id = Column('client_id', Integer, primary_key=True)
  partner_id = Column('partner_id', Integer, primary_key=True)
  campaign_id = Column('campaign_id', Integer, primary_key=True)
  cost_center = Column('cost_center', String, primary_key=True)
  ranking = Column('ranking', String, nullable=False, primary_key=True)
  country = Column('country', String, nullable=False, primary_key=True)
  subregion = Column('subregion', String, nullable=False, primary_key=True)
  region = Column('region', String, nullable=False, primary_key=True)
  site_type = Column('site_type', String, primary_key=True)
  event_name = Column('event_name', String, primary_key=True)
  run_date = Column('run_date', Date, primary_key=True)
  kpi = Column('kpi', String, primary_key=True)
  is_alert = Column('is_alert', Boolean)

  def __init__(self, source, username, series, run_date, kpi, is_alert, \
  client_id = None, partner_id = None, campaign_id = None, cost_center = None, ranking = None, \
  country = None, subregion = None, region = None, site_type = None, event_name = None):
    self.source = source.lower()
    self.username = username
    self.datetime = datetime.now()
    self.series = series
    self.run_date = run_date
    self.kpi = kpi
    self.is_alert = is_alert
    self.client_id = client_id or -11
    self.partner_id = partner_id or -1
    self.campaign_id = campaign_id or -1
    self.cost_center = cost_center or 'UNKNOWN'
    self.ranking = ranking or 'UNKNOWN'
    self.country = country or 'UNKNOWN'
    self.subregion = subregion or 'UNKNOWN'
    self.region = region or 'UNKNOWN'
    self.site_type = site_type or 'N/A'
    self.event_name = event_name or 'N/A'

class User(Base):
  __tablename__ = 'users'
  __table_args__ = {'schema' : 'alerts'}
  username = Column('username', String, primary_key=True, nullable=False)
  team = Column('team', String)
  region = Column('region', String)
