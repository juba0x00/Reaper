#!/usr/bin/env python3

"""
This module contains the implementation of a drone simulator.

The Drone class represents a drone and provides methods for controlling the drone's movements and camera.
The Simulator class simulates the drone's movements on a turtle graphics screen based on received commands.

Classes:
- Drone: Represents a drone and provides methods for controlling the drone's movements and camera.
- Simulator: Simulates the drone's movements on a turtle graphics screen based on received commands.
"""



import socket
import turtle
from os import path

from subprocess import run, CalledProcessError
from cv2 import VideoCapture
import pickle
import struct
from media.ascii import ascii_drone

PORT = 5556  # Port to listen on


class Drone:
    """
    Represents a drone and provides methods for controlling the drone's movements and camera.

    Attributes:
    - payload_messages (dict): A mapping of payload IDs to corresponding messages and operations.
    - camera_started (bool): Indicates whether the camera is started or not.

    Methods:
    - __init__: Initializes the Drone object.
    - start_services: Starts FTP and SSH services.
    - turn_camera_on: Turns on the drone's camera.
    """

    payload_messages = {
        "290717696": {"print_message": "Drone goes up", "operation": "up"},
        "290711696": {"print_message": "Drone goes down", "operation": "down"},
        "290721696": {"print_message": "Drone moves right", "operation": "right"},
        "290731696": {"print_message": "Drone moves left", "operation": "left"},
        "290741696": {"print_message": "Drone takes off", "operation": "takeoff"},
        "290751696": {"print_message": "Drone lands", "operation": "land"},
        "2907510942": {"print_message": "Turn on camera", "operation": "turnoncamera"}
    }


    def __init__(self) -> None:
        """
        Initializes the Drone object.

        Sets the initial state of the drone and starts necessary services.
        """
        self.camera_started = False
        self.start_services()
        print(ascii_drone)
        print("Ready For Receiving Instructions")
        self.start_camera_listener()
        self.takeoff = False


    def start_services(self) -> None:
        """
        Starts FTP and SSH services.

        Raises:
        - CalledProcessError: If an error occurs while starting the services.
        """
        try:
            run(['sudo', 'systemctl', 'start', 'vsftpd'], check=True)
            print("FTP service started successfully.")
        except CalledProcessError as e:
            print(f"Error occurred: {e}")


    def start_camera_listener(self) -> socket.socket:
        self.camera_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.camera_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.camera_socket.bind(('', 9090))
        self.camera_socket.listen(10)


    def turn_camera_on(self) -> None:
        """
        Turns on the drone's camera.

        Captures frames from the camera and sends them over a socket connection.
        """
        try:
            cap = VideoCapture(0)
            print('Socket now listening')
            conn, _ = self.camera_socket.accept()

            while True:
                _, frame = cap.read()
                data = pickle.dumps(frame)
                message_size = struct.pack("L", len(data))
                conn.sendall(message_size + data)
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            cap.release()
            self.camera_socket.close()
            self.start_camera_listener()


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
        turtle.register_shape(path.join(path.dirname(__file__), 'media', 'drone.gif'))
        screen.bgpic(path.join(path.dirname(__file__), 'media', 'map2.gif'))
        turtle.bgcolor("black")
        turtle.pencolor("red")
        self.arrow.shape(path.join(path.dirname(__file__), 'media', 'drone.gif'))
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
                  

if __name__ == "__main__":
    try:
        reaper = Drone()
        sim = Simulator(reaper)
    except KeyboardInterrupt:
        print("Exiting...")
        exit(0)
