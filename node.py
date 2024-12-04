import Pyro4
import requests
import re
import time


@Pyro4.expose
class EmailScraperNode:
    def scrape_emails(self, urls, max_time_minutes):
        """Scrape emails from the assigned URLs."""
        results = []
        start_time = time.time()

        for url in urls:
            try:
                # Stop if max time exceeded
                elapsed_time = (time.time() - start_time) / 60  # in minutes
                if elapsed_time > max_time_minutes:
                    print(f"[!] Time limit exceeded while scraping {url}")
                    break

                response = requests.get(url, timeout=10)
                email_regex = re.findall(r"[A-Za-z0-9._%+-]+@dlsu\.edu\.ph", response.text)
                emails = self.decode_cfemail(response.text, email_regex)
                results.extend(emails)

            except requests.RequestException as e:
                print(f"[!] Failed to scrape {url}: {e}")

        print(f"[+] Scraping completed. Emails found: {len(results)}")
        return results

    def decode_cfemail(self, html_content, email_regex):
        """Decode Cloudflare obfuscated emails."""
        email_regex = r'data-cfemail="([a-fA-F0-9]+)"'
        encoded_emails = re.findall(email_regex, html_content)
        decoded_emails = []

        for encoded in encoded_emails:
            r = int(encoded[:2], 16)
            decoded = ''.join(chr(int(encoded[i:i+2], 16) ^ r) for i in range(2, len(encoded), 2))
            decoded_emails.append(decoded)

        return decoded_emails


def start_worker_node(node_id, server_ip):
    """Start a worker node and connect to the server."""
    server_uri = f"PYRONAME:email_scraper.server@{server_ip}"  # Use server IP in URI
    daemon = Pyro4.Daemon(host="192.0.0.2")
    uri = daemon.register(EmailScraperNode)
    server_proxy = Pyro4.Proxy(server_uri)
    server_proxy.register_node(node_id, str(uri))
    print(f"[+] Worker Node {node_id} ready and registered with server {server_ip}.")
    daemon.requestLoop()

def get_server_config():
        config = {}
        with open("config.txt", "r") as f:
            for line in f:
                key, value = line.strip().split("=")
                config[key] = value
        server_ip = config["server_ip"]
        return server_ip

if __name__ == "__main__":
    server_ip = get_server_config().strip()
    while True:
        node_id = input("Enter Worker Node ID: ").strip()
        if node_id:
            break
        print("[!] Worker Node ID cannot be empty. Please try again.")

    # Start the worker node
    start_worker_node(node_id, server_ip)
