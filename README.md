# Multi-Robot-Parking-Slot-Navigation-System
The project simulates autonomous robot navigation in a 3-floor parking system using VPython. Robots are assigned slots based on user input and move autonomously. It manages real-time slot availability, parking durations, and queueing for limited second-floor slots with dynamic user interaction.


**How It Works**
The system features a 3-level parking building (Ground, First, and Second floor).
Each floor contains marked parking slots and supporting pillars visualized in 3D.
A total of 15 robots (5 per floor) are placed at the start.
The user inputs:
The slot number each robot should park in.
The time duration (in minutes) the robot should remain parked.


**Robot Behavior**
Robots autonomously move to their assigned parking slots.
Movement is smooth and animated within the 3D environment.
Ground floor is restricted to short-term parking (≤30 minutes).
The second floor has only 3 slots, so if all are taken, incoming robots are queued.
Once a robot’s time is up, the user is prompted to extend the time or vacate the slot.
If a slot on the second floor becomes free, the next robot in the queue takes its place.


**Behind the Scenes**
Uses Python’s threading module to handle multiple robots simultaneously.
Updates the status of filled and empty slots in real-time.
Manages slot assignments and robot movements dynamically.

