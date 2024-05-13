
from subprocess import run, CalledProcessError
from cv2 import VideoCapture
import pickle
import struct
import socket


from media.ascii import ascii_drone


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
