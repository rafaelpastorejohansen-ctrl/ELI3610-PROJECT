import socket


#Class to handle the connection between the robot and pc.
class RobotConnection:
    def __init__(self, host="0.0.0.0", port=5000):
        self.host = host
        self.port = port
        self.server = None
        self.connection = None
        self.receive_buffer = ""
        
    #Method to establish a connection with the robot
    def connect(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.server.bind((self.host, self.port))
        self.server.listen(1)
        
        print("Waiting for UR3 connection...")
        
        self.connection, address = self.server.accept()
        
        print(f"UR3 connected from {address}")
        
    #Method to send a command to the robot
    def send_command(self, command):
        command = f"{command}\n"
        encoded_message = command.encode()
        self.connection.sendall(encoded_message)
        
    #Method to receive a message from the robot
    def receive_message(self):
        while "\n" not in self.receive_buffer:
            received_data = self.connection.recv(1024)
            if received_data == b"":
                self.connection.close()
                raise ConnectionError("UR3 disconnected")
            part_message = received_data.decode()
            self.receive_buffer += part_message
            
        message, self.receive_buffer = self.receive_buffer.split("\n", 1)
        
        return message

# Which reference object is which card value: match this to SOPAS
REFERENCE_TO_RANK = {
    0: "A", 1: "2", 2: "3", 3: "4", 4: "5", 5: "6", 6: "7",
    7: "8", 8: "9", 9: "10", 10: "J", 11: "Q", 12: "K",
}

class CameraConnection:
    def __init__(self, camera_ip = "192.168.12.85", port=2115):
        self.camera_ip = camera_ip
        self.port = port
        self.connection = None
        self.receive_buffer = ""

    #Method to connect to the camera (camera acts as server)
    def connect(self):
        print(f"Connecting to camera {self.camera_ip}:{self.port}...")
        self.connection = socket.create_connection((self.camera_ip, self.port), timeout=5)
        self.connection.settimeout(None)
        print("Camera connected")

    #Method to receive one line from the camera
    def receive_message(self):
        while "\n" not in self.receive_buffer:
            received_data = self.connection.recv(1024)
            if received_data == b"":
                self.connection.close()
                raise ConnectionError("Camera disconnected")
            part_message = received_data.decode(errors="ignore")
            self.receive_buffer += part_message

        message, self.receive_buffer = self.receive_buffer.split("\n", 1)

        return message.strip()

    #Method to throw away old results, so the next read is a new image
    def flush(self):
        self.receive_buffer = ""
        self.connection.setblocking(False)
        try:
            while self.connection.recv(1024):
                pass
        except (BlockingIOError, OSError):
            pass
        self.connection.setblocking(True)

    #Method to read one result and return the card value (or None)
    def read_card(self):
        line = self.receive_message()

        if not (line.startswith("BEGIN;") and line.endswith(";END")):
            print(f"Unknown result format, ignoring: {line!r}")
            return None

        fields = line.split(";")[1:-1]          # ['2', ref, image nr, decision]
        if len(fields) != 4:
            print(f"Wrong number of fields, ignoring: {line!r}")
            return None

        _, ref_object, image_number, decision = (int(f) for f in fields)

        if decision != 1:
            print(f"Image {image_number}: no match")
            return None

        rank = REFERENCE_TO_RANK.get(ref_object)
        print(f"Image {image_number}: {rank}")
        return rank