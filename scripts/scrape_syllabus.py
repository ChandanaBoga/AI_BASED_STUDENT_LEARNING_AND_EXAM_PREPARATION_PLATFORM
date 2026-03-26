import requests
from bs4 import BeautifulSoup
import os
import time

def scrape_syllabus():
    url = "https://tkrcet.ac.in/syllabus/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Create database directory if not exists
    db_path = os.path.join("..", "database")
    if not os.path.exists(db_path):
        os.makedirs(db_path)
        
    links = soup.find_all('a', href=True)
    pdf_links = [l['href'] for l in links if l['href'].endswith('.pdf')]
    
    print(f"Found {len(pdf_links)} PDF links.")
    
    for link in pdf_links:
        file_name = link.split('/')[-1]
        file_path = os.path.join(db_path, file_name)
        
        print(f"Downloading {file_name}...")
        try:
            r = requests.get(link, stream=True)
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"Saved to {file_path}")
        except Exception as e:
            print(f"Error downloading {file_name}: {e}")
            
        time.sleep(1) # Be polite to the server

if __name__ == "__main__":
    scrape_syllabus()
