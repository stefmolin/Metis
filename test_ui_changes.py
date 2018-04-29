import pandas as pd
from flask import Flask, render_template, redirect, url_for, request, session, flash, escape, Markup
app = Flask(__name__)
app.secret_key = 'Hablando del rey de Roma por la puerta asoma'

@app.route("/")
@app.route("/login", methods=['POST', 'GET'])
def login():
  return render_template('login.html')

@app.route("/new_user", methods=['POST', 'GET'])
def new_user():
  return render_template('new_user.html')

@app.route("/not_supported")
def not_supported_team():
  return render_template('not_supported.html', username='cs.user', team='CS')

@app.route("/faq")
def show_faq():
  return render_template('faq.html')

@app.route("/logout")
def logout(switch_user=0):
  return render_template('logout.html', username='s.molin')

@app.route("/intro")
def intro():
  return render_template('instructions.html')

@app.route("/classification", methods=['GET', 'POST'])
def classify():
    return render_template('classification.html', \
      kpi_data=pd.DataFrame({'day' : ['2018-04-01', '2018-04-02','2018-04-03','2018-04-04','2018-04-05','2018-04-06','2018-04-07','2018-04-08','2018-04-09'],
                            'value' : [0.01, 0.02, 0.01, 0.05, 0.08, 0.04, 0.01, 0.01, 0.3]}), user_team='AS', kpi='ctr')

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html', username='s.molin')

@app.route('/leaderboard')
def leaderboard():
    session['username'] = 'me'
    return render_template('leaderboard.html', rankings=pd.DataFrame({ 'source' : ['web_app'] * 7 + ['email'] * 7,
                                                                        'rank' : [1, 2, 3, 4, 5, 10, 17000, 1, 2, 3, 4, 5, 17, 210000],
                                                                        'username' : ['s.molin', 'f.last', 'fm.last', 'j.doe', 'ja.doe', 't.smith'] * 2 + ['you', 'me'],
                                                                        'responses' : [1105, 1005, 995, 900, 877, 201, 101, 35, 33, 21, 17, 7, 4, 3]}))

@app.route('/email_submission', methods=['GET'])
def email_submission():
  return render_template('email_submission.html')

app.run(debug=True)
