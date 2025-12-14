# What is happening when we run the port scanner?

## Part 1 - Network Layer

The basics of this script that it interacts with the Transport Layer of the OSI model, specifically using TCP (Transmission Control Protocol) to establish connections to specified ports on a target IP address.

### Socket Object

The line `socket.socket(socket.AF_INET, socket.SOCK_STREAM)` creates a new socket object. Here's a breakdown of the parameters:
- `socket.AF_INET`: This specifies the address family for the socket. `AF_INET` indicates that the socket will use IPv4 addresses.
- `socket.SOCK_STREAM`: This specifies the socket type. `SOCK_STREAM` indicates that the socket will use TCP, which is a connection-oriented protocol. `SOCK_DGRAM` would be used for UDP, which is connectionless.

### The Scan Logic
When `sock.connect_ex((target_ip, port))` is called, a 3-way TCP handshake is initiated:
1. **SYN (Synchronize)**: The client (our port scanner) sends a SYN packet to the server (the target IP) to initiate a connection.
2. **SYN-ACK (Synchronize-Acknowledge)**: If the target port is open, the server responds with a SYN-ACK packet, indicating that it is ready to establish a connection.
3. **ACK (Acknowledge)**: The client sends an ACK packet back to the server, completing the handshake.
If the port is closed, the server will respond with a RST (Reset) packet instead of a SYN-ACK, indicating that the connection cannot be established.
If the port is filtered (e.g., by a firewall), the client may not receive any response, leading to a timeout.

### Why Use `connect_ex`?
The `connect_ex` method is used instead of `connect` because it returns an error code instead of raising an exception if the connection fails. This allows the script to handle different outcomes (open, closed, filtered) more gracefully without crashing.

## Part 2 - Multithreading
Scanning 1000 ports sequentially is slow because of *Blocking I/O*

### Blocking I/O vs Concurrency
In a standard loop, when we send a packet to Port 80, the CPU idles doing nothing while waiting for a response. This is called Blocking.

 - *Sequential*: Send 1 packet -> Wait for response -> Send next packet -> Wait for response -> Repeat
 - *Threaded*: Send 2 packets -> Wait for responses -> Process responses as they arrive

### Producer Consumer Model
The code implements a Producer-Consumer model using a queue:
- **The Queue (The Buffer)**: Holds the ports to be scanned. This acts as a conveyor belt. It is thread safe, meaning it has internal locks. If Threads A and B try to access an item at the exact nanosecond, the Queue forces one to wait.
- **Producer**: The main thread that populates the queue with port numbers to be scanned.
- **Consumers**: The worker() functions are the Consumers. They stand at the delivery end of the conveyor belt, taking ports from the queue and scanning them.
 1 - `port_queue.get()` "Give me a Job"
 2 - `scan_port(...)` "I'll do the Job"
 3 - `port_queue.task_done()` "Job Complete"

 ### The Global Interpreter Lock (GIL)
 Pythons threads technically are not real threads because of the GIL. The GIL restricts python to executing only one CPU instruction at a time.
  - For CPU bound tasks (e.g. calculating prime numbers), Python threads are not effective because they cannot run in true parallel.
  - For I/O bound tasks (e.g. network requests, file I/O), Python threading is exellent.
   - When Thread A sends a packet and waits (blocks), the GIL realises that Thread A is waiting on the network. It releases the lock and lets Thread B run immediately. Which allows us to have hundreds of network requests in flight simultaneously.
