import Pyro4

def get_server_config():
    """Read the server's IP address from a config file."""
    config = {}
    with open("config.txt", "r") as f:
        for line in f:
            key, value = line.strip().split("=")
            config[key] = value
    return config["server_ip"]

def connect_to_server():
    """Connect to the Pyro4 server."""
    try:
        server_ip = get_server_config()
        # Connect to the server via Pyro4 Name Server
        server = Pyro4.Proxy(f"PYRONAME:email_scraper.server@{server_ip}")
        print("[+] Connected to the Email Scraper Server.")
        return server
    except Exception as e:
        print(f"[!] Could not connect to server: {e}")
        raise

def main():
    """Main client logic to interact with the server."""
    try:
        server = connect_to_server()

        # Get user inputs for the target URL, max scraping time, and nodes
        target_url = "https://www.dlsu.edu.ph".strip()
        max_time_minutes = int(input("Enter Scraping Time (in minutes): "))
        max_nodes = int(input("Enter Number of Nodes: "))

        print("[+] Sending request to the server...")
        
        # Invoke the scraping function on the server
        result = server.email_web_scraper(target_url, max_time_minutes, max_nodes)

        # Display results to the user
        print(f"\n[+] Scraping completed. Results saved to:")
        print(f"    Emails File: {result['emails_file_path']}")
        print(f"    Stats File: {result['stats_file_path']}")
        print(f"    Emails Found: {result['emails_found']}")
        print(f"    Pages Scraped: {result['pages_scraped']}")

    except Pyro4.errors.PyroError as pyro_err:
        print(f"[!] Pyro4 Error: {pyro_err}")
    except Exception as e:
        print(f"[!] Unexpected Error: {e}")

if __name__ == "__main__":
    print("Starting Email Scraper Client...")
    main()
