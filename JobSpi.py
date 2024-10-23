#!/usr/bin/python3

from __future__ import division
from argparse import RawTextHelpFormatter
import json, math, argparse, sys, os, urllib3, requests, getpass, yaspin, time, logging, re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


banner = r"""
     ___.     ___.     ________     .__ 
    |   | ____\_ |__  /  _____/____ |__|
    |   |/  _ \| __ \ \____  \   _ \|  |
/\__|   (  (_) ) \_\ \/       \ |_) |  |
\_______|\____/|___  /______  /  __/|__|
   v0.3            \/       \/|_|       
        Author: #Waffl3ss"""
print(banner + '\n')

# Parse user arguments
parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
parser.add_argument('-c', dest='company', default='', required=False, help="Company to search for")
parser.add_argument('-u', dest='linkedin_username', required=False, help="LinkedIn.com Authenticated Username")
parser.add_argument('-p', dest='linkedin_password', required=False, help="LinkedIn.com Authenticated Password")
parser.add_argument('-o', dest='outputfile', required=False, default='', help="Write output to file")
parser.add_argument('-pn', dest='printnames', required=False, default=False, help="Print found names to screen", action='store_true')
parser.add_argument('-id', dest='companyid', required=False, help="Company ID to search for")
parser.add_argument('--sleep', dest='sleep', default=5, required=False, help="Time to sleep between requests")
parser.add_argument('--timeout', dest='timeout', required=False, default=5, help="HTTP Request timeout")
parser.add_argument('--logretry', dest='loginRetryAmount', required=False, default=5, help="Amount of times to attempt the to login to LinkedIn")
parser.add_argument('--secretry', dest='linkedInRetryAmount', required=False, default=10, help="Amount of times to attempt the LinkedIn Security bypass")
parser.add_argument('--debug', dest='debugMode', required=False, default=False, help="Turn on debug mode for error output", action="store_true")
parser.add_argument('--proxy', dest='proxy', required=False, default='', help="Proxy to use for requests")
args = parser.parse_args()



# Assign user arguments to variables we can use (old habit of mine)
company = str(args.company) # String
companyid = args.companyid # Int
sleep = int(args.sleep) # Int
timeout = int(args.timeout) # Int
outputfile = str(args.outputfile) # String
printnames = args.printnames # Bool
linkedin_username = str(args.linkedin_username) # String
linkedin_password = str(args.linkedin_password) # String
debugMode = args.debugMode # Bool
linkedInRetryAmount = int(args.linkedInRetryAmount) # Int
loginRetryAmount = int(args.loginRetryAmount) # Int
retrySecCheck = 1
retryLILogin = 1
user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
linkedinEmployeeList = []
linkedinEmployeeInfo = []
linkedinEmployeeInfoUniq = []
proxy = str(args.proxy) # String

if proxy != '':
    proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    }   
else:
    proxies = {
        "http": "",
        "https": ""
    }   

logger = logging.getLogger(__name__)
logging.basicConfig(filename='jobspi.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
logger.addHandler(console_handler)

if debugMode:
	logger.setLevel(logging.DEBUG)
	console_handler.setLevel(logging.DEBUG)
	console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

if args.companyid is None and args.company == '':
    company = input(" Company Name: ")
if args.linkedin_username is None:
    linkedin_username = input(" LinkedIn Username: ")
if args.linkedin_password is None:
    linkedin_password = getpass.getpass(" LinkedIn Password: ")

if outputfile == '' and not printnames:
    logger.error("No output option select, choose an output file (-o) or print to screen (-pn) and try again...")
    sys.exit()

def parseProfileData(full_name, json_data):
    try:
        included = json_data.get('included', [])
        for item in included:
            top_components = item.get('topComponents', [])
            for idx, component in enumerate(top_components):
                components = component.get('components', {})
                header_component = components.get('headerComponent', {})
                if header_component and isinstance(header_component, dict):
                    title = header_component.get('title')
                    if title and isinstance(title, dict):
                        text_value = title.get('text')
                        if text_value and text_value.lower() == "experience":
                            if idx + 1 < len(top_components):
                                next_component = top_components[idx + 1]
                                try:
                                    dict1 = next_component['components']['fixedListComponent']['components'][0]
                                except:
                                    logger.debug(f"No employment history found for {full_name}")
                                    return 'Err', 'Err', 'Err'
                                try:
                                    jobTitle = dict1['components']['entityComponent']['subComponents']['components'][0]['components']['entityComponent']['titleV2']['text']['text']
                                except:
                                    jobTitle = 'N/A'
                                try:
                                    companyName = dict1['components']['entityComponent']['titleV2']['text']['text']
                                except:
                                    companyName = 'N/A'
                                try:
                                    companyLengthInitial = dict1['components']['entityComponent']['subtitle']['text']
                                    time_part = re.split(r'·|\u00b7', companyLengthInitial)[-1].strip()
                                    years = re.search(r'(\d+)\s*yr', time_part)
                                    months = re.search(r'(\d+)\s*mo', time_part)
                                    years = int(years.group(1)) if years else None
                                    months = int(months.group(1)) if months else None
                                    output = []
                                    if years is not None:
                                        output.append(f"{years} yr{'s' if years != 1 else ''}")
                                    if months is not None:
                                        output.append(f"{months} mo{'s' if months != 1 else ''}")
                                    companyLength = " ".join(output) if output else "Less than a month (or there was an error)"
                                    #companyLength = "N/A" #it can have an error getting the length sometimes...
                                except:
                                    companyLength = 'N/A'

                            if companyName == 'N/A' or jobTitle == 'N/A':
                                companyName, jobTitle = jobTitle, companyName # Sometimes if it cant find the company name it messes up the order
                                
                            return jobTitle, companyName, companyLength
    except:
        logger.debug(f"No experience card found for {full_name}")
        return 'Err', 'Err', 'Err' 

def jobspiGen(companyid):
    global retrySecCheck
    global retryLILogin
    if retrySecCheck >= linkedInRetryAmount:
        logger.error(f'LinkedIn Security Check Implemented, {linkedInRetryAmount} retries attemped and failed. Please use the README for more info.')
        sys.exit(0)

    if retryLILogin >= loginRetryAmount:
        logger.error(f'Attempted to login to LinkedIn {loginRetryAmount} times with no success. Please use the README for more info. ')
        sys.exit(0)

    try:
        # Create Login Session and Hold Cookies
        linkedinSession = requests.Session()
        linkedinSession.headers.update({'User-Agent': user_agent})
        linkedinSession.get('https://www.linkedin.com/uas/login?trk=guest_homepage-basic_nav-header-signin', verify=False, proxies=proxies, allow_redirects=True)

        # Get CSRF cookie
        for cookie in linkedinSession.cookies:
            if cookie.name == "bcookie":
                csrfCookie = str(cookie.value.split('&')[1][:-1])
                if csrfCookie is None:
                    logger.error('Failed to pull CSRF token')

        # Conduct Login and Store in Session
        loginData = {"session_key": linkedin_username, "session_password": linkedin_password, "isJsEnabled": "false", "loginCsrfParam": csrfCookie}
        loginRequest = linkedinSession.post("https://www.linkedin.com/checkpoint/lg/login-submit", data=loginData, timeout=timeout, verify=False, proxies=proxies, allow_redirects=True)

        if "<title>Security Verification | LinkedIn</title>" in loginRequest.content.decode("utf-8"):
            retrySecCheck += 1
            logger.debug(f'LinkedIn Security Check Bypass Attempt #{retrySecCheck}')
            time.sleep(sleep)
            jobspiGen(companyid)
        else:
            if 'li_at' in linkedinSession.cookies.get_dict():
                logger.debug('LinkedIn Login Successful')
            else:
                retryLILogin += 1
                logger.debug(f'LinkedIn Login Unsuccessful... Retrying attempt #{retryLILogin}')
                time.sleep(sleep)
                jobspiGen(companyid)
        
        specialCookieList = ''
        for cookie in linkedinSession.cookies:
            if cookie.name == "JSESSIONID":
                ajaxcookie = cookie.value[1:-1]
            specialCookieList += cookie.name + "=" + cookie.value + "; "

        linkedinSession.headers.update({
            "Host": "www.linkedin.com",
            "User-Agent": user_agent,
            "Accept": "application/vnd.linkedin.normalized+json+2.1",
            "x-restli-protocol-version": "2.0.0",
            "Cookie": specialCookieList,
            "Csrf-Token": ajaxcookie,
            })

        if (companyid == '' or companyid is None):
            logger.info("Pulling Company ID for {:s}".format(company.strip()))

            query = "includeWebMetadata=true&variables=(start:0,origin:SWITCH_SEARCH_VERTICAL,query:(keywords:" + str(company) + ",flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:resultType,value:List(COMPANIES))),includeFiltersInResponse:false))&&queryId=voyagerSearchDashClusters.8456d8ebf04d20b152309b0c7cfabee2"
            req = linkedinSession.get("https://www.linkedin.com/voyager/api/graphql?" + query, verify=False, proxies=proxies)
            jsonObject = json.loads(req.content.decode())

            for companyObject in jsonObject["included"]:
                try:
                    id = companyObject["trackingUrn"].split(":")[3]
                    companyname = companyObject["title"]["text"]
                    print("{:.<55}: {:s}".format(companyname + " ",id))
                except:
                    pass

            companyid = input("\nSelect company ID value: ")  

        employeeSearchQuery = "/voyager/api/graphql?variables=(start:0,origin:COMPANY_PAGE_CANNED_SEARCH,query:(flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:currentCompany,value:List(" + str(companyid) + ")),(key:resultType,value:List(PEOPLE))),includeFiltersInResponse:false))&&queryId=voyagerSearchDashClusters.c4f33252de52295107ac12f946d34b0d"
        employeeSearchRequest = linkedinSession.get("https://www.linkedin.com" + employeeSearchQuery, verify=False, proxies=proxies)
        jsonUserListObject = json.loads(employeeSearchRequest.content.decode())

        count = 0
        count = jsonUserListObject["data"]["data"]["searchDashClustersByAll"]["metadata"]["totalResultCount"]
        logger.info("Found {:d} possible employees".format(count))

        with yaspin.yaspin(text=" - Running LinkedIn Employee Enumeration   "):
            for countNum in range(0,int((int(math.ceil(count / 10.0)) * 10) / 10)):
                try:
                    pageQuery = "/voyager/api/graphql?variables=(start:" + str(countNum * 10) + ",origin:COMPANY_PAGE_CANNED_SEARCH,query:(flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:currentCompany,value:List(" + str(companyid) + ")),(key:resultType,value:List(PEOPLE))),includeFiltersInResponse:false))&&queryId=voyagerSearchDashClusters.c4f33252de52295107ac12f946d34b0d"
                    pageRequest = linkedinSession.get("https://www.linkedin.com" + pageQuery, verify=False, proxies=proxies)
                    jsonUserContent = json.loads(pageRequest.content.decode())
                    for person in jsonUserContent["included"]:
                        if "title" in person:
                            url = person['navigationContext']['url']
                            nameField = person['title']['text']
                            if "," in nameField:
                                cleanNameField = nameField.split(",")[0]
                                first_name = cleanNameField.split(" ")[0]
                                last_name = cleanNameField.split(" ")[-1]
                            else:
                                first_name = nameField.split(" ")[0]
                                last_name = nameField.split(" ")[-1]

                            if len(first_name) <= 1 or len(last_name) <= 1:
                                pass
                            elif "LinkedIn" in first_name:
                                pass
                            elif "." in last_name:
                                pass
                            elif "." in first_name:
                                pass
                            else:
                                full_name = (first_name.capitalize() + " " + last_name.capitalize())
                                if full_name.startswith("."):
                                    pass
                                else:
                                    fsdurn = url.split('%3A')[-1]
                                    logger.debug(f'Found User: {full_name}')
                                    linkedinEmployeeList.append(f'{full_name},{fsdurn}')

                        time.sleep(sleep/2)

                except Exception as linkedinuserexception:
                    logger.debug(f"Employee Search Module Exception for {full_name}: {linkedinuserexception}")
                    pass

        with yaspin.yaspin(text=" - Running Employee Job Enumeration   "):
            for employee in linkedinEmployeeList:
                try:
                    full_name, fsdurn = employee.split(',')
                    req = linkedinSession.get(f'https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true&variables=(profileUrn:urn%3Ali%3Afsd_profile%3A{fsdurn})&queryId=voyagerIdentityDashProfileCards.5419d81edf3eff3d1f4fb2cb5b6c8104', verify=False, proxies=proxies)
                    response_content = req.content.decode('utf=8')
                    jsonJobData = json.loads(response_content)
                    job_title, companyname, length = parseProfileData(full_name,jsonJobData)
                    logger.debug(f'{full_name} -- {job_title} at {companyname} for {length}')
                    linkedinEmployeeInfo.append(f'{full_name} -- {job_title} at {companyname} for {length}')
                    time.sleep(sleep/2)
                except json.JSONDecodeError:
                    logger.debug(f"JSON Decode Error for {full_name}")
                    pass
                except Exception as linkedinuserexception:
                    logger.debug(f"Job Search Module Exception for {full_name}: {linkedinuserexception}")
                    pass
                
    except Exception as linkedinexception:
        logger.error(f"LinkedIn module exception: {linkedinexception}")
        pass
        #sys.exit()
	
def main_generator():
    global outputfile

    if outputfile != '':
        if os.path.exists(outputfile):
            del_outfile = input("Output File exists, overwrite? [Y/n] ")
            if del_outfile == 'y' or 'Y' or '':
                os.remove(outputfile)
            elif del_outfile == 'n' or 'N':
                logger.error("Not overwriting file, exiting...")
                sys.exit()
            else:
                logger.error("Not a valid option, exiting...")
                sys.exit()
                
    jobspiGen(companyid)
    
    linkedinEmployeeInfoUniq = list(set(linkedinEmployeeInfo))
    totalUsersInList = int(len(linkedinEmployeeInfoUniq))

    if totalUsersInList == 0:
        logger.error('No names obtained, Exiting...')
        sys.exit()

    if outputfile != '':
        with open(outputfile, mode='wt', encoding='utf-8') as writeOutFile:
            writeOutFile.write('\n'.join(linkedinEmployeeInfoUniq))

    if printnames:
        print('\n')
        for i in list(linkedinEmployeeInfoUniq):
            logger.info(str(i))
        print('\n')

    logger.info(f'Found a total of {totalUsersInList} potential users')

if __name__ == "__main__":
    main_generator()
