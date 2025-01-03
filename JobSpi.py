#!/usr/bin/python3

from __future__ import division
from argparse import RawTextHelpFormatter
from alive_progress import alive_bar
from tabulate import tabulate
import pandas as pd
import json, math, argparse, sys, os, urllib3, requests, getpass, time, logging, re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


banner = r"""
     ___.     ___.     ________     .__ 
    |   | ____\_ |__  /  _____/____ |__|
    |   |/  _ \| __ \ \____  \   _ \|  |
/\__|   (  (_) ) \_\ \/       \ |_) |  |
\_______|\____/|___  /______  /  __/|__|
   v0.5            \/       \/|_|       
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
parser.add_argument('--csv', dest='outputCSV', required=False, default='', help="Output to CSV file", action="store_true")
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
proxy = str(args.proxy) # String
outputCSV = args.outputCSV # String
retrySecCheck = 1
retryLILogin = 1
user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
linkedinEmployeeList = []

if proxy != '':
    proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}   
else:
    proxies = {"http": "", "https": ""}   

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

def jobspiGen(companyid):
    global retrySecCheck, retryLILogin
    flattened_data = []
    while retrySecCheck < linkedInRetryAmount:
        linkedinSession = requests.Session()
        linkedinSession.headers.update({'User-Agent': user_agent})
        linkedinSession.get('https://www.linkedin.com/uas/login?trk=guest_homepage-basic_nav-header-signin', verify=False, proxies=proxies, allow_redirects=True)

        for cookie in linkedinSession.cookies:
            if cookie.name == "bcookie":
                csrfCookie = str(cookie.value.split('&')[1][:-1])
                if csrfCookie is None:
                    logger.error('Failed to pull CSRF token')

        loginData = {"session_key": linkedin_username, "session_password": linkedin_password, "isJsEnabled": "false", "loginCsrfParam": csrfCookie}
        loginRequest = linkedinSession.post("https://www.linkedin.com/checkpoint/lg/login-submit", data=loginData, timeout=timeout, verify=False, proxies=proxies, allow_redirects=True)

        if "<title>Security Verification | LinkedIn</title>" in loginRequest.content.decode("utf-8"):
            retrySecCheck += 1
            logger.debug(f'LinkedIn Security Check Bypass Attempt #{retrySecCheck}')
            time.sleep(sleep)
            continue
        if 'li_at' not in linkedinSession.cookies.get_dict():
            retryLILogin += 1
            if retryLILogin >= loginRetryAmount:
                logger.error(f'Login failed after {loginRetryAmount} attempts, Please use the README for more info.')
                sys.exit()
            logger.debug(f'LinkedIn Login Unsuccessful... Retrying with attempt #{retryLILogin}')
            time.sleep(sleep)
            continue
        if "li_at" in linkedinSession.cookies.get_dict():
            logger.debug('LinkedIn Login Successful')
            break
    
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
    metadata = jsonUserListObject.get("data", {}).get("data", {}).get("searchDashClustersByAll", {}).get("metadata", {})
    if not metadata:
        logger.error("Failed to pull employee count, attempting to continue anyways...")
        count = 0
    else:
        count = metadata.get("totalResultCount", 0)
        
    logger.info("Found {:d} possible employees".format(count))
    
    with alive_bar(count, title="Processing Company Employees", enrich_print=False) as bar:
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
                                logger.debug(f'Found User: {full_name} - URN: {fsdurn}')
                                linkedinEmployeeList.append(f'{full_name},{fsdurn}')
                        bar()
            except Exception as e:
                logger.error(f'Error in employee search: {e}')
                bar()
                pass
            time.sleep(sleep/2)
    print ('\n')
    
    with alive_bar(len(linkedinEmployeeList), title="Parsing Employment Details", enrich_print=False) as bar2:
        for employee in linkedinEmployeeList:
            Full_Name, fsdurn = employee.split(',')
            try:
                req = linkedinSession.get(f"https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=false&variables=(profileUrn:urn%3Ali%3Afsd_profile%3A{fsdurn},sectionType:experience,locale:en_US)&queryId=voyagerIdentityDashProfileComponents.7f5e16224b53da3d4b722ed8f8f5fbf8", verify=False, allow_redirects=True)
                data = json.loads(req.content.decode('utf=8'))

            except Exception as e:
                logger.error(f'LinkedIn Employee Info Exception for {Full_Name}: {e}')
                bar2()
                continue
            
            dataDic = {}
            employeeExperiences = get_profile_experiences(data)
            if employeeExperiences:
                logger.debug(f'Found {len(employeeExperiences)} job profiles for {Full_Name}')
                if Full_Name not in dataDic:
                    dataDic[Full_Name] = []
                for jobProfile in employeeExperiences:
                    dataDic[Full_Name].append({"Job_Title": jobProfile.get("title", "N/A"),"Company": jobProfile.get("companyName", "N/A") or "N/A","Duration": jobProfile.get("duration", "N/A") or "N/A"})
                    
            for employee_name, jobs in dataDic.items():
                for idx, job in enumerate(jobs):
                    flattened_data.append({"Full_Name": employee_name if idx == 0 else "","Job Title": job["Job_Title"],"Current Company": job["Company"],"Duration at Company": job["Duration"]})
            time.sleep(sleep/2)
            bar2()
    return flattened_data

def get_profile_experiences(json_data):
    def parse_item(item, is_group_item=False):
        component = item["components"]["entityComponent"]
        title = component["titleV2"]["text"]["text"]
        subtitle = component["subtitle"]
        company = subtitle["text"].split(" · ")[0] if subtitle else None
        employment_type_parts = subtitle["text"].split(" · ") if subtitle else None
        employment_type = (employment_type_parts[1] if employment_type_parts and len(employment_type_parts) > 1 else None)
        metadata = component.get("metadata", {}) or {}
        location = metadata.get("text")

        if (component is not None and "caption" in component and component["caption"] is not None and "text" in component["caption"] and component["caption"]["text"] is not None):
            duration_text = component["caption"]["text"]
        else:
            duration_text = None

        if duration_text is not None:
            duration_parts = duration_text.split(" · ")
            date_parts = duration_parts[0].split(" - ")

            duration = (duration_parts[1] if duration_parts and len(duration_parts) > 1 else None)
            start_date = date_parts[0] if date_parts else None
            end_date = date_parts[1] if date_parts and len(date_parts) > 1 else None
        else:
            duration = start_date = end_date = "N/A"

        sub_components = component["subComponents"]
        fixed_list_component = (sub_components["components"][0]["components"]["fixedListComponent"] if sub_components else None)
        fixed_list_text_component = (fixed_list_component["components"][0]["components"]["textComponent"] if fixed_list_component else None)
        description = (fixed_list_text_component["text"]["text"] if fixed_list_text_component else None)

        parsed_data = {
            "title": title,
            "companyName": company if not is_group_item else None,
            "employmentType": company if is_group_item else employment_type,
            "locationName": location,
            "duration": duration,
            "startDate": start_date,
            "endDate": end_date,
            "description": description,
        }
        
        return parsed_data

    def get_grouped_item_id(item):
        sub_components = item["components"]["entityComponent"]["subComponents"]
        sub_components_components = (sub_components["components"][0]["components"] if sub_components else None)
        paged_list_component_id = (sub_components_components.get("*pagedListComponent", "") if sub_components_components else None)
        if (paged_list_component_id and "fsd_profilePositionGroup" in paged_list_component_id):
            pattern = r"urn:li:fsd_profilePositionGroup:\([A-z0-9]+,[A-z0-9]+\)"
            match = re.search(pattern, paged_list_component_id)
            return match.group(0) if match else None

    data2 = json_data
    items = []
    try:
        for item in data2["included"][0]["components"]["elements"]:
            grouped_item_id = get_grouped_item_id(item)
            if grouped_item_id:
                component = item["components"]["entityComponent"]
                company = component["titleV2"]["text"]["text"]

                location = (component["caption"]["text"] if component["caption"] else None)

                group = [i for i in data2["included"] if grouped_item_id in i.get("entityUrn", "")]
                if not group:
                    continue
                for group_item in group[0]["components"]["elements"]:
                    parsed_data = parse_item(group_item, is_group_item=True)
                    parsed_data["companyName"] = company
                    parsed_data["locationName"] = location
                    if parsed_data["endDate"] == "Present":
                        items.append(parsed_data)
                continue

            parsed_data = parse_item(item)
            if parsed_data["endDate"] == "Present":
                items.append(parsed_data)
    except Exception as e:
        logger.error(f'Error in parsing experiences: {e}')
        pass

    return items
                
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
        
    all_employee_data = jobspiGen(companyid)
    if not all_employee_data:
        logger.error("No employee data found, exiting...")
        sys.exit()
    
    df = pd.DataFrame(all_employee_data)

    if outputfile != '':
        with open(outputfile, mode='wt', encoding='utf-8') as writeOutFile:
            writeOutFile.write(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
            logger.info(f'Output written to {outputfile}')
        if outputCSV:
            csvFileName = outputfile + '.csv'
            df.to_csv(csvFileName, index=False)
            logger.info(f'Output CSV written to {csvFileName}')

    if printnames:
        print('\n')
        logger.info("\n" + tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
        print('\n')

if __name__ == "__main__":
    main_generator()
