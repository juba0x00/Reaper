#!/usr/bin/env python3
from modules.drone import Drone
from modules.gui import Simulator


"""
This module contains the implementation of a drone simulator.

The Drone class represents a drone and provides methods for controlling the drone's movements and camera.
The Simulator class simulates the drone's movements on a turtle graphics screen based on received commands.

Classes:
- Drone: Represents a drone and provides methods for controlling the drone's movements and camera.
- Simulator: Simulates the drone's movements on a turtle graphics screen based on received commands.
"""

     

if __name__ == "__main__":
    try:
        reaper = Drone()
        sim = Simulator(reaper)
    except KeyboardInterrupt:
        print("Exiting...")
        exit(0)
