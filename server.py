import Pyro4
from collections import deque
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import time
import threading
import csv
import os

@Pyro4.expose
class EmailScraperServer:
    def __init__(self):
        self.lock = threading.Lock() 
        self.client_counter = 0 

    def email_web_scraper(self, target_url, max_time_minutes, max_nodes):
        with self.lock:
            self.client_counter += 1  
            client_id = self.client_counter
        print(f"[+] Client {client_id} connected and started a scraping task.")

        urls = deque([target_url])
        scraped_urls = set()
        emails = {}
        stats = {"url": target_url, "pages_scraped": 0, "emails_found": 0}
        start_time = time.time()

        while urls:
            if (time.time() - start_time) / 60 > max_time_minutes:
                break

            if stats["pages_scraped"] >= max_nodes:
                break

            url = urls.popleft()
            scraped_urls.add(url)
            stats["pages_scraped"] += 1

            parts = urllib.parse.urlsplit(url)
            base_url = '{0.scheme}://{0.netloc}'.format(parts)
            path = url[:url.rfind('/') + 1] if '/' in parts.path else url

            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()  
            except requests.exceptions.MissingSchema as e:
                print(f"[!] Invalid URL schema: {url}")
                continue 
            except requests.exceptions.ConnectionError as e:
                print(f"[!] Connection error: {url}")
                continue
            except requests.exceptions.Timeout as e:
                print(f"[!] Timeout error: {url}")
                continue
            except requests.exceptions.HTTPError as e:
                print(f"[!] HTTP error: {url}")
                continue
            except requests.exceptions.RequestException as e:
                print(f"[!] Request failed: {url} - {e}")
                continue


       
            page_emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}", response.text)

            for email in page_emails:
                with self.lock:  
                    if email not in emails:
                        emails[email] = {"name": "N/A", "office": "N/A", "department": "N/A"}

            stats["emails_found"] = len(emails)

            soup = BeautifulSoup(response.text, "lxml")
            for anchor in soup.find_all("a", href=True):
                link = anchor['href']
                if link.startswith('/'):
                    link = base_url + link
                elif not link.startswith('http'):
                    link = path + link
                if link not in urls and link not in scraped_urls:
                    urls.append(link)

      
        emails_file = f"emails_scrape_{client_id}.csv"
        stats_file = f"scraping_stats_{client_id}.csv"

        emails_file_path = os.path.abspath(emails_file)
        with open(emails_file, "w", newline='', encoding='utf-8') as email_file:
            csv_writer = csv.writer(email_file)
            csv_writer.writerow(["Email", "Name", "Office", "Department"])
            for email, details in emails.items():
                csv_writer.writerow([email, details["name"], details["office"], details["department"]])

        stats_file_path = os.path.abspath(stats_file)
        with open(stats_file, "w", newline='', encoding='utf-8') as stats_file:
            csv_writer = csv.writer(stats_file)
            csv_writer.writerow(["Website URL", "Pages Scraped", "Emails Found"])
            csv_writer.writerow([stats["url"], stats["pages_scraped"], stats["emails_found"]])
        


        print(f"[+] Client {client_id}: Scraping completed. Files saved as {emails_file_path} and {stats_file_path}.")
        return {
            "emails_file_path": emails_file_path,
            "stats_file_path": stats_file_path,
            "emails_found": stats["emails_found"],
            "pages_scraped": stats["pages_scraped"]
        }

def start_server():
    
    Pyro4.Daemon.serveSimple(
        {
            EmailScraperServer: "email_scraper.server"
        },
        ns=True,  
        host="192.168.100.23", 
        verbose=True  
    )

if __name__ == "__main__":
    print("Starting Email Scraper Server...")
    start_server()
