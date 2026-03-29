"""
Author: Caio dos Santos Cotts Quintão
Assignment: #2
Description: Port Scanner — A tool that scans a target machine for open network ports
"""
import datetime
# TODO: Import the required modules (Step ii)
# socket, threading, sqlite3, os, platform, datetime
import socket
import threading
import sqlite3
import os  # not used but imported as per instructions
import platform

# TODO: Print Python version and OS name (Step iii)
print(f"Python Version: {platform.python_version()}")
print(f"Operating System: {platform.system()}")

# TODO: Create the common_ports dictionary (Step iv)
# Add a 1-line comment above it explaining what it stores

# Common ports and what services they usually expose
common_ports = {
    21: 'FTP',
    22: 'SSH',
    23: 'Telnet',
    25: 'SMTP',
    53: 'DNS',
    80: 'HTTP',
    110: 'POP3',
    143: 'IMAP',
    443: 'HTTPS',
    3306: 'MySQL',
    3389: 'RDP',
    8080: 'HTTP-Alt'
}


# TODO: Create the NetworkTool parent class (Step v)
# - Constructor: takes target, stores as private self.__target
# - @property getter for target
# - @target.setter with empty string validation
# - Destructor: prints "NetworkTool instance destroyed"

class NetworkTool:
    def __init__(self, target: str):
        self.__target = target

    # Q3: What is the benefit of using @property and @target.setter?
    # TODO: Your 2-4 sentence answer here... (Part 2, Q3)
    # Using @property and @target.setter allows us to control access to the target attribute.
    # This encapsulation helps maintain data integrity and prevents invalid states in our objects.
    @property
    def target(self) -> str:
        return self.__target

    @target.setter
    def target(self, target: str):
        if target == '':
            print('Error: Target cannot be empty')
            return
        self.__target = target

    def __del__(self):
        print('NetworkTool instance destroyed')



# TODO: Create the PortScanner child class that inherits from NetworkTool (Step vi)
# - Constructor: call super().__init__(target), initialize self.scan_results = [], self.lock = threading.Lock()
# - Destructor: print "PortScanner instance destroyed", call super().__del__()

# Q1: How does PortScanner reuse code from NetworkTool?
# TODO: Your 2-4 sentence answer here... (Part 2, Q1)
# PortScanner inherits from NetworkTool, which means it can use the target attribute and its methods, getters, and setters without having to redefine them.
# This can be accomplished by using the "class childClass(superClass)" syntax
class PortScanner(NetworkTool):
    def __init__(self, target: str):
        super().__init__(target)
        self.scan_results = []
        self.lock = threading.Lock()

    def __del__(self):
        print('PortScanner instance destroyed')
        super().__del__()

    def scan_port(self, port: int):
        sock = None
        # Q4: What would happen without try-except here?
        # TODO: Your 2-4 sentence answer here... (Part 2, Q4)
        # Without try-except, if an error occurs while scanning a port (e.g., network error, permission error), the entire scanning process would crash and stop.
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.target, port))
            service_name = common_ports[port] if port in common_ports else 'Unknown'
            status = "Open" if result == 0 else "Closed"
            self.lock.acquire()
            self.scan_results.append((port, status, service_name))
            self.lock.release()

        except socket.error as e:
            print(f'Error scanning port {port}: {e.message}')
        finally:
            if sock: sock.close()

    def get_open_ports(self) -> list[tuple]:
        return [port_info for port_info in self.scan_results if port_info[1] == 'Open']

    # Q2: Why do we use threading instead of scanning one port at a time?
    # TODO: Your 2-4 sentence answer here... (Part 2, Q2)
    # Using threading allows us to scan multiple ports simultaneously, which could reduce time spent scanning large ranges of ports
    # This is not really that significant or noticeable in this case as scanning ports is a relatively fast operation.
    # But if scanning a port was more time-consuming, then scanning ports sequentially could take a long time, this is where concurrency would be more beneficial.
    def scan_range(self, start_port, end_port):
        threads = []
        for port in range(start_port, end_port + 1):
            t = threading.Thread(target=self.scan_port, args=(port,))
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()


# TODO: Create save_results(target, results) function (Step vii)
# - Connect to scan_history.db
# - CREATE TABLE IF NOT EXISTS scans (id, target, port, status, service, scan_date)
# - INSERT each result with datetime.datetime.now()
# - Commit, close
# - Wrap in try-except for sqlite3.Error

def save_results(target: str, results: list[tuple]):
    conn = None
    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()
        cursor.execute("""
                       create table if not exists scans
                       (
                           id
                               integer
                               primary
                                   key
                               autoincrement,
                           target
                               text,
                           port
                               integer,
                           status
                               text,
                           service
                               text,
                           scan_date
                               text
                       );
                       """)
        for (port, status, service_name) in results:
            cursor.execute("insert into scans (target, port, status, service, scan_date) values (?, ?, ?, ?, ?)",
                           (target, port, status, service_name, str(datetime.datetime.now())))
    except sqlite3.Error as e:
        print(f'Error: Unable to save scan results to database: {e}')
    finally:
        conn.commit()
        conn.close()


# TODO: Create load_past_scans() function (Step viii)
# - Connect to scan_history.db
# - SELECT all from scans
# - Print each row in readable format
# - Handle missing table/db: print "No past scans found."
# - Close connection
def load_past_scans():
    conn = None
    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()
        cursor.execute("select * from scans")
        rows = cursor.fetchall()
        for row in rows:
            _, target, port, status, service, scan_date = row
            scan_date = datetime.datetime.strptime(scan_date, "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{scan_date}] {target} : Port {port} ({service}) - {status}")
    except sqlite3.Error:
        print('No past scans found.')
    finally:
        conn.close()


# ============================================================
# MAIN PROGRAM
# ============================================================
if __name__ == "__main__":
    # TODO: Get user input with try-except (Step ix)
    # - Target IP (default "127.0.0.1" if empty)
    # - Start port (1-1024)
    # - End port (1-1024, >= start port)
    # - Catch ValueError: "Invalid input. Please enter a valid integer."
    # - Range check: "Port must be between 1 and 1024."

    target_ip = input('Enter an IP address to target: ')
    if target_ip == '':
        target_ip = '127.0.0.1'

    start_port = 0
    end_port = 0

    while True:
        try:
            start_port = int(input('Enter a stating port for the port range: '))
            if start_port < 1 or start_port > 1024:
                print('Port must be between 1 and 1024.')
                continue
            end_port = int(input('Enter an ending port for the port range: '))
            if end_port < 1 or end_port > 1024:
                print('Port must be between 1 and 1024.')
                continue
            if end_port < start_port:
                print('Starting port must be less than ending port in range')
                continue
        except ValueError:
            print('Invalid input. Please enter a valid integer.')
            continue
        break

    # TODO: After valid input (Step x)
    # - Create PortScanner object
    # - Print "Scanning {target} from port {start} to {end}..."
    # - Call scan_range()
    # - Call get_open_ports() and print results
    # - Print total open ports found
    # - Call save_results()
    # - Ask "Would you like to see past scan history? (yes/no): "
    # - If "yes", call load_past_scans()

    ps = PortScanner(target_ip)
    print(f'\n--- Scanning {target_ip} from port {start_port} to {end_port}...---')
    ps.scan_range(start_port, end_port)
    # Port 22: Open (SSH)
    print(f'--- Scan Results for {target_ip} ---')
    for (port, status, service_name) in ps.get_open_ports():
        print(f'Port {port}: {status} ({service_name})')
    print('------')
    print('Total open ports found: ', len(ps.get_open_ports()))
    save_results(ps.target, ps.scan_results)
    choice = input('Would you like to see past scan history? (yes/no): ').lower()
    if choice == 'yes':
        load_past_scans()

# Q5: New Feature Proposal
# TODO: Your 2-3 sentence description here... (Part 2, Q5)
# Diagram: See diagram_studentID.png in the repository root
# I would add a feature to allow the user to specify a custom list of ports to scan instead of a range.
# This would be useful for users who only want to scan specific ports that are relevant to their needs.
# The implementation could use a list comprehension to filter the scan results based on the user-specified ports, allowing for efficient retrieval of the relevant scan information.
