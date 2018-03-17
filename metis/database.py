from sqlalchemy import create_engine, and_, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from metis import utils
from metis import models
import logging
from datetime import datetime
import pandas
from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)

class MetisDatabase(object):
    def __init__(self, db_uri, base, directory_dict, schema='alerts'):
        self.schema = schema
        self.engine = create_engine(db_uri, echo=False, poolclass=NullPool)
        self.session = Session(self.engine)
        self.Base = base
        self.combos = self.__get_combos_to_classify()
        self.AS_index_generator = self.__get_index_generator(team='AS')
        self.AX_index_generator = self.__get_index_generator(team='AX')
        self.TS_index_generator = self.__get_index_generator(team='TS')
        logger.info('Database connection initiated')

    def query_first(self, query):
        for _ in range(2):
            try:
                data = query.first()
                return data
            except OperationalError as e:
                last_error = e
                self.session.rollback()
        else:
            raise(last_error)

    def query_all(self, query):
        for _ in range(2):
            try:
                data = query.all()
                return data
            except OperationalError as e:
                last_error = e
                self.session.rollback()
        else:
            raise(last_error)

    def __get_combos_to_classify(self):
        data = self.query_all(
            self.session.query(
                models.KpiEvolution.series,
                models.KpiEvolution.kpi,
                models.KpiEvolution.run_date,
                models.KpiEvolution.client_id,
                models.KpiEvolution.partner_id,
                models.KpiEvolution.campaign_id,
                models.KpiEvolution.cost_center,
                models.KpiEvolution.ranking,
                models.KpiEvolution.country,
                models.KpiEvolution.subregion,
                models.KpiEvolution.region,
                models.KpiEvolution.site_type,
                models.KpiEvolution.event_name
                ).distinct())
        dataframe = pandas.DataFrame.from_records(
            data,
            columns=[
                'series',
                'kpi',
                'run_date',
                'client_id',
                'partner_id',
                'campaign_id',
                'cost_center',
                'ranking',
                'country',
                'subregion',
                'region',
                'site_type',
                'event_name'])
        dataframe['run_date'] = dataframe['run_date'].astype(str)
        return dataframe

    def get_kpi_data(self, run_date, kpi, series):
        data = self.query_all(
            self.session.query(
                models.KpiEvolution.day,
                models.KpiEvolution.value
            ).filter(
                models.KpiEvolution.run_date == datetime.strptime(
                    run_date,
                    '%Y-%m-%d'),
                models.KpiEvolution.kpi == kpi,
                models.KpiEvolution.series == series
            ).order_by(
                models.KpiEvolution.day
            ))
        dataframe = pandas.DataFrame.from_records(data, columns=['day', 'value'])
        dataframe['day'] = dataframe['day'].astype(str)
        return dataframe

    def __get_index_generator(self, team):
        if team == 'AS':
            kpi_list = ['spend',
                        'cos',
                        'ctr',
                        'cr',
                        'client_rext',
                        'clicks',
                        'displays',
                        'conversions',
                        'order_value']
        elif team == 'TS':
            kpi_list = ['site_events', 'tag_events']
        elif team == 'AX':
            kpi_list = ['territory_rext', 'tac', 'rext_euro', 'margin']
        else:
            raise ValueError("Only teams 'AS', 'AX', and 'TS' are supported")
        valid_combos = self.combos[self.combos['kpi'].isin(kpi_list)]
        data = self.query_all(
            self.session.query(
                models.Logs.username,
                models.Logs.series,
                models.Logs.run_date,
                models.Logs.kpi).distinct())
        already_classified = pandas.DataFrame.from_records(
            data,
            columns=['username', 'series', 'run_date', 'kpi'])
        already_classified = already_classified[
                already_classified['kpi'].isin(kpi_list)]
        already_classified['run_date'] = already_classified['run_date'].astype(str)
        not_yet_classified = utils.get_unclassified_indices(
            all_combos_df=valid_combos,
            classified_combos_df=already_classified)
        team_index_generator = utils.index_generator(
            index_list=list(valid_combos.index.values),
            use_first=not_yet_classified)
        return team_index_generator

    def select_random_kpi_evolution(self, team):
        if team == 'AS':
            random_index = next(self.AS_index_generator)
        elif team == 'TS':
            random_index = next(self.TS_index_generator)
        elif team == 'AX':
            random_index = next(self.AX_index_generator)
        else:
            raise ValueError("Only 'AS', 'AX', and 'TS' are supported.")
        random_row = self.combos.iloc[random_index].to_dict()
        return random_row

    def record_classification(self,
                              source,
                              username,
                              series,
                              run_date,
                              kpi,
                              is_alert,
                              client_id=None,
                              partner_id=None,
                              campaign_id=None,
                              cost_center=None,
                              ranking=None,
                              country=None,
                              subregion=None,
                              region=None,
                              site_type=None,
                              event_name=None):
        self.session.add(
                models.Logs(
                        source=source,
                        username=username,
                        series=series,
                        run_date=run_date,
                        kpi=kpi,
                        is_alert=is_alert,
                        client_id=client_id,
                        partner_id=partner_id,
                        campaign_id=campaign_id,
                        cost_center=cost_center,
                        ranking=ranking,
                        country=country,
                        subregion=subregion,
                        region=region,
                        site_type=site_type,
                        event_name=event_name))
        self.session.commit()

    def is_already_classified_by_user(self, username, series, kpi, run_date):
        check = self.query_first(
            self.session.query(models.Logs).filter(
                and_(
                    models.Logs.username == username,
                    models.Logs.series == series,
                    models.Logs.kpi == kpi,
                    models.Logs.run_date == run_date)
                ))
        if check:
            return True
        else:
            return False
            
    def record_email_response(self, username, series, kpi, run_date, is_alert, 
                              client_id=None, partner_id=None, campaign_id=None,
                              cost_center=None, ranking=None, country=None,
                              subregion=None, region=None, site_type=None,
                              event_name=None):
        source = 'email'
        check = self.query_first(
            self.session.query(models.Logs).filter(
                and_(
                    models.Logs.source == source,
                    models.Logs.username == username,
                    models.Logs.series == series,
                    models.Logs.kpi == kpi,
                    models.Logs.run_date == run_date)
                ))
        if check:
            check.is_alert = is_alert
            check.datetime = datetime.now()
            self.session.commit()
        else:
            self.record_classification(source=source, username=username, series=series, run_date=run_date,
                                       kpi=kpi, is_alert=is_alert, client_id=client_id, partner_id=partner_id,
                                       campaign_id=campaign_id, cost_center=cost_center, ranking=ranking,
                                       country=country, subregion=subregion, region=region, site_type=site_type,
                                       event_name=event_name)

    def add_new_user(self, username, team, region):
        user = models.User(username=username, team=team, region=region)
        self.session.add(user)
        self.session.commit()

    def get_user_team(self, user):
        team = self.query_first(
            self.session.query(
               models.User.team
            ).filter(
               models.User.username == user
            ))
        if team:
            team = team[0]
        return team

    def test_connection(self):
        self.session.query(models.User.team).first()

    def close_connections(self):
        self.engine.dispose
        self.session.close()
        logger.info('Database connection closed')
