# Metis: SCOPE Machine Learning Data Collector
Web app allowing collection of user input on various KPI evolutions determining whether or not the last point should be considered an alert. Collected data will be used for training and testing machine learning algorithms to trigger alerts.

## What's in a name?
> Metis (Μῆτις, "wisdom," "skill," or "craft"), in ancient Greek religion, was a mythological character belonging to the Titan generation. [...] By the era of Greek philosophy in the 5th century BC, Metis had become the mother of wisdom and deep thought, [...] the embodiment of "prudence", "wisdom" or "wise counsel" [...] The Greek word metis meant a quality that combined wisdom and cunning. -- [Source](https://en.wikipedia.org/wiki/Metis_(mythology))

## Requirements
Python 3, Flask, SQLAlchemy, Pandas, pyyaml

## Disclaimers
- Note that this has been modified from its original state to not contain any sensitive data. You can infer how the database looks by looking at the classes in metis/models.py; however, no database is available for testing this version of the data.
- This web app was created to work inside of a project for spawning Docker containers (hence the Dockerfile); however, that code will not be provided here either.

## Screenshots
|Login|New User|
| :---: | :---: |
|<img src="Metis%20Screenshots/metis_login.png?raw=true" align="center" width="450" alt="Metis Login">|<img src="Metis%20Screenshots/metis_new_user.png?raw=true" align="center" width="450" alt="Metis New User">

|Instructions|Classify KPI Evolution|
| :---: | :---: |
|<img src="Metis%20Screenshots/metis_instructions_still.png?raw=True" align="center" width="450" alt="Metis Instructions">|<img src="Metis%20Screenshots/metis_classification_page.png?raw=true" align="center" width="450" alt="Metis Classify">

|Record Email Submission|Logout|
| :---: | :---: |
|<img src="Metis%20Screenshots/metis_email_submission.png?raw=true" align="center" width="450" alt="Metis Accept Email Submission">|<img src="Metis%20Screenshots/metis_logout.png?raw=true" align="center" width="450" alt="Metis Logout">|

|Leaderboard (Logged In)|Leaderboard (Logged Out)|
| :---: | :---: |
|<img src="Metis%20Screenshots/metis_leaderboard.png?raw=true" align="center" width="450" alt="Metis Leaderboard when logged in">|<img src="Metis%20Screenshots/metis_leaderboard_not_logged_in.png?raw=true" align="center" width="450" alt="Metis Leaderboard when logged out">|

|FAQ Cards|FAQ Cards Revealed|
| :---: | :---: |
|<img src="Metis%20Screenshots/metis_faq_closed.png?raw=true" align="center" width="450" alt="Metis FAQ">|<img src="Metis%20Screenshots/metis_faq_expanded_blue_theme.png?raw=true" align="center" width="450" alt="Metis FAQ cards revealed.">
