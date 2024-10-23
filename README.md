# JobSpi

- This is the initial release and more or less a 'beta' version. Cleaning up the script and output is on the TODO list, as well as more parsing to accuratly get data for identified users. The JSON is a little crazy so taking some time.

- The script will ask for options when you dont supply any. This includes that password field, which wont show when typing, and thus is better for screenshots and evidence gathering.

- Please mark any issues in the proper github way and ill attempt to address them.

- The system you are running this script from needs to have successfully logged into LinkedIn via web browser with the account you are using. 

- LinkedIn does throttle the amount of login attempts, so running this multiple times may get you throtteled and unable to execute for 24 hours.

------------------------------------------------------------------------------------

# Usage

```
$ python3 JobSpi.py -h

     ___.     ___.     ________     .__
    |   | ____\_ |__  /  _____/____ |__|
    |   |/  _ \| __ \ \____  \   _ \|  |
/\__|   (  (_) ) \_\ \/       \ |_) |  |
\_______|\____/|___  /______  /  __/|__|
   v0.3            \/       \/|_|
        Author: #Waffl3ss

usage: JobSpi.py [-h] [-c COMPANY] [-u LINKEDIN_USERNAME] [-p LINKEDIN_PASSWORD] [-o OUTPUTFILE] [-pn] [-id COMPANYID] [--sleep SLEEP] [--timeout TIMEOUT] [--logretry LOGINRETRYAMOUNT] [--secretry LINKEDINRETRYAMOUNT] [--debug] [--proxy PROXY]

options:
  -h, --help            show this help message and exit
  -c COMPANY            Company to search for
  -u LINKEDIN_USERNAME  LinkedIn.com Authenticated Username
  -p LINKEDIN_PASSWORD  LinkedIn.com Authenticated Password
  -o OUTPUTFILE         Write output to file
  -pn                   Print found names to screen
  -id COMPANYID         Company ID to search for
  --sleep SLEEP         Time to sleep between requests
  --timeout TIMEOUT     HTTP Request timeout
  --logretry LOGINRETRYAMOUNT
                        Amount of times to attempt the to login to LinkedIn
  --secretry LINKEDINRETRYAMOUNT
                        Amount of times to attempt the LinkedIn Security bypass
  --debug               Turn on debug mode for error output
  --proxy PROXY         Proxy to use for requests

```
