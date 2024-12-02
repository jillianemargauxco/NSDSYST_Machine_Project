import Pyro4


def connect_to_server():
  
    server = Pyro4.Proxy("PYRONAME:email_scraper.server@192.168.100.23")
    return server

def main():
 
    server = connect_to_server()

    target_url = input("Enter Target URL to Scan: ").strip()
    max_time_minutes = int(input("Enter Scraping Time (in minutes): "))
    max_nodes = int(input("Enter Number of Nodes (pages) to Scrape: "))


    result = server.email_web_scraper(target_url, max_time_minutes, max_nodes)

    
    print(f"Scraping completed. Results saved in {result['emails_file_path']} and {result['stats_file_path']}.")
    print(f"Emails found: {result['emails_found']}, Pages scraped: {result['pages_scraped']}")

if __name__ == "__main__":
    main()
