
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
#from element_manager import *
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from io import BytesIO
from PIL import Image 
import io
import os
from google.cloud import vision
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import time
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, MoveTargetOutOfBoundsException
import pdf_reader



def read_image():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/ABHISHEK/Downloads/casemaster1-0a653bc80b08.json'

# Initialize the Vision API client
    client = vision.ImageAnnotatorClient()

# Open the image file in binary mode
    with io.open('C:/Users/ABHISHEK/Downloads/captcha/Caselocal_image.png', 'rb') as image_file:
        content = image_file.read()

# Convert the image content to a Vision API image object
    image = vision.Image(content=content)

# Perform text detection on the image
    response = client.text_detection(image=image)

# Get the text annotations from the response
    text_annotations = response.text_annotations

# Print the extracted text
    if text_annotations:
        # If there are annotations, extract alphanumeric text
        alphanumeric_text = ''.join(char for char in text_annotations[0].description if char.isalnum())
        return alphanumeric_text
    else:
        # Handle the case where there are no text annotations
        print("No text annotations found in the image.")
        return None


def initialize_driver():
    options = webdriver.ChromeOptions()
    #options.binary_location = 'C:/Program Files/Google/Chrome/Application/chrome.exe'  # Specify the path to Chrome binary if needed
    options.add_argument('executable_path=C:/Users/ABHISHEK/Downloads/chrome-win64/chromedriver/chromedriver.exe')
    driver = webdriver.Chrome(options=options)
    return driver


    
def input_data(driver):

    driver.get('https://services.ecourts.gov.in/ecourtindia_v6/')




# to click on input field
    input_field = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'cino'))
    )

# Type content in the input field
    input_field.send_keys('HRGR010094602020')



# to click on input field


    captcha_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "captcha_image"))
    )

# Capture screenshot of the entire page
    driver.save_screenshot("C:/Users/ABHISHEK/Downloads/captcha/screen_shot.png")

# Capture screenshot of the captcha element
    captcha_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "captcha_image"))
    )

# Now take screenshot 
    captcha_element.screenshot("C:/Users/ABHISHEK/Downloads/captcha/Caselocal_image.png")

    captcha =read_image()
    if captcha is not None:
        print(captcha)
    # Continue with the rest of your code
    else:
    # Handle the case where captcha extraction failed
        print("Failed to extract captcha.")
        driver.quit()
        mainfunction()
# Type content in the input field
    input_field = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'fcaptcha_code'))
    )
    input_field.send_keys(captcha)

    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'searchbtn'))
    )

# Click on the submit button
    submit_button.click()

# Get the HTML source code of the page
    time.sleep(10)
    page_source = driver.page_source
    return page_source

# Parse the HTML source code with BeautifulSoup

def mainfunction():
    driver = initialize_driver()
    page_source =input_data(driver)
    soup = BeautifulSoup(page_source, 'html.parser')
    cleaned_cnr=case_details(soup,driver)
    pdf_download(cleaned_cnr,driver)
    pdf_reader.pdf_reader(cleaned_cnr)

# Find the table containing the data





# Check if the div is found
# Find the div with id 'history_cnr'
def case_details(soup,driver):
    history_div = soup.find('div', {'id': 'history_cnr'})
    div_content = ''
# Check if the div is found
    if history_div:
    # Extract all content (including text and nested elements) within the div
        div_content = history_div.text.strip()
    
    #print(div_content)
    # Now, you have the extracted conten
    else:
        print("Div with id 'history_cnr' not found on the page.")

    case_details_string = div_content
    case_type = ''
    filing_number = ''
    filing_date = ''
    registration_number = ''
    registration_date = ''
    first_hearing_date = ''
    cnrnumber =''
    case_status = ''
    court_number_and_judge = ''
    petitioner_and_advocate = ''
    respondent_and_advocate = ''
    cleaned_cnr = ''

# Split the string into lines
    case_details_lines = case_details_string.split('\n')

# Iterate over the lines to extract information
    for i, line in enumerate(case_details_lines):
        line = line.strip()
        if line.startswith("Case Type"):
            case_type = case_details_lines[i + 1].strip()
        elif line.startswith("Filing Number"):
            filing_number = case_details_lines[i + 1].strip()
        elif line.startswith("Filing Date"):
            filing_date = case_details_lines[i + 1].strip()
        elif line.startswith("Registration Number"):
            registration_number = case_details_lines[i + 1].strip()
        elif line.startswith("First Hearing Date"):
            first_hearing_date = case_details_lines[i + 1].strip()
        elif line.startswith("CNR Number"):
            cnrnumber = case_details_lines[i + 1].strip()
            cleaned_cnr = re.sub(r'\s*\(.*\)\s*', '', cnrnumber)

# Print the extracted details
    print(f"Case Type: {case_type}")
    print(f"Filing Number: {filing_number}")
    print(f"Filing Date: {filing_date}")
    print(f"Registration Number: {registration_number}")
    print(f"First Hearing Date: {first_hearing_date}")
    print(f"CNR Number: {cleaned_cnr}")
    try:
        case_status_table = soup.find('table', {'class': 'case_status_table'})
        case_status_rows = case_status_table.find_all('tr')

    except:
        driver.quit()
        mainfunction()

    
    case_status_data = {}
    for row in case_status_rows:
        cells = row.find_all(['td', 'th'])
        if len(cells) == 2:
            label = cells[0].get_text(strip=True)
            value = cells[1].get_text(strip=True)
            case_status_data[label] = value

# Extract Petitioner and Advocate Information
    petitioner_advocate_table = soup.find('table', {'class': 'Petitioner_Advocate_table'})
    petitioner_advocate_rows = petitioner_advocate_table.find_all('tr')

    petitioner_data = {}
    for row in petitioner_advocate_rows:
        cells = row.find_all('td')
        if cells:
            petitioner_data['Petitioner'] = cells[0].get_text(strip=True)

# Extract Respondent and Advocate Information
    respondent_advocate_table = soup.find('table', {'class': 'Respondent_Advocate_table'})
    respondent_advocate_rows = respondent_advocate_table.find_all('tr')

    respondent_data = []
    for row in respondent_advocate_rows:
        cells = row.find_all('td')
        if cells:
            respondent_data.append(cells[0].get_text(strip=True))

    print("Case Status Information:")
    for label, value in case_status_data.items():
        print(f"{label}: {value}")

    print("\nPetitioner and Advocate Information:")
    print(f"Petitioner: {petitioner_data.get('Petitioner', 'N/A')}")

    print("\nRespondent and Advocate Information:")
    for idx, respondent in enumerate(respondent_data, start=1):
        print(f"{idx}) {respondent}")

    table = soup.find('table', {'id': 'act_table'})

# Extract data from the table
    if table:
        rows = table.find_all('tr')
    
    # Extract headers
        headers = [header.text.strip() for header in rows[0].find_all('th')]
    
    # Extract data from rows
        data = [row.find_all('td') for row in rows[1:]]
    
    # Display the extracted details
        for row in data:
            details = [item.text.strip() for item in row]
            result = dict(zip(headers, details))
            print("Act used in this case" ,result)
    else:
        print("Table with ID 'act_table' not found.")

    table = soup.find('table', class_='history_table')

# If the table is found, find all rows in the table body
    if table:
        rows = table.find('tbody').find_all('tr')

    # Initialize a counter for the rows with 'Business on Date'
        row_count = len(rows)

        print(f"Number of  Business on Date: {row_count}")
        if row_count > 0:
            last_row_hearing_date = rows[-1].find_all('td')[2].text.strip()
            if last_row_hearing_date:
                print(f"Next Hearing Date: {last_row_hearing_date}")
            else:
                print("Case has been disposed")
        else:
            print("No Business Date")
    else:
        print("Table with class 'history_table' not found.")



    return cleaned_cnr

# ... (previous code)
def pdf_download(cleaned_cnr,driver):
    wait = WebDriverWait(driver, 10)
    order_links = wait.until(EC.presence_of_all_elements_located((By.LINK_TEXT, 'Copy of order')))
    counter =0
# Click on each link, wait 5 minutes after each click
    for link_element in order_links:
        try:
        # Scroll the link into view if needed
        # actions = ActionChains(driver)
        # actions.move_to_element(link_element).perform()

        # Wait for the link to be clickable and then click using JavaScript
            driver.execute_script("arguments[0].click();", link_element)

        # Wait for the PDF viewer modal to appear
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'modal-content')))
            updated_page_source = driver.page_source

        # Parse the updated HTML source code with BeautifulSoup
            updated_soup = BeautifulSoup(updated_page_source, 'html.parser')

        # Find the 'object' tag within the updated page source
            object_tag = updated_soup.find('div', {'id': 'modal_order_body'}).find('object')

        # Extract the 'data' attribute from the 'object' tag
            pdf_path = object_tag['data']
            base_url = 'https://services.ecourts.gov.in/ecourtindia_v6/'
            pdf_link = urljoin(base_url, pdf_path)

        # Download PDF file
        #file_name = pdf_link.split('/')[-1]
            file_name = f'{cleaned_cnr}_document_{counter}.pdf'

        # Increment the counter for the next iteration
            counter += 1
            pdf_dir = f'C:/Users/ABHISHEK/Downloads/pdfdownload/{cleaned_cnr}'
            if not os.path.exists(pdf_dir):
                os.makedirs(pdf_dir)
            full_path = os.path.join(pdf_dir, file_name)

            response = requests.get(pdf_link, stream=True)
            with open(full_path, 'wb') as pdf_file:
                pdf_file.write(response.content)
            print(f"Downloaded {file_name}")

        except Exception as e:
            print(f"An error occurred: {e}")

    # Close the PDF viewer modal


# Assuming driver is already defined and you have navigated to the page containing the modal
        close_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='btn-close']"))).click
#close_button.click()
    driver.quit()

mainfunction()

if __name__ == "__main__":
    mainfunction()