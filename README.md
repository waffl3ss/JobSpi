# JobSpi v0.5

- The v0.5 update has increased accuracy, parsing better and getting more results. I dont have exact numbers but im seeing over 60 extra returns compared to the .3 version. Any company an employee is currently working for (i.e. end date is "Present") will be listed. Ive also included a CSV output option, and a clean/pretty table output (this prints the pretty table in the output (-o) and terminal (-pn))  

- The script will ask for required options when you dont supply any. This includes that password field, which wont show when typing, and thus is better for screenshots and evidence gathering.

- Please mark any issues in the proper github way and ill attempt to address them. Im working on streamlining things with a linkedin API, but linkedin JSON is horrible and even the API's are having trouble handeling it.

- The system you are running this script from needs to have successfully logged into LinkedIn via web browser with the account you are using. 

- LinkedIn does throttle the amount of login attempts (generally 10-15), so running this multiple times may get you throtteled and unable to execute for 24 hours.

------------------------------------------------------------------------------------

# Usage

```
$ python3 JobSpi.py -h

     ___.     ___.     ________     .__
    |   | ____\_ |__  /  _____/____ |__|
    |   |/  _ \| __ \ \____  \   _ \|  |
/\__|   (  (_) ) \_\ \/       \ |_) |  |
\_______|\____/|___  /______  /  __/|__|
   v0.5            \/       \/|_|
        Author: #Waffl3ss

usage: JobSpi copy.py [-h] [-c COMPANY] [-u LINKEDIN_USERNAME] [-p LINKEDIN_PASSWORD] [-o OUTPUTFILE] [-pn] [-id COMPANYID] [--sleep SLEEP] [--timeout TIMEOUT] [--logretry LOGINRETRYAMOUNT] [--secretry LINKEDINRETRYAMOUNT] [--debug] [--proxy PROXY] [--csv]

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
  --csv                 Output to CSV file

```
