from flask import Flask, render_template, redirect, url_for, request, session, flash, escape, Markup
from metis.security import is_valid_user
from datetime import datetime
import os
import logging
try:
  from __main__ import app
except ImportError:
  from __init__ import app
try:
  from __main__ import metis_db
except ImportError:
  from __init__ import metis_db

logger = logging.getLogger('MetisApp')

def clear_session(exhausted_kpi_evolutions=False):
  if os.environ.get('DEPLOYMENT_ENVIRONMENT') == 'testing':
    # if we are testing, clear all the session variables
    for key in list(session):
     session.pop(key, None)
  else:
    # production environment, just clear username for logout
    session.pop('username', None)
    session.pop('team', None)
    # also pop 'exhausted_kpi_evolutions' if the user was logged out bc no more combos were available
    if exhausted_kpi_evolutions:
      session.pop('exhausted_kpi_evolutions', None)

def assign_kpi_evolution(metis_db):
  # get random KPI evolution
  to_classify = metis_db.select_random_kpi_evolution(session['team'])

  # debug what was pulled
  logger.debug('Selected row:')
  logger.debug(to_classify)

  # store that user's current task in the session
  session['series'] = to_classify['series']
  session['run_date'] = to_classify['run_date']
  session['kpi'] = to_classify['kpi']
  session['client_id'] = int(to_classify['client_id'])
  session['partner_id'] = int(to_classify['partner_id'])
  session['campaign_id'] = int(to_classify['campaign_id'])
  session['cost_center'] = to_classify['cost_center']
  session['ranking'] = to_classify['ranking']
  session['country'] = to_classify['country']
  session['subregion'] = to_classify['subregion']
  session['region'] = to_classify['region']
  session['site_type'] = to_classify['site_type']
  session['event_name'] = to_classify['event_name']

  # debug the types of everything
  for key, value in session.items():
    logger.debug('Field {key} with value {value} is of type {field_type}'.format(key=key, value=value, field_type=type(value)))

@app.route("/")
@app.route("/login", methods=['POST', 'GET'])
def login():
  # check if the user already has a session
  if 'username' in session:
    # flash(Markup('Logged in as {user}. <a href="{switch}">Not you?</a>'.format(user=escape(session['username']), switch=url_for('logout', switch_user=1))))
    return redirect(url_for('classify'))
  else:
    # no session detected, show log in
    error = None
    if request.method == 'POST':
      username = request.form['username'].split("@")[0]
      if is_valid_user(login=username, password=request.form['password']):
        # successful login, set session
        logger.info('{user} has logged in'.format(user=username))
        session['username'] = username

        # check if the user has a team already
        if 'team' not in session:
          team_in_db = metis_db.get_user_team(session['username'])
          if team_in_db:
            session['team'] = team_in_db
          else:
            # if the session doesn't have a team or the user doesn't have a team in the database
            return redirect(url_for('new_user'))

        if session['team'] in ['AS', 'AX', 'TS']:
          # show instructions if not seen recently otherwise go to classify
          if 'has_read_instructions' in session:
            return redirect(url_for('classify'))
          else:
            return redirect(url_for('intro'))
        else:
          # we don't have KPI evolutions for other teams to classify so log them out
          return redirect(url_for('not_supported_team'))
      else:
        # unsuccessful login attempt, display error and allow another attempt
        error = 'Wrong username/password. Please try again.'
        return render_template('login.html', error=error)
    else:
      return render_template('login.html')

@app.route("/new_user", methods=['POST', 'GET'])
def new_user():
  if 'username' in session:
    if 'team' in session:
      # team has already been added to the session (from login)
      if 'has_read_instructions' in session:
        return redirect(url_for('classify'))
      else:
        return redirect(url_for('intro'))
    else:
      if request.method == 'POST':
        # add team to the session
        session['team'] = request.form['team']

        # add this user + team relationship to the database so we don't ask again
        metis_db.add_new_user(username=session['username'], team=session['team'], \
          region=request.form['region'])

        if session['team'] in ['AS', 'AX', 'TS']:
          # take user to the instructions page
          return redirect(url_for('intro'))
        else:
          # we don't have KPI evolutions for other teams to classify so log them out
          return redirect(url_for('not_supported_team'))
      else:
        # prompt user for their team (GET request to the new_user page from the login page)
        logger.info('{user} is new to Metis. Collecting team info...'.format(user=session['username']))
        return render_template('new_user.html')
  else:
    # user needs to log in, to get to this page
    return redirect(url_for('login'))

@app.route("/not_supported")
def not_supported_team():
  if 'username' not in session:
    return redirect(url_for('login'))
  else:
    username = session['username']
    team = session['team']

    # logging user out
    clear_session()
    logger.info('Logging out {team} user {user} since we have no support for {team} classifications.'.\
      format(team=team, user=username))
    return render_template('not_supported.html', username=username, team=team)

@app.route("/faq")
def show_faq():
  # allow FAQ page to be accessed regardless of being logged in
  if 'username' in session:
    username = session['username']
  else:
    username = 'anonymous user'
  logger.info('{user} accessed the FAQ page'.format(user=username))
  return render_template('faq.html')

@app.route("/logout")
@app.route("/logout/<int:switch_user>")
def logout(switch_user=0):
  if 'username' in session:
    username = session['username']
    if switch_user:
      # if switching the user, clear the session and redirect to login page
      clear_session()
      logger.info('{user} is switching logins'.format(user=username))
      return redirect(url_for('login'))
    else:
      # if not switching the user, clear the session if it exists
      clear_session()
      logger.info('{user} logged out'.format(user=username))
      return render_template('logout.html', username=username)
  else:
    return redirect(url_for('login'))

@app.route("/intro")
def intro():
  if 'username' not in session:
    return redirect(url_for('login'))
  else:
    logger.info('Showing instructions to user {user}.'.format(user=session['username']))

    return render_template('instructions.html')

@app.route("/classification", methods=['GET', 'POST'])
def classify():
  if 'username' in session:
    # check if the user has a team already
    if 'team' not in session:
      team_in_db = metis_db.get_user_team(session['username'])
      if team_in_db:
        session['team'] = team_in_db
      else:
        # if the session doesn't have a team or the user doesn't have a team in the database
        return redirect(url_for('new_user'))

    # note that user has finished the instructions at least once
    if 'has_read_instructions' not in session:
      session['has_read_instructions'] = True

    # collect response
    if request.method == 'POST':

      # log past response
      metis_db.record_classification(source='web_app', username=session['username'], series=session['series'], \
        run_date=session['run_date'], kpi=session['kpi'], is_alert=request.form['is_alert'], client_id=session['client_id'], \
        partner_id=session['partner_id'], campaign_id=session['campaign_id'], cost_center=session['cost_center'], \
        ranking=session['ranking'], country=session['country'], subregion=session['subregion'], region=session['region'], \
        site_type=session['site_type'], event_name=session['event_name'])

    # get random selection and store in the session for that user:
    logger.info('Getting a KPI evolution for {user}...'.format(user=session['username']))
    for _ in range(5):
      # try 5 times to get one they haven't classified already
      assign_kpi_evolution(metis_db)
      if not metis_db.is_already_classified_by_user(username=session['username'], \
        series=session['series'], kpi=session['kpi'], run_date=session['run_date']):
          # found a combo that the user is eligible to classify (they haven't classified it already)
          break
      logger.info('{user} has already classified the selected combination'.\
        format(user=session['username']))
    else:
      # failed to find a new KPI evolution for the user to classify
      logger.info("Unable to find a combination that {user} hasn't classified. Logging {user} out.".\
        format(user=session['username']))
      session['exhausted_kpi_evolutions'] = True
      return redirect(url_for('thank_you'))

    # show next KPI evolution to classify
    return render_template('classification.html', \
      kpi_data=metis_db.get_kpi_data(run_date=session['run_date'], kpi=session['kpi'], \
        series=session['series']), user_team=session['team'], kpi=session['kpi'])
  else:
    return redirect(url_for('login'))

@app.route('/thank_you')
def thank_you():
  # alternate logout page for users that can't classify anymore; can't be accessed, only redirects
  if 'exhausted_kpi_evolutions' in session:
    username = session['username']
    clear_session(exhausted_kpi_evolutions=True)
    logger.info('{user} has been successfully logged out'.format(user=username))
    return render_template('thank_you.html', username=username)
  else:
    # block from users not logged in
    return redirect(url_for('login'))

@app.route('/email_submission', methods=['GET'])
def email_submission():
  username = request.args.get('username')
  series = request.args.get('series')
  client_id = request.args.get('client_id')
  partner_id = request.args.get('partner_id')
  campaign_id = request.args.get('campaign_id')
  cost_center = request.args.get('cost_center')
  ranking = request.args.get('ranking')
  country = request.args.get('country')
  subregion = request.args.get('subregion')
  region = request.args.get('region')
  site_type = request.args.get('site_type')
  event_name = request.args.get('event_name')
  run_date = request.args.get('run_date')
  kpi = request.args.get('kpi')
  is_alert = request.args.get('is_alert')

  if not username or not series or not kpi or not run_date or is_alert is None:
    return redirect(url_for('login'))
  else:
    metis_db.record_email_response(username=username, series=series, run_date=run_date, kpi=kpi,
                                   is_alert=is_alert, client_id=client_id, partner_id=partner_id,
                                   campaign_id=campaign_id, cost_center=cost_center, ranking=ranking,
                                   country=country, subregion=subregion, region=region,
                                   site_type=site_type, event_name=event_name)
    logger.info('Recording response from {user}: {series} for {kpi} on {run_date} is {response} an alert'.\
                format(user=username, series=series, kpi=kpi, run_date=run_date, response='' if is_alert else 'not'))
  return render_template('email_submission.html')

@app.route('/db_connection_healthcheck', methods=['GET', 'POST'])
def db_connection_healthcheck():
  metis_db.test_connection()
  return 'ok'
