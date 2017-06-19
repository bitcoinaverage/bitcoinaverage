03/12/2015

This version of the reposisitory will remain "as-is" going forward. Many changes have been made privately to this version. The repository is working but will no longer be maintained.
------------------------------------------------------------------------------------

19/06/2017

Version 2 of our API has now been running for around 9 months, as such Version 1 of the API has been switched off.

All bitcoin, ethereum, litecoin, ripple price data is freely available.

Documentation: https://apiv2.bitcoinaverage.com/
Register: https://bitcoinaverage.com/en/register
Homepage: https://bitcoinaverage.com/


------------------------------------------------------------------------------------
*this is the source of BitcoinAverage.com website*

*licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Public License*

run instructions
---------------------
- download sources
- copy server.py.dist into server.py in the same folder and setup paths to folders (see comments in the file).
- install dependencies with `sudo apt-get install python-dev libevent-dev libxml2-dev python-pip libxslt1-dev redis-server && sudo apt-get build-dep libxml2 && sudo pip install SQLObject eventlet requests libxslt-dev lxml redis simplejson`
- to run the api_daemon.py you need python 2.7, no db or other storage engines needed. Install any other missing dependencies if needed.

system structure
--------------------
There are several \*_daemon.py files in the project root folder - these are parts of the backend that make whole thing work. Despite "daemon" name these are not real system daemons yet (there is an outstanding task in github for that).  
Daemons are:
- /api_daemon.py - main script, it loads all settings from bitcoinaverage/config.py, queries all external exchanges APIs, creates bitcoinaverage own API and regenerates API files (except for history part). 
- /history_daemon.py - fetches current data from live API and generates history API csv files. It uses HTTP to fetch API data so it can seamlessly run on separate server if needed.
- /twitter_daemon.py - sends updates to twitter.
- /image_daemon.py - generates price images (I wonder if anybody uses these images)
- /monitor_daemon.py - monitors last update timestamps for api and history daemons, triggers email alerts if timestamp is older than 5 min.
- /api folder - stores all API files. Yes, whole bitcoinaverage API is read only and based on static JSON files generated by api_daemon and served by nginx. Simple, but very high performance (only bandwidth is the limit). whole contents of this folder is generated automatically, just configure server.py and run api_daemon.
This folder must be web accessible as web API.
- /www folder - actual website. Static, must be web accessible. Files in /www/charts/* and /www/currencies/* are generated automatically and are not meant to be user viewed. 


Whole frontend is JS-driven, it fetches JSON API via AJAX and renders the page. 


*Feel free to contact us at bitcoinaverage@gmail.com for with questions on any matters about this system and website.*



related thirdparty libraries
--------------------
- python calculator module - https://gist.github.com/miohtama/7814435
- ruby API wrapper - https://github.com/git-toni/bitcoinaverage
