from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import os
import pickle
# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
# for encoding/decoding messages in base64
import base64
from googleapiclient.errors import HttpError

from mimetypes import guess_type as guess_mime_type

"""What is the difference between this and just going on HandShake
    It is going to Excel can I webscrape my email to check if ive gotten any responses?
    go to applied put it in a csv file called applied create a email webscraper to check if replied"""

"""GOAL: Ask if either UCSD or Internship! Once that is done put it into csv file then EXCEL in order to see most common requirements,
average pay, when posted, whether or not applied"""
"""Issue: occuring is that once login it and click ucsd it goes back ?
SOLVED: Due to having driver.get(ucsdpposting). But now it won't instantly go to posting page :("""

"""Issue: When I want to have the UCSD SSO button instant clicked it wont allow me
SOLVED: Since it is not a button but a <a> tag and it is redirecting I think that is what it is so maybe I have to link it to redirection page instead"""

#be able to ask for ucsd jobs/ non ucsd jobs/ specific skills
#driver can be anything but most people use driver

SCOPES = ['https://mail.google.com/']
#Put the gmail here
our_email = 'EMAIL@gmail.com'

driver = webdriver.Chrome(options=Options())

#To login
def login_automatically():
    #CHANGE THESE
    #Input ur ucsd email and password
    UCSDemail = 'EMAIL@ucsd.edu'
    passwordUCSD = 'Password'
    #Create variables here in order to replace email and password

    driver.get('https://app.joinhandshake.com/login')

    # Goes to login finds the login thing
    WebDriverWait(driver, 80).until(
        EC.presence_of_element_located((By.NAME, 'identifier'))
    )

    # Find and fill in the login thing :o was really cool when it did it (lerned somethin new :D)
    email_input = driver.find_element(By.NAME, 'identifier')
    next_button = driver.find_element(By.XPATH, '//*[@id="ui-id-1"]/div[3]/form/div/button')
    #If are non UCSD student remove this or comment it out! or maybe we can put ask if UCSD student or not
    #Since I am UCSD student I will leave it for now later on for imporvements to make more inclusive
    
    #when i turn this in/ upload to github put variables loolol
    email_input.send_keys(UCSDemail)
    next_button.click()

    #for the duo/for UCSD students
    WebDriverWait(driver, 80).until(
        EC.presence_of_all_elements_located((By.NAME, 'urn:mace:ucsd.edu:sso:username'))
    )

   
    UCSDemail_input = driver.find_element(By.NAME, 'urn:mace:ucsd.edu:sso:username')
    UCSDpassword = driver.find_element(By.NAME, 'urn:mace:ucsd.edu:sso:password')
    login = driver.find_element(By.XPATH, '//*[@id="login"]/button')

    #MAKE SURE TO CHANGE THIS BEFORE UPLOADING TO GITHUBBBB!!!
    UCSDemail_input.send_keys(UCSDemail)
    UCSDpassword.send_keys(passwordUCSD)
    login.click()

    # Wait for the login to complete and redirect to the target page
    WebDriverWait(driver, 75).until(
        EC.url_changes('https://ucsd.joinhandshake.com/stu/postings')
    )

""""UCSD Jobs"""
def ucsd_jobs():
    
    #get the ucsd post link
    #Auto apply with resume get link and see what works what doesnt
    """Fetch UCSD jobs and save to CSV."""
    print("Fetching UCSD jobs...")
    driver.get('https://ucsd.joinhandshake.com/stu/postings?page=1&per_page=25&sort_direction=desc&sort_column=default&query=ucsd')
    # Wait for job cards to be present
    WebDriverWait(driver, 75).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "style__card___XOQvr"))
    )
    
    # Find job cards
    cards = driver.find_elements(By.CLASS_NAME, "style__card___XOQvr")
    ucsd_jobs = []

    for card in cards:
        try:
            # Getting the UCSD tthings 
            #When working on internship then do the if do != UCSD and do more generic
            span_element = WebDriverWait(card, 10).until(
                EC.visibility_of_element_located((By.XPATH, './div/div[3]/div[1]/div[1]/div'))
            )
            job_type = span_element.text

            if(job_type == 'UC San Diego'):
                job_description = card.find_element(By.XPATH, './/h3').text

    #Finding the location
                try:
                    location_element = card.find_element(By.XPATH, './div/div[3]/div[2]/div/span/div/span[1]/span')
                    location = location_element.text
                    #if not found then this is what it will say
                except Exception as e:
                    print(f"Error finding location: {e}")
                    location = "Not Specified"

    #finding the date posted check if recent!
                try:
                    date_posted_element = card.find_element(By.XPATH, './div/div[3]/div[2]/div/span/div/div/p')
                    date_posted = date_posted_element.text
                    #if not found then this is what it will say
                except Exception as e:
                    print(f"Error finding date posted: {e}")
                    date_posted = "No date"
                

            #Find the link and store link to be able to apply create a method probably because I want to use this for intrnship too
                try:
                    link = card.get_attribute('href')
                    
                except Exception as e:
                    print(f'Error finding link {e}')
                    link = "Not found"

            #Click on the link to be able to see requirements save them and then be able to check which 
            #Qualifications I want create a method probably and check for internship
            #Find the requirements 

            # Store the information in a dictionary
                job_info = {
                    'Job Type': job_type,
                    'Job Description': job_description,
                    'Location': location,
                    'Link':link,
                    'Date Posted': date_posted
                
                }

            # Append to the list
                ucsd_jobs.append(job_info)
        
        except Exception as e:
            print(f"Error extracting data from a card: {e}")

        # Define the CSV file path
        csv_file_path = 'handshakeData.csv'
    
    # Write the extracted data to a CSV file
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['Job Type', 'Job Description', 'Location', 'Link','Date Posted']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for job in ucsd_jobs:
                writer.writerow(job)
    
    print(f"Data has been written to {csv_file_path}")
   

"""Internship Opportunities"""
def fetch_internships():
    #wait time
    driver.get('https://ucsd.joinhandshake.com/stu/postings?page=1&per_page=25&sort_direction=desc&sort_column=default&query=cs%20internship#skip-to-content')
    #Go to internship page me thinks so do the get thing while the other one is ucsd page
    print("Fetching internships...")
    WebDriverWait(driver, 75).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "style__card___XOQvr"))
    )
    
    # Find job cards
    cards = driver.find_elements(By.CLASS_NAME, "style__card___XOQvr")
    ucsd_jobs = []

    for card in cards:
        try:
            # Getting the UCSD tthings //*[@id="posting-845427765"]/div/div[3]/div[1]/div[1]/div
            #When working on internship then do the if do != UCSD and do more generic
            span_element = WebDriverWait(card, 10).until(
                EC.visibility_of_element_located((By.XPATH, './div/div[3]/div[1]/div[1]/div'))
            )
            job_type1 = span_element.text
            if(job_type1 != "UC San Diego"):

                #Description of job
                job_description1 = card.find_element(By.XPATH, './/h3').text
                if("Intern" in job_description1 or "Internship" in job_description1):
                    
                #Find the location
                    try:
                        location_element1 = card.find_element(By.XPATH, './div/div[3]/div[2]/div/span/div/span[1]/span')
                        location1 = location_element1.text
                    except Exception as e:
                        print(f"Error Finding Location: {e}")
                        location1 = "Not Specified"

                #Date 
                    try:
                        date_element1 = card.find_element(By.XPATH, './div/div[3]/div[2]/div/span/div/div/p')
                        date_posted1 = date_element1.text
                    except Exception as e:
                        print(f"Not found date posted: {e}")
                        date_posted1 = "No Date"
                    
                    try:
                        link = card.get_attribute('href')
                    
                    except Exception as e:
                        print(f'Error finding link {e}')
                        link = "Not found"

                    job_info = {
                        'Job Type': job_type1,
                        'Job Description': job_description1,
                        'Location': location1,
                        'Link': link,
                        'Date Posted': date_posted1

                    }
                    ucsd_jobs.append(job_info)
        except Exception as e:
            print("Error")

        csv_file_path = 'internshipData.csv'
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['Job Type', 'Job Description', 'Location','Link','Date Posted']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for job in ucsd_jobs:
                writer.writerow(job)
    print("Data has been written to internshipData.csv")
            


def email_check():
    #be able to input the line of code we got from either internshipData or handshakeData
    #and make it be spliced into a dictionary in the corresponding spots:
    csv_file = 'applied.csv'
    
    # Initial job list
    ucsd_jobs = [     
    ]
    
    # Ask the user if they want to add a new job or just check the list
    questionNew = input("Do you want to add new input or just check? (type 'new' to add or 'check' to view): ")
    
    if questionNew.lower() == "new":
        # Get the input from the user
        newJob = input("Input the corresponding data in the format 'Job Type, Job Description, Location, URL, Date Posted': ")
        
        # Split the input string by commas
        details = newJob.split(',')
        
        if len(details) == 6:
            # Parse details
            job_type = details[0].strip()
            job_description = details[1].strip()
            location = details[2].strip()
            url = details[5].strip()
            date_posted = details[4].strip()
            
            # Create a dictionary for the new job
            new_job = {
                'Job Type': job_type,
                'Job Description': job_description,
                'Location': location,
                'Date Posted': date_posted,
                'URL': url
            }
            
            # Append the new job to the list
            ucsd_jobs.append(new_job)
            print("New job added successfully!")

            with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                fieldnames = ['Job Type', 'Job Description', 'Location','URL','Date Posted']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                csv_file = 'applied.csv'
                file_exists = os.path.isfile(csv_file) and os.path.getsize(csv_file) > 0
                if not file_exists:
                    writer.writeheader()
                for job in ucsd_jobs:
                    writer.writerow(job)
            print("Finished updating !")
        
        else:
            print("Input format is incorrect. Please provide exactly 5 comma-separated values.")
    
    elif questionNew.lower() == "check":
        service = get_gmail_service()
        for job in ucsd_jobs:
            job_description = job.get('Job Description')
            if job_description:
                print(f"Searching for messages related to job description: '{job_description}'")

                messages = search_messages(service, job_description)
                
                if messages:
                    print(f"Found messages for job '{job_description}':")
                    for message in messages:
                        print(f"Message ID: {message['id']}")
                        print(f"Body (first 100 characters): {message['body'][:100]}")
                        print("-" * 40)  # Separator for readability
                else:
                    print(f"No messages found for job '{job_description}'")
            else:
                print("Job description is missing in the row.")
        
    
    else:
        print("Invalid input. Please type 'new' to add a job or 'check' to view the job listings.")
    #Scrape email! both of them
    #I think manually from all the other files put info into applied
    
    #have a timer/counter check everyday if reply so once I run it it will update
    #applied file check and see if email scraped matches what is being shown

#from API
def get_gmail_service():
    """Authenticate and return the Gmail API service object."""
    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def process_jobs_and_search_messages(service, csv_file):
    """Read job entries from a CSV file, search messages for each job, and display results."""
    try:
        with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                job_description = row.get('Job Description')
                if job_description:
                    print(f"Searching for messages related to job description: '{job_description}'")
                    messages = search_messages(service, job_description)
                    
                    if messages:
                        print(f"Found messages for job '{job_description}':")
                        for message in messages:
                            print(f"Message ID: {message['id']}")
                            print(f"Body (first 100 characters): {message['body'][:100]}")
                            print("-" * 40)  # Separator for readability
                    else:
                        print(f"No messages found for job '{job_description}'")
                else:
                    print("Job description is missing in the row.")

    except FileNotFoundError:
        print(f"The file '{csv_file}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

#From the API Google
def search_messages(service, query):
    """Search for emails that match the query and fetch detailed message information."""
    try:
        # Search for messages that match the query
        result = service.users().messages().list(userId='me', q=query).execute()
        messages = []
        if 'messages' in result:
            messages.extend(result['messages'])
        while 'nextPageToken' in result:
            page_token = result['nextPageToken']
            result = service.users().messages().list(userId='me', q=query, pageToken=page_token).execute()
            if 'messages' in result:
                messages.extend(result['messages'])
        
        # Fetch detailed information for each message
        detailed_messages = []
        for msg in messages:
            msg_id = msg['id']
            msg_detail = service.users().messages().get(userId='me', id=msg_id).execute()
            
            # Extract the message body
            body_data = msg_detail.get('payload', {}).get('parts', [])
            body = ''
            for part in body_data:
                mime_type = part.get('mimeType')
                if mime_type in ['text/plain', 'text/html']:
                    body = part.get('body', {}).get('data', '')
                    body = base64.urlsafe_b64decode(body).decode('utf-8')
                    break
            
            # Append detailed message info
            detailed_messages.append({
                'id': msg_id,
                'body': body
            })
        
        return detailed_messages
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

#from the API
def gmail_authenticate():
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

# get the Gmail API service
#Idk if this is needed anymore :0
#service = gmail_authenticate()

#Main
def main():

    #We can also have the both option!
    #Give option of either a UCSD job or an Internship
    #Find how to get all info seperated
    
    print("Wait until full login")
    TypeOfWork = input("Are you looking for UCSD job, Internship, or check Email?: ").strip()
    if TypeOfWork == "UCSD":
        login_automatically()
        input("Press Enter to continue, once all logged in")
        ucsd_jobs()
    elif TypeOfWork == "Internship":
        login_automatically()
        input("Press Enter to continue, once all logged in")
        fetch_internships()
    elif TypeOfWork == "Email":
        email_check()
        service = get_gmail_service()
        csv_file = 'applied.csv'
        process_jobs_and_search_messages(service, csv_file)
    else:
        print("Exiting Script")
    
    driver.quit()
        

if __name__ == '__main__':
    main()