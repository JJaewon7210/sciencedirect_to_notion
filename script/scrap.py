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
import time
import random

YONSEI_URL = "https://access.yonsei.ac.kr/link.n2s?url="

def clean_text(text):
    text = re.sub(r'\[\d+(?:,\d+)*\]', '', text)
    text = re.sub(r'\[\s*(?:,\s*)*\s*\]', '', text)
    text = re.sub(r'\[\]', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([.,;!?])', r'\1', text)
    text = text.strip()
    return text

def load_config(file_path):
    with open(file_path, "r", encoding="utf-8") as yaml_file:
        data_dict = yaml.safe_load(yaml_file)
    return data_dict

def perform_search(elsevier_apikey, elsevier_query):
    client = elsapy.elsclient.ElsClient(elsevier_apikey)
    doc_srch = elsapy.elssearch.ElsSearch(elsevier_query, 'scopus')
    doc_srch.execute(client, get_all=True)
    filtered_results = [result for result in doc_srch.results if 'pii' in result]
    return filtered_results

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

def start_chrome_driver(chrome_user_agent, headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('headless')
    chrome_options.add_argument('window-size=1920x1080')
    chrome_options.add_argument("disable-gpu")
    chrome_options.add_argument(f"user-agent={chrome_user_agent}")
    chrome_options.add_argument("lang=ko_KR")
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def scrap_articles(yonsei_username, yonsei_password, chrome_user_agent, search_results, output_folder="data/scrap/exp"):

    driver = start_chrome_driver(chrome_user_agent)
    wait = WebDriverWait(driver, 10)
    login_to_library(driver, wait, yonsei_username, yonsei_password)
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for i, search_result in enumerate(search_results):
        max_retries = 3
        retries = 0
        success = False
        while retries < max_retries and not success:
            try:
                pii = search_result['pii']
                title = search_result['dc:title']
                journal = search_result['prism:publicationName']
                coverDate = search_result['prism:coverDate']
                first_author = search_result['dc:creator']
                doi = search_result['prism:doi']
                doi_suffix = doi.split('/')[-1]
                file_name = os.path.join(output_folder, f"{doi_suffix}.txt")
                
                article_url = f"{YONSEI_URL}https://www.sciencedirect.com/science/article/pii/{pii}"
                article_url_02 = f"https://www.sciencedirect.com/science/article/pii/{pii}"
                
                driver.get(article_url)
                time.sleep(2 + (5 - 2) * random.betavariate(2, 5))
                
                content_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#body > div")))
                content_html = content_element.get_attribute('innerHTML')
                
                soup = BeautifulSoup(content_html, 'html.parser')
                sections = soup.find_all('section')
                
                extracted_text = [
                    f"Title: {title}",
                    f"Journal: {journal}",
                    f"Cover Date: {coverDate}",
                    f"URL: {article_url_02}",
                    f"First Author: {first_author}"
                ]
                
                for section in sections:
                    for ref in section.find_all('a', class_='anchor anchor-primary'):
                        ref.decompose()
                    for figure in section.find_all('figure'):
                        figure.decompose()
                    text = section.get_text(separator='\n', strip=True)
                    cleaned_text = clean_text(text)
                    extracted_text.append(cleaned_text)
                
                full_text = '\n\n'.join(extracted_text)
                with open(file_name, 'w', encoding='utf-8') as file:
                    file.write(full_text)
                
                # New file size validation
                file_size = os.path.getsize(file_name)
                if file_size < 1024*4:  # 4KB threshold
                    os.remove(file_name)  # Delete undersized file
                    raise ValueError(
                        f"Generated file size {file_size} bytes < 4KB. "
                        "Possible incomplete content."
                    )
                
                print(f"Text extracted and saved for article {i+1}")
                success = True
                
            except Exception as e:
                print(f"Error processing article {i+1}: {e}")
                if driver:
                    driver.quit()
                # Reinitialize driver and login
                driver = start_chrome_driver(chrome_user_agent)
                wait = WebDriverWait(driver, 10)
                login_to_library(driver, wait, yonsei_username, yonsei_password)
                retries += 1
                if retries >= max_retries:
                    print(f"Max retries reached for article {i+1}. Skipping.")
        if not success:
            print(f"Skipping article {i+1} after {retries} retries.")
    
    driver.quit()
    print("Scraping completed.")

def main():
    config = load_config("config.yaml")
    
    search_results = perform_search(config['elsevier_apikey'], config['elsevier_query'])
    if not search_results or 'error' in search_results[0]:
        print('No search results found. Exiting program.')
        exit()
    else:
        print(f"Found {len(search_results)} search results.")
    
    try:
        scrap_articles(config["yonsei_username"], config["yonsei_password"], config["chrome_user_agent"], search_results, output_folder=config["scrap_output_folder"])
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
    finally:
        print("Scraping process completed.")

if __name__ == "__main__":
    main()
