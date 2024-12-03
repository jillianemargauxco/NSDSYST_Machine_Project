import Pyro4

def get_server_config():
    config = {}
    with open("config.txt", "r") as f:
        for line in f:
            key, value = line.strip().split("=")
            config[key] = value
    server_ip = config["server_ip"]
    return server_ip

def connect_to_server():
    server_ip = get_server_config()
    server = Pyro4.Proxy("PYRONAME:email_scraper.server@" + server_ip)
    return server

def main():
    server = connect_to_server()

    target_url = "https://www.dlsu.edu.ph"
    max_time_minutes = int(input("Enter Scraping Time (in minutes): "))
    max_nodes = int(input("Enter Number of Nodes: "))


    result = server.email_web_scraper(target_url, max_time_minutes, max_nodes)

    
    print(f"Scraping completed. Results saved in {result['emails_file_path']} and {result['stats_file_path']}.")
    print(f"Emails found: {result['emails_found']}, Pages scraped: {result['pages_scraped']}")

if __name__ == "__main__":
    main()
