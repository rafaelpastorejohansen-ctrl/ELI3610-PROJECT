import socket

CAMERA_IP = "192.168.12.85"
PORTS = list(range(2100, 2130)) + list(range(5000, 5010))

for port in PORTS:
    try:
        s = socket.create_connection((CAMERA_IP, port), timeout=0.5)
    except OSError:
        continue
    print(f"Port {port} is open, listening for 5 s...")
    s.settimeout(5)
    try:
        data = s.recv(1024)
        print(f"  received: {data!r}")
    except socket.timeout:
        print("  nothing received")
    s.close()