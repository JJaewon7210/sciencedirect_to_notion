from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import elsapy.elsclient
import elsapy.elssearch
import json
import shutil
import yaml
import re
import os
from bs4 import BeautifulSoup
import time  # Import the time module
import random  # Import the random module

YONSEI_URL = "https://access.yonsei.ac.kr/link.n2s?url="

# Function to clean the extracted text
def clean_text(text):
    text = re.sub(r'\[\d+(?:,\d+)*\]', '', text)
    text = re.sub(r'\[\s*(?:,\s*)*\s*\]', '', text)
    text = re.sub(r'\[\]', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([.,;!?])', r'\1', text)
    text = text.strip()
    return text

# Function to load configuration from a YAML file
def load_config(file_path):
     # Open your YAML file
    with open(file_path, "r", encoding="utf-8") as yaml_file:
        # Use safe_load to parse the YAML content
        data_dict = yaml.safe_load(yaml_file)
    return data_dict

# Function to perform the search and extract PII and title lists
def perform_search(elsevier_apikey, elsevier_query):
    client = elsapy.elsclient.ElsClient(elsevier_apikey)

    doc_srch = elsapy.elssearch.ElsSearch(elsevier_query, 'scopus')
    doc_srch.execute(client, get_all=True)
    return doc_srch.results

# Function to log in to Yonsei University Library
def login_to_library(driver, wait, yonsei_username, yonsei_password):
    driver.get("https://library.yonsei.ac.kr/login")
    username_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="id"]')))
    password_input = driver.find_element(By.XPATH, '//*[@id="password"]')
    login_button = driver.find_element(By.XPATH, '//*[@id="login"]/fieldset/div[2]/p/input')
    username_input.send_keys(yonsei_username)
    password_input.send_keys(yonsei_password)
    login_button.click()
    wait.until(EC.url_contains("https://library.yonsei.ac.kr/"))
    print("Login successful.")

# Function to scrape and extract text from articles
def scrape_articles(driver, wait, search_results, output_folder="data/scrap/exp", save_html=False):
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for i, search_result in enumerate(search_results):
        
        pii = search_result['pii']
        title = search_result['dc:title']
        journal = search_result['prism:publicationName']
        coverDate = search_result['prism:coverDate']
        first_author = search_result['dc:creator']
        doi = search_result['prism:doi'] # "prism:doi": "10.1016/j.autcon.2025.105972",
        doi_suffix = doi.split('/')[-1]  # Gets 'j.autcon.2025.105972'
        file_name = f"{output_folder}/{doi_suffix}.html"
        
        # Check if a file with the same name exists in the search_folder and its subfolders
        file_exists = False
        search_folder = os.path.join(output_folder, "..")
        for root, dirs, files in os.walk(search_folder):
            if f"{doi_suffix}.txt" in files:
                existing_file_path_txt = os.path.join(root, f"{doi_suffix}.txt")
                shutil.copy(existing_file_path_txt, file_name.replace(".html",".txt"))
                file_exists = True
                break
        
        if file_exists:
            continue  # Skip scraping if the file already exists
        
        article_url = f"{YONSEI_URL}https://www.sciencedirect.com/science/article/pii/{pii}"
        article_url_02 = f"https://www.sciencedirect.com/science/article/pii/{pii}"
        driver.get(article_url)
        
        # Add a random break
        time.sleep(6.5 + (8.5 - 6.5)*random.betavariate(2, 5))
        
        content_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#body > div")))
        
        content_html = content_element.get_attribute('innerHTML')
        
        # Save files in the output_folder
        if save_html:
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(content_html)
        
        soup = BeautifulSoup(content_html, 'html.parser')
        sections = soup.find_all('section', id=lambda x: x and re.match(r'^s\d{4}$', x))
        
        extracted_text = []
        extracted_text.append(f"Title: {title}")
        extracted_text.append(f"Journal: {journal}")
        extracted_text.append(f"Cover Date: {coverDate}")
        extracted_text.append(f"URL: {article_url_02}")
        extracted_text.append(f"First Author: {first_author}")

        for section in sections:
            for ref in section.find_all('a', class_='anchor anchor-primary'):
                ref.decompose()
            for figure in section.find_all('figure'):
                figure.decompose()
            text = section.get_text(separator='\n', strip=True)
            extracted_text.append(clean_text(text))
        full_text = '\n\n'.join(extracted_text)
        with open(file_name.replace(".html",".txt"), 'a', encoding='utf-8') as file:
            file.write(full_text + '\n\n')
        print(f"Text extracted and saved for article {i+1}")

def main():
    config = load_config("config.yaml")
    
    search_results = perform_search(config['elsevier_apikey'], config['elsevier_query'])
    if search_results[0].get('error') is not None:
        print('No search results found. Exiting program.')
        exit()
    else:
        print(f"Found {len(search_results)} search results.")
    
    chrome_options = Options()
    chrome_options.add_argument('headless')  # Uncomment if headless mode is needed
    chrome_options.add_argument('window-size=1920x1080')
    chrome_options.add_argument("disable-gpu")
    chrome_options.add_argument("user-agent={}".format(config["chrome_user_agent"]))
    chrome_options.add_argument("lang=ko_KR")
    chrome_options.add_experimental_option("detach", True)
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)
    try:
        login_to_library(driver, wait, config["yonsei_username"], config["yonsei_password"])
        scrape_articles(driver, wait, search_results, output_folder=config["scrap_output_folder"])
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
        print("Scraping completed and browser closed.")
    
if __name__ == "__main__":
    main()