# Distributed Programming Project – Email Address Web Scraper

## Overview

The **Email Address Web Scraper** is a distributed system designed to extract email addresses from web pages. It uses **Pyro4** for remote method invocation, allowing clients to request web scraping tasks and retrieve the results efficiently. The system filters email addresses to include only those ending with `@gmail.com`, `@dlsu.edu`, and `@dlsu.edu.ph`.

The project demonstrates the principles of **message passing** and **coordination** in distributed systems to achieve seamless communication and task execution between clients and the server.

---

## Team Members

Aperin, Johanna
Elloso, Jilliane
Pecson, Richard
Ypaguirre, Gebromel

---

## Features

1. **Email Filtering**: Captures email addresses ending with specific domains.
2. **Time and Node Limits**: Users can specify the maximum time for scraping and the maximum number of pages to scrape.
3. **Thread-Safe Operations**: Ensures safe multi-client handling using Python's threading and locking mechanisms.
4. **File Generation**:
   - CSV file containing extracted emails.
   - Statistics file summarizing the scraping session.
5. **Distributed Processing**: Uses Pyro4 for efficient task distribution.

---

## Distributed System Techniques Used

### **1. Message Passing**
The system employs **message passing** to facilitate communication between clients and the server:
- **Client-Server Communication**: Clients invoke methods on the server using Pyro4's Remote Procedure Call (RPC) mechanism. 
- **Serialization and Deserialization**: Pyro4 serializes data (e.g., file paths, results) to send between the server and clients.

### **2. Coordination**
The server uses **coordination techniques** to manage concurrent requests from multiple clients:
- **Thread Safety**: A threading lock ensures that shared resources (e.g., the client counter) are not accessed simultaneously, avoiding race conditions.
- **Task Queuing**: URLs to scrape are maintained in a thread-safe queue (`collections.deque`) to ensure orderly processing.

---

## System Requirements

- **Python**: Version 3.7 or higher
- **Libraries**:
  - `Pyro4`
  - `requests`
  - `BeautifulSoup4`
  - `csv`
- **Network**: Ensure the server and clients can communicate over a shared network.

---

## Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd email_scraper_server
   ```

2. Install required libraries:
   ```bash
   pip install Pyro4 requests beautifulsoup4
   ```

3. Start the Pyro4 nameserver:
   ```bash
  python -m Pyro4.naming -n <SERVER_IP>
   ```

4. Start the server:
   ```bash
   python server.py
   ```

5. Use the client to connect to the server:
   ```bash
   python client.py
   ```

---

## Usage

1. **Server Configuration**:
   - The server listens for client requests and processes scraping tasks.
   - The host IP is configured in the `server.py` file:
     ```python
     host="192.168.x.x"  # Replace with your server's IP address
     ```

2. **Client Configuration**:
   - Provide the target URL, maximum scraping time, and the maximum number of nodes to scrape.
   - Example:
     ```python
     target_url = "http://example.com"
     max_time_minutes = 5
     max_nodes = 50
     result = server.email_web_scraper(target_url, max_time_minutes, max_nodes)
     ```

3. **Output Files**:
   - **Emails File**: A CSV file containing extracted emails with placeholders for additional metadata.
   - **Statistics File**: A text file summarizing the scraping session.

---

## Project Structure

```
email_scraper_server/
├── server.py          # Pyro4 server handling scraping requests
├── client.py          # Example client implementation
├── README.md          # Project documentation
```


