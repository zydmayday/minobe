# coding: utf-8
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import re

def sanitize_filename(name):
    """Remove invalid characters and patterns from a string to make it a valid filename."""
    # Remove file size in parentheses, e.g., (1.23MB)
    name = re.sub(r'\s*\(.*\)', '', name)
    # Replace newline characters with a space
    name = name.replace('\n', ' ').replace('\r', ' ')
    # Remove characters that are invalid in Windows filenames
    name = re.sub(r'[:\\/*?"<>|]', "", name)
    # Strip leading/trailing whitespace and periods
    name = name.strip().rstrip('.')
    return name

def login_and_scrape():
    # URL and credentials
    base_url = 'http://buscatch.net'
    login_url = 'http://buscatch.net/mobile/minobe0046/?u=20d8e091a0a309ed1562443&s=977411'
    password = 'vyvput-ciQcaf-rigwy8'

    # Create a session object to persist login
    session = requests.Session()

    # First, get the login page to find the necessary form data
    try:
        response = session.get(login_url)
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching login page: {e}")
        return

    # Parse the login page to find the correct form fields
    soup = BeautifulSoup(response.content, 'lxml')
    
    # Find the form and its input fields
    form = soup.find('form')
    if not form:
        print("Could not find the login form.")
        return

    post_url = urljoin(base_url, form.get('action'))

    inputs = form.find_all('input')
    payload = {input.get('name'): input.get('value', '') for input in inputs}

    # Update the payload with the password
    password_field_name = ''
    for input_tag in inputs:
        if input_tag.get('type') == 'password':
            password_field_name = input_tag.get('name')
            break
    
    if not password_field_name:
        print("Could not find the password input field.")
        return
        
    payload[password_field_name] = password

    # Send the POST request to log in
    try:
        response = session.post(post_url, data=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error during login: {e}")
        return

    # Check if login was successful
    if "パスワードを入力してください" in response.text:
        print("Login failed. Please check your credentials.")
        return

    print("Login successful!")

    # Find the link to the news page
    soup = BeautifulSoup(response.content, 'lxml')
    news_link = soup.find('a', string="幼稚園からのお知らせ")

    if not news_link:
        print("Could not find the link to the news page.")
        return

    news_page_url = urljoin(base_url, news_link.get('href'))

    # Navigate to the news page
    try:
        response = session.get(news_page_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news page: {e}")
        return

    # Create the main notifications folder
    if not os.path.exists('notifications'):
        os.makedirs('notifications')

    # Find all the links to individual news articles
    soup = BeautifulSoup(response.content, 'lxml')
    article_links = soup.find_all('a', href=lambda href: href and "news/detail" in href)

    for link in article_links:
        article_url = urljoin(base_url, link.get('href'))
        try:
            article_response = session.get(article_url)
            article_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching article at {article_url}: {e}")
            continue

        article_soup = BeautifulSoup(article_response.content, 'lxml')

        # Get the article title and sanitize it for the folder name
        article_title = sanitize_filename(link.text)
        article_folder = os.path.join('notifications', article_title)
        
        if not os.path.exists(article_folder):
            os.makedirs(article_folder)

        # Save the article text
        article_text = article_soup.get_text(separator='\n', strip=True)
        with open(os.path.join(article_folder, 'content.txt'), 'w', encoding='utf-8') as f:
            f.write(article_text)

        # Find and download attachments
        attachment_links = article_soup.find_all('a', href=lambda href: href and "/files/get_upload_file" in href)
        for attachment_link in attachment_links:
            attachment_url = urljoin(base_url, attachment_link.get('href'))
            attachment_filename = sanitize_filename(attachment_link.text)

            if not attachment_filename:
                print(f"Skipping attachment with empty filename from URL: {attachment_url}")
                continue

            attachment_path = os.path.join(article_folder, attachment_filename)

            try:
                attachment_response = session.get(attachment_url)
                attachment_response.raise_for_status()
                with open(attachment_path, 'wb') as f:
                    f.write(attachment_response.content)
                print(f"Downloaded attachment: {attachment_filename}")
            except requests.exceptions.RequestException as e:
                print(f"Error downloading attachment {attachment_filename}: {e}")

    print("News content and attachments saved to the 'notifications' folder.")

# Call the function
login_and_scrape()
