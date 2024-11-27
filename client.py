import Pyro4

def main():
    email_scraper = Pyro4.Proxy("PYRONAME:email_scraper.server")

    target_url = input("[+] Enter Target URL to Scan: ").strip()
    max_time_minutes = int(input("[+] Enter Scraping Time (in minutes): "))
    max_nodes = int(input("[+] Enter Number of Nodes (pages) to Scrape: "))

    print("[+] Starting scraping task...")
    result = email_scraper.email_web_scraper(target_url, max_time_minutes, max_nodes)

    # Print or save results
    print("\n[+] Scraping Statistics:")
    print(f"URL: {result['stats']['url']}")
    print(f"Pages Scraped: {result['stats']['pages_scraped']}")
    print(f"Emails Found: {result['stats']['emails_found']}")

    print("\n[+] Emails:")
    for email, details in result["emails"].items():
        print(f"{email}: {details}")

if __name__ == "__main__":
    main()
