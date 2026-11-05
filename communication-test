from robot_connection import RobotConnection

robot = RobotConnection(port=5000)
robot.connect()                       # waits for the robot, then expects READY
print("Got READY from robot")

for i in range(1, 4):
    message = f"({i},0.1,0.2,0.3,0.4,0.5,0.6)"
    robot.send_command(message)
    print(f"Sent:     {message}")
    reply = robot.receive_message()
    print(f"Received: {reply}")

robot.send_command("(9,0,0,0,0,0,0)")
print("Received:", robot.receive_message())
print("Communication test OK")
