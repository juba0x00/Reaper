

import socket
import turtle
from os import path


from modules.drone import Drone


PORT = 5556 # Port to listen on
DRONE_GIF = "/home/juba/code/python/Reaper/media/drone.gif"
MAP_GIF = "/home/juba/code/python/Reaper/media/map2.gif"

class Simulator:
    """
    Simulates the drone's movements on a turtle graphics screen based on received commands.

    Attributes:
    - arrow (turtle.Turtle): The turtle object representing the drone.
    - socket (socket.socket): The socket used for receiving commands.

    Methods:
    - __init__: Initializes the Simulator object.
    - move_drone: Moves the drone on the screen based on a command.
    - listen: Listens for commands on a socket.
    - simulate: Simulates the drone's movements based on received commands.
    """


    def __init__(self, drone: Drone) -> None:
        """
        Initializes the Simulator object.

        Creates a turtle graphics screen and sets up the drone's initial position and appearance.
        Starts listening for commands on a socket and simulates the drone's movements.

        Args:
        - drone (Drone): The Drone object to simulate.
        """
        screen = turtle.Screen()
        screen.setup(1920, 1080)
        self.arrow = turtle.Turtle()
        # turtle.register_shape(path.join(path.dirname(__file__), 'media', 'drone.gif'))
        turtle.register_shape(DRONE_GIF)
        screen.bgpic(MAP_GIF)
        # screen.bgpic(path.join(path.dirname(__file__), 'media', 'map2.gif'))
        
        turtle.bgcolor("black")
        turtle.pencolor("red")
        self.arrow.shape(DRONE_GIF)
        # self.arrow.shape(path.join(path.dirname(__file__), 'media', 'drone.gif'))
        self.arrow.shapesize(stretch_wid=2, stretch_len=2, outline=8)
        self.socket = self.listen()
        self.simulate(drone)
        self.takeoff = False



    def move_drone(self, drone, direction) -> bool:
        """
        Moves the drone on the screen based on a direction.

        If the drone is in the air, it moves the drone in the specified direction.

        Args:
        - drone (Drone): The Drone object.
        - direction (str): The direction in which to move the drone.

        Returns:
        - Success: True if the drone is in the air and the direction is valid, False otherwise.
        """
        if drone.takeoff:
            if direction == "up":
                self.arrow.setheading(90)
                self.arrow.forward(10)
            elif direction == "down":
                self.arrow.setheading(270)
                self.arrow.forward(10)
            elif direction == "right":
                self.arrow.setheading(0)
                self.arrow.forward(10)
            elif direction == "left":
                self.arrow.setheading(180)
                self.arrow.forward(10)
            return True
        else:
            print("Drone is not in the air. Please take off first.")
            return False


    def listen(self) -> socket.socket:
        """
        Listens for commands on a socket.

        Returns:
        - socket.socket: The socket used for receiving commands.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", PORT))
        return sock


    def simulate(self, drone: Drone):
        """
        Simulates the drone's movements based on received commands.

        Receives commands from the socket and performs corresponding actions.

        Args:
        - drone (Drone): The Drone object to simulate.
        """
        while True:
            data, _ = self.socket.recvfrom(1024)
            command = data.decode().strip().split(',')[-1]

            if command == "2907510942":
                drone.turn_camera_on()
            elif command == "290741696":
                drone.takeoff = True
            elif command == "290751696":
                drone.takeoff = False
            else:
                if self.move_drone(drone, Drone.payload_messages[command]['operation']):
                    print(f"Received payload [{command}]: {Drone.payload_messages[command]['print_message']}")
             