import socket

class RobotConnection:
    def __init__(self, host="0.0.0.0", port=5000):
        self.host = host
        self.port = port
        self.server = None
        self.connection = None
        self.receive_buffer = ""
    
    def connect(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.server.bind((self.host, self.port))
        self.server.listen(1)
        
        print("Waiting for UR3 connection...")
        
        self.connection, address = self.server.accept()
        
        print(f"UR3 connected from {address}")
    
    def send_command(self, command):
        command = f"{command}\n"
        encoded_message = command.encode()
        self.connection.sendall(encoded_message)
    
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