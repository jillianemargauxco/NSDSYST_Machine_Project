import Pyro4

# Connect to the Pyro4 nameserver and get the remote object
def connect_to_server():
    # Connect to the Pyro4 Naming Server running on the server machine
    # Replace <SERVER_IP> with the actual IP address of the machine running the server
    server = Pyro4.Proxy("PYRONAME:email_scraper.server@192.168.100.23")
    return server

def main():
    # Get the server reference
    server = connect_to_server()

    # Input parameters
    target_url = input("Enter Target URL to Scan: ").strip()
    max_time_minutes = int(input("Enter Scraping Time (in minutes): "))
    max_nodes = int(input("Enter Number of Nodes (pages) to Scrape: "))

    # Call the scraping function
    result = server.email_web_scraper(target_url, max_time_minutes, max_nodes)

    # Output the results
    print(f"Scraping completed. Results saved in {result['emails_file_path']} and {result['stats_file_path']}.")
    print(f"Emails found: {result['emails_found']}, Pages scraped: {result['pages_scraped']}")

if __name__ == "__main__":
    main()
