#Foreign Influence

This project is the data-entry and scraping scripts that generate an API and will power a Foreign Influence Explorer website. See the front-facing app [here](https://github.com/sunlightlabs/bulgogi).

Foreign Influence Explorer documents some of the ways foreign entities influence U.S. policy and opinions. The two main datasets are the Department of Justice's Foreign Agent Registration Act(FARA) and press releases from The Defense Security Cooperation Agency(DSCA) records. 

##FARA Records

The management command create_feed, in the fara_feed app, scrapes the PDFs from the DOJ. Web forms in the FaraData app create pages for people to normalize the data according to instructions. The project uses a sql database. The data can be accesses through the API and RSS feeds. 

##DSCA Records

The arms_sales app scrapes press releases from the DSCA for proposed arms sales. These sales are purposed and may not happen, but these documents can add context to some of the lobbying that is visible in the FARA dataset. 


##Hacking

**To set up this project to scrape FARA feeds locally:**

1. Create a virtual environment (specify python2.7)

2. In your virtual environment, run pip install -r requirements.txt

3. In fara_feed/management/commands/ add an empty file called __init__.pyc

4. In fara/ create the file local_settings.py

5. Add the following to local_settings.py:
    a) SECRET_KEY="something"
    b) ES_CONFIG={}

6. If mysql is not installed, install it

7. Create a mysql database called FaraData.

8. Run python manage.py syncdb

9. Run python manage.py migrate

10. If elasticsearch is not installed, install it and make sure a server is running. The setting in 5(b) above works with a default Elasticsearch server configuration.

11. Run python manage.py create_feed

12. Run python manage.py arms_sales_archive



**To get the site and API running:**

1. Add the following to local_settings.py:
    a) API_PASSWORD="apikey" # or whatever you want, you'll need it to hit your local API
    b) apikey="" # this is never used

2. If you'll be poking around, it's probably worth setting DEBUG=True in local_settings.py

3. Run python manage.py runserver

4. You should now be able to access the site at localhost:8000

5. If you want to access the API, you'll need to pass the parameter key=apikey where apikey is whatever you set in local settings. For example:

```
http://localhost:8000/api/proposed-arms?key=apikey.
```

Find available endpoints in api/urls.py


**To incorporate historical information on principals into the database**
This feature is new and has no visible front-end component yet. It draws on an historical source to incorporate additional machine-readable information on principals into existing client records, defaulting to older manually entered data if it exists. The process uses two distinct commands in order to separate scraping (historical_feed) and merging into the database (merge_feeds) while we're confirming that the process is not destructive to old data (thus far it appears to be fine).

To add historical data to the database:

1. Run ```python manage.py historical_feed```
2. Run ```python manage.py merge_feeds```

Tests to check that the process maintains the integrity of older data can be run with ```/manage.py test FaraData```

---

This is project is under construction. If you are interested in contributing in some way email contact@sunlightfoundation.com