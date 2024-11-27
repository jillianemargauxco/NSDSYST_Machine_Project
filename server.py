import Pyro4
from collections import deque
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import time
import csv

@Pyro4.expose
class EmailScraperServer:
    def email_web_scraper(self, target_url, max_time_minutes, max_nodes):
        urls = deque([target_url])
        scraped_urls = set()
        emails = {}
        stats = {"url": target_url, "pages_scraped": 0, "emails_found": 0}
        start_time = time.time()

        try:
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
                except (requests.exceptions.MissingSchema, 
                        requests.exceptions.ConnectionError, 
                        requests.exceptions.Timeout,
                        requests.exceptions.HTTPError):
                    continue

                page_emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}", response.text)
                for email in page_emails:
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
        except KeyboardInterrupt:
            pass

        # Save results to CSV (optional: you can send results directly to the client)
        with open("emails.csv", "w", newline='', encoding='utf-8') as email_file:
            csv_writer = csv.writer(email_file)
            csv_writer.writerow(["Email", "Name", "Office", "Department"])
            for email, details in emails.items():
                csv_writer.writerow([email, details["name"], details["office"], details["department"]])

        with open("scraping_stats.csv", "w", newline='', encoding='utf-8') as stats_file:
            csv_writer = csv.writer(stats_file)
            csv_writer.writerow(["Website URL", "Pages Scraped", "Emails Found"])
            csv_writer.writerow([stats["url"], stats["pages_scraped"], stats["emails_found"]])

        return {
            "emails": emails,
            "stats": stats
        }

def start_server():
    Pyro4.Daemon.serveSimple(
        {
            EmailScraperServer: "email_scraper.server"
        },
        ns=True
    )

if __name__ == "__main__":
    print("Starting Email Scraper Server...")
    start_server()
