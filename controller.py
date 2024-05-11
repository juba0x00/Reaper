#!/usr/bin/env python3
import socket
import customtkinter
import pickle
import socket
import struct

import cv2
from argparse import ArgumentParser

PORT = 5556

def send_payload(command, seq_num):
    """
    Sends a payload command to the drone.

    Args:
        command (str): The command to send.
        seq_num (int): The sequence number of the command.

    Raises:
        Exception: If there is an error sending the payload.

    """
    payloads = {
        "up": "AT*REF={},290717696\r",
        "down": "AT*REF={},290711696\r",
        "right": "AT*REF={},290721696\r",
        "left": "AT*REF={},290731696\r",
        "takeoff": "AT*REF={},290741696\r",
        "land": "AT*REF={},290751696\r",
        "turnoncamera": "AT*REF={},2907510942\r"
    }
    try:
        payload = payloads[command]
        formatted_payload = payload.format(seq_num)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(formatted_payload.encode(), (drone_ip, PORT))
        sock.close()
        log("Payload sent successfully: " + formatted_payload)
    except Exception as e:
        log("Error: " + str(e))

def send_command(command):
    """
    Sends a command to the drone.

    Args:
        command (str): The command to send.

    """
    seq_num = 0
    if command == "turnoncamera": #TODO fix video streaming
        send_payload(command, 0)

        display_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket created')
        display_socket.connect((drone_ip, 9090))
        print('Socket bind complete')
        print('Socket now listening')

        data = b'' 
        payload_size = struct.calcsize("L") 

        while True:
            try:
                # Retrieve message size
                while len(data) < payload_size:
                    data += display_socket.recv(4096)

                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("L", packed_msg_size)[0] 

                # Retrieve all data based on message size
                while len(data) < msg_size:
                    data += display_socket.recv(4096)

                frame_data = data[:msg_size]
                data = data[msg_size:]

                # Extract frame
                frame = pickle.loads(frame_data)

                # Display
                cv2.imshow('frame', frame)
                cv2.waitKey(1)
                # make it stop by closing the window
                if cv2.getWindowProperty('frame', cv2.WND_PROP_VISIBLE) < 1:
                    break
            except KeyboardInterrupt:
                print('close camera...')
                break
    else:
        send_payload(command, seq_num)
        seq_num += 1

def log(message):
    """
    Logs a message to the log_text area.

    Args:
        message (str): The message to log.

    """
    log_text.insert(customtkinter.END, message + "\n")
    log_text.see(customtkinter.END)

def DroneControllerPage():
    """
    Creates buttons and log_text area for the drone controller page.

    """
    # Create buttons for each command
    button_up = customtkinter.CTkButton(master=root, text="Up ⬆️", command=lambda: send_command("up"))
    button_up.grid(row=1, column=250, padx=3, pady=(10,2))

    button_down = customtkinter.CTkButton(master=root, text="Down ⬇️", command=lambda: send_command("down"))
    button_down.grid(row=5, column=250, padx=3, pady=(2,10))

    button_right = customtkinter.CTkButton(master=root, text="Right ➡️", command=lambda: send_command("right"))
    button_right.grid(row=4, column=270, padx=(2,10), pady=3)

    button_left = customtkinter.CTkButton(master=root, text="Left ⬅️", command=lambda: send_command("left"))
    button_left.grid(row=4, column=230, padx=(10,2), pady=3)

    button_takeoff = customtkinter.CTkButton(master=root, text="Takeoff 🚀", command=lambda: send_command("takeoff"))
    button_takeoff.grid(row=7, column=230, padx=5, pady=(20,3))

    button_land = customtkinter.CTkButton(master=root, text="Land 🛬", command=lambda: send_command("land"))
    button_land.grid(row=7, column=270, padx=5, pady=(20,3))

    button_camera = customtkinter.CTkButton(master=root, text="Turn On Camera 📷", command=lambda:send_command("turnoncamera"))
    button_camera.grid(row=7, column=250, padx=5, pady=(20,3))

    # Log text area
    global log_text
    log_text = customtkinter.CTkTextbox(master=root, height=200, width=400)
    log_text.grid(row=4, column=250, padx=20, pady=20)

def parse_ip() -> str:
    """
    Parses the drone IP address from the command line arguments.

    Returns:
        str: The drone IP address.

    """
    parser = ArgumentParser()
    parser.add_argument('drone_ip', help='Drone IP Address')
    return parser.parse_args().drone_ip

if __name__ == "__main__":
    try:
        drone_ip = parse_ip()
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("green")
        root = customtkinter.CTk()
        root.geometry("850x550")

        DroneControllerPage()
        root.mainloop()
        print("Final selected drone IP:", drone_ip)
    except KeyboardInterrupt:
        print("Exiting...")
        exit(0)

