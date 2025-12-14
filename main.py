import socket
import threading
import queue
import argparse

def scan_port(ip, port, results):
    try:
        # Use 'with' context manager to ensure socket always closes
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5) # Reduced timeout for speed (adjust based on network)
            result = sock.connect_ex((ip, port))
            if result == 0:
                results.append(port)
    except Exception:
        pass

def worker(ip, port_queue, results):
    while True:
        try:
            # Try to get a port from the queue without blocking forever
            # 'block=False' raises the Empty exception immediately if queue is empty
            port = port_queue.get(block=False)
            scan_port(ip, port, results)
            port_queue.task_done()
        except queue.Empty:
            # If the queue is empty, this thread is done. Break the loop.
            break

def main():
    parser = argparse.ArgumentParser(description="Multi-threaded Port Scanner")
    parser.add_argument("ip", help="Target IP address to scan")
    parser.add_argument("--start-port", type=int, default=1, help="Starting port (default: 1)")
    parser.add_argument("--end-port", type=int, default=1024, help="Ending port (default: 1024)")
    parser.add_argument("--threads", type=int, default=10, help="Thread count (default: 10)")
    args = parser.parse_args()

    port_queue = queue.Queue()
    results = []

    # Fill the queue
    print(f"[*] Scanning {args.ip} from port {args.start_port} to {args.end_port}...")
    for port in range(args.start_port, args.end_port + 1):
        port_queue.put(port)

    # Start threads
    threads = []
    for _ in range(args.threads):
        thread = threading.Thread(target=worker, args=(args.ip, port_queue, results))
        thread.start()
        threads.append(thread)

    # Wait for threads to finish
    for thread in threads:
        thread.join()

    # Sort results for cleaner output
    results.sort()
    
    if results:
        print(f"\n[+] Open ports on {args.ip}: {results}")
    else:
        print(f"\n[-] No open ports found on {args.ip}.")

if __name__ == "__main__":
    main()