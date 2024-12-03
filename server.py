import Pyro4
import re
import requests
import time
import threading
import csv
import os
import uuid
import urllib.parse
from bs4 import BeautifulSoup  # Import BeautifulSoup

@Pyro4.expose
class EmailScraperServer:
    def __init__(self):
        self.lock = threading.Lock()
        self.client_counter = 0
        self.nodes = []  
    
    def create_nodes(self, max_nodes):
        """Automatically create and register nodes based on max_nodes."""
        with self.lock:
            self.nodes = [f"node_{i+1}" for i in range(max_nodes)]
            print(f"[+] Created and registered {max_nodes} nodes: {self.nodes}")

    def email_web_scraper(self, target_url, max_time_minutes, max_nodes):
        try:
            # Automatically create nodes based on max_nodes
            self.create_nodes(max_nodes)
            
            with self.lock:
                client_id = str(uuid.uuid4()).split('-')[0] 
            
            print(f"[+] Client {client_id} connected and started a scraping task.")

            # Step 1: Crawl the target URL and get all URLs to scrape
            urls = self.crawl_target_url(target_url)
            total_urls = len(urls)
            if total_urls == 0:
                raise ValueError(f"No URLs found to scrape from {target_url}")

            print(f"[+] Total URLs to scrape: {total_urls}")

            # Step 2: Distribute URLs across the nodes
            urls_per_node = total_urls // max_nodes
            nodes_workload = {node_id: [] for node_id in self.nodes}  # Initialize empty workloads for each node

            for i, url in enumerate(urls):
                node_id = self.nodes[i % max_nodes]  # Distribute URLs to nodes
                nodes_workload[node_id].append(url)

            # Step 3: Scrape emails on each node (simulated using threads)
            emails = {}
            stats = {"url": target_url, "pages_scraped": 0, "emails_found": 0}

            # Keep track of the start time to enforce the max time limit
            start_time = time.time()

            def scrape_emails(node_id, urls_to_scrape):
                """Function to scrape emails for a specific node."""
                nonlocal emails, stats
                print(f"[+] Node {node_id} starting email scraping...")
                node_emails = set()

                for url in urls_to_scrape:
                    # Check if we've exceeded the max time
                    elapsed_time = (time.time() - start_time) / 60  # in minutes
                    if elapsed_time > max_time_minutes:
                        print(f"[!] Max time exceeded, stopping scraping on Node {node_id}.")
                        break

                    page_emails = self.scrape_page_emails(url)
                    node_emails.update(page_emails)
                    stats["pages_scraped"] += 1

                with self.lock:
                    for email in node_emails:
                        if email not in emails:
                            emails[email] = {"name": "N/A", "office": "N/A", "department": "N/A"}

                print(f"[+] Node {node_id} finished scraping. Found {len(node_emails)} emails.")

            threads = []
            for node_id, urls_to_scrape in nodes_workload.items():
                thread = threading.Thread(target=scrape_emails, args=(node_id, urls_to_scrape))
                threads.append(thread)
                thread.start()

            # Wait for all threads (nodes) to finish
            for thread in threads:
                thread.join()

            stats["emails_found"] = len(emails)

            # Step 4: Save results to CSV
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

        except Exception as e:
            print(f"[ERROR] Exception in email_web_scraper: {e}")
            raise

    def crawl_target_url(self, target_url):
        """Crawl the target URL to get all the internal links using BeautifulSoup."""
        urls = set()
        base_url = urllib.parse.urlsplit(target_url).scheme + '://' + urllib.parse.urlsplit(target_url).hostname
        try:
            response = requests.get(target_url, timeout=10)
            response.raise_for_status()

            # Use BeautifulSoup to parse HTML and extract all URLs
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)

            for link in links:
                href = link['href']
                if href.startswith('/'):
                    href = base_url + href
                elif not href.startswith('http'):
                    href = urllib.parse.urljoin(base_url, href)
                urls.add(href)

        except requests.exceptions.RequestException as e:
            print(f"[!] Error crawling {target_url}: {e}")
        return list(urls)

    def scrape_page_emails(self, url):
        """Scrape email addresses from the page."""
        page_emails = []
        try:
            response = requests.get(url, timeout=10)
            email_regex = r'data-cfemail="([a-fA-F0-9]+)"'
            page_emails = self.decode_cfemail(response.text, email_regex)
        except requests.exceptions.RequestException as e:
            pass
        return page_emails

    def decode_cfemail(self, page_content, email_regex):
        """Decode Cloudflare's obfuscated email addresses."""
        emails = re.findall(email_regex, page_content)
        decoded_emails = []
        for email in emails:
            decoded_email = ''.join(chr(int(email[i:i+2], 16) ^ int(email[:2], 16)) for i in range(2, len(email), 2))
            decoded_emails.append(decoded_email)
        return decoded_emails

def get_server_config():
        config = {}
        with open("config.txt", "r") as f:
            for line in f:
                key, value = line.strip().split("=")
                config[key] = value
        server_ip = config["server_ip"]
        return server_ip

def start_server():
    server_host = get_server_config()
    Pyro4.Daemon.serveSimple(
        {
            EmailScraperServer: "email_scraper.server"
        },
        ns=True,
        host=server_host,
        verbose=True
    )

if __name__ == "__main__":
    print("Starting Email Scraper Server...")
    start_server()
