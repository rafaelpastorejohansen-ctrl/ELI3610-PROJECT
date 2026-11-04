import socket

def send_message():
    message = "CARD,"
    message += input("Enter card: ")
    message += "\n"
    encoded_message = message.encode()
    robot.sendall(encoded_message)
    message = "DONE\n"
    encoded_message = message.encode()
    robot.sendall(encoded_message)

HOST = "127.0.0.1"
PORT = 5000

robot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
robot.connect((HOST, PORT))

print("Simulated UR3 connected!")

received_data = robot.recv(1024)
message = received_data.decode()
action, num = message.split(",")
num = int(num)

for i in range(num*2 + 1):
    send_message()

message = "DONE\n"
encoded_message = message.encode()
robot.sendall(encoded_message)

while True:
    received_data = robot.recv(1024)
    message = received_data.decode()
    if received_data == b"":
        break
    print(f"Received: {message}")

    command, player, hand, card_num = message.strip().split(",")

    if command == "HIT":
        send_message()
    elif command == "REVEAL":
        send_message()
    elif command == "SPLIT":
        message = "DONE\n"
        encoded_message = message.encode()
        robot.sendall(encoded_message)