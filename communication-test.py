from connections import RobotConnection

ZERO = [0, 0, 0, 0, 0, 0]


def send(robot, command, pose=ZERO, pose2=ZERO):
    """Send a command and two poses (12 values), print and return the reply."""
    values = ",".join(f"{v:.5f}" for v in list(pose) + list(pose2))
    robot.send_command(command)
    robot.send_command(f"({values})")
    print(f"Sent:     {command}  ({values})")

    reply = robot.receive_message().strip()
    print(f"Received: {reply}\n")
    return reply


robot = RobotConnection(port=5000)
robot.connect()

ready = robot.receive_message().strip()
print(f"Received: {ready}\n")

# Commands that make the robot answer without moving
send(robot, "PING")         # unknown command, expect ERR
send(robot, "REGISTERED")   # no card held, expect DONE

# With the test stubs loaded on the robot, these only log, no movement
send(robot, "HIT", [0.44106, 0.07806, -0.02127, -0.46709, 3.08587, 0.00225])
send(robot, "SPLIT",
     [0.45688, 0.08086, -0.02077, -0.46709, 3.08587, 0.00225],
     [0.44763, 0.01592, -0.02127, -0.25069, 3.11088, 0.0])

send(robot, "QUIT")         # expect BYE, robot program ends

robot.connection.close()
robot.server.close()
print("Communication test finished")