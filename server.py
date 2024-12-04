import Pyro4
import threading
import requests
import time
import urllib.parse
from bs4 import BeautifulSoup
import csv
import os
import uuid
import re


@Pyro4.expose
class EmailScraperCoordinator:
    def __init__(self):
        self.nodes = {}
        self.lock = threading.Lock()

    def register_node(self, node_id, node_uri):
        """Register a new worker node with the central server."""
        with self.lock:
            self.nodes[node_id] = node_uri
            print(f"[+] Node {node_id} registered with URI {node_uri}")
            print(f"Current nodes: {self.nodes}")

    def distribute_work(self, urls):
        """Distribute URLs across the registered worker nodes."""
        print(self.nodes)
        node_count = len(self.nodes)
        if node_count == 0:
            raise RuntimeError("No nodes registered to perform the work.")

        workloads = {node_id: [] for node_id in self.nodes}
        for i, url in enumerate(urls):
            node_id = list(self.nodes.keys())[i % node_count]
            workloads[node_id].append(url)

        return workloads

    def email_web_scraper(self, target_url, max_time_minutes, max_nodes):
        """Main method to scrape emails using registered worker nodes."""
        print(f"[+] Starting scraping for {target_url}")
    
        # Step 1: Crawl the target URL to get the list of all URLs to scrape
        urls = self.crawl_target_url(target_url)
        if not urls:
            raise ValueError(f"No URLs found to scrape from {target_url}")

        print(f"[+] Total URLs found: {len(urls)}")
        
        if not self.nodes:
            raise ValueError("No nodes are available for scraping.")

        # Step 3: Distribute workloads (urls) across nodes
        workloads = self.distribute_work(urls)
        print(f"[+] Workload distributed to nodes: {len(workloads)} nodes.")

        # Step 4: Initialize results and stats tracking
        results = []
        stats = {"pages_scraped": 0, "emails_found": 0}
        threads = []

        def scrape_on_node(node_id, urls_to_scrape):
            try:
                uri = self.nodes[node_id]
                node_proxy = Pyro4.Proxy(uri)
                node_results = node_proxy.scrape_emails(urls_to_scrape, max_time_minutes)
                with self.lock:
                    results.extend(node_results)
                    stats["pages_scraped"] += len(urls_to_scrape)
                    stats["emails_found"] += len(node_results)
            except Exception as e:
                print(f"[!] Error in node {node_id}: {e}")
         


        for node_id, urls_to_scrape in workloads.items():
            thread = threading.Thread(target=scrape_on_node, args=(node_id, urls_to_scrape))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Save the results to CSV files
        client_id = str(uuid.uuid4()).split('-')[0]
        emails_file = f"emails_scrape_{client_id}.csv"
        stats_file = f"scraping_stats_{client_id}.csv"

        emails_file_path = os.path.abspath(emails_file)
        stats_file_path = os.path.abspath(stats_file)

        # Save Emails
        with open(emails_file, "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Email"])
            for email in results:
                writer.writerow([email])

        # Save Stats
        with open(stats_file, "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Pages Scraped", "Emails Found"])
            writer.writerow([stats["pages_scraped"], stats["emails_found"]])

        print(f"[+] Results saved to {emails_file_path} and {stats_file_path}")
        return {
            "emails_file_path": emails_file_path,
            "stats_file_path": stats_file_path,
            "emails_found": stats["emails_found"],
            "pages_scraped": stats["pages_scraped"]
        }

    def crawl_target_url(self, target_url):
        """Crawl the target URL to get all internal links."""
        urls = set()
        base_url = urllib.parse.urlsplit(target_url).scheme + '://' + urllib.parse.urlsplit(target_url).hostname
        try:
            response = requests.get(target_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            for anchor in soup.find_all("a", href=True):
                link = anchor['href']
                if link.startswith('/'):
                    link = base_url + link
                elif not link.startswith('http'):
                    link = urllib.parse.urljoin(base_url, link)
                urls.add(link)
        except requests.exceptions.RequestException as e:
            print(f"[!] Error crawling {target_url}: {e}")
        return list(urls)

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
    coordinator_instance = EmailScraperCoordinator()  
    Pyro4.Daemon.serveSimple(
        {
            coordinator_instance: "email_scraper.server"
        },
        ns=True,
        host=server_host,
        verbose=True
    )



if __name__ == "__main__":
    print("Starting Email Scraper Server...")
    start_server()
