from vpython import *
import time
from threading import Thread, Lock
from queue import Queue

# Set up the scene with enhanced lighting
scene = canvas(title="Autonomous Robot Navigation with Multi-Floor Parking and Pillars",
               width=800, height=600, center=vector(0, 6, 0), background=color.black)
scene.autoscale = False
scene.lights = []
distant_light(direction=vector(1, 1, 1), color=color.white)
distant_light(direction=vector(-1, -1, -1), color=color.gray(0.5))

# Instructions for viewing
print("Instructions for viewing:")
print("- Scroll or use two-finger drag to zoom in/out.")
print("- Shift + drag to rotate around the center point.")

# Function to create a floor
def create_floor(y_offset, floor_number, is_top_floor=False):
    ground = box(pos=vector(0, y_offset - 0.1, 0), size=vector(20, 0.2, 20), color=color.gray(0.7))
    for x in range(-10, 11, 1):
        curve(pos=[vector(x, y_offset, -10), vector(x, y_offset, 10)], color=color.gray(0.4), radius=0.01)
    for z in range(-10, 11, 1):
        curve(pos=[vector(-10, y_offset, z), vector(10, y_offset, z)], color=color.gray(0.4), radius=0.01)
    
    pillar_height = 5 if not is_top_floor else 3
    pillar_positions = [vector(-10, y_offset - 0.1, -10), vector(-10, y_offset - 0.1, 10),
                        vector(10, y_offset - 0.1, -10), vector(10, y_offset - 0.1, 10)]
    for pos in pillar_positions:
        cylinder(pos=pos, axis=vector(0, pillar_height, 0), radius=0.3, color=color.gray(0.6))
    
    slots = []
    labels_list = []
    num_slots_per_side = 5 if floor_number != 2 else 3
    for i in range(num_slots_per_side):
        left_slot_number = f"{floor_number}{i + 1:02}"
        left_slot_pos = vector(-8 + i * 4, y_offset, -9)
        slots.append({'pos': left_slot_pos, 'number': left_slot_number})
        curve(pos=[
            vector(left_slot_pos.x - 1, y_offset + 0.01, left_slot_pos.z - 1),
            vector(left_slot_pos.x - 1, y_offset + 0.01, left_slot_pos.z + 1),
            vector(left_slot_pos.x + 1, y_offset + 0.01, left_slot_pos.z + 1),
            vector(left_slot_pos.x + 1, y_offset + 0.01, left_slot_pos.z - 1),
            vector(left_slot_pos.x - 1, y_offset + 0.01, left_slot_pos.z - 1)
        ], color=color.yellow, radius=0.05)
        labels_list.append(label(pos=vector(left_slot_pos.x, y_offset + 1, left_slot_pos.z),
                                 text=left_slot_number, height=10, box=False, color=vector(1, 1, 1)))
        
        if floor_number != 2:
            right_slot_number = f"{floor_number}{i + 6:02}"
            right_slot_pos = vector(-8 + i * 4, y_offset, 9)
            slots.append({'pos': right_slot_pos, 'number': right_slot_number})
            curve(pos=[
                vector(right_slot_pos.x - 1, y_offset + 0.01, right_slot_pos.z - 1),
                vector(right_slot_pos.x - 1, y_offset + 0.01, right_slot_pos.z + 1),
                vector(right_slot_pos.x + 1, y_offset + 0.01, right_slot_pos.z + 1),
                vector(right_slot_pos.x + 1, y_offset + 0.01, right_slot_pos.z - 1),
                vector(right_slot_pos.x - 1, y_offset + 0.01, right_slot_pos.z - 1)
            ], color=color.yellow, radius=0.05)
            labels_list.append(label(pos=vector(right_slot_pos.x, y_offset + 1, right_slot_pos.z),
                                     text=right_slot_number, height=10, box=False, color=vector(1, 1, 1)))
    
    return slots

# Create floors
ground_floor_slots = create_floor(0, 0)
first_floor_slots = create_floor(5, 1)
second_floor_slots = create_floor(10, 2, is_top_floor=True)

# Combine all slots
all_slots = ground_floor_slots + first_floor_slots + second_floor_slots
print("All available slots:", [slot['number'] for slot in all_slots])

occupied_slots = {}

class RobotCar:
    def __init__(self, pos, color=color.magenta):
        self.car_body = box(pos=vector(pos.x, pos.y + 0.25, pos.z), size=vector(1.5, 0.5, 1.0), color=color)
        self.shade = ellipsoid(pos=vector(pos.x, pos.y + 0.01, pos.z),
                               length=1.8, height=0.02, width=1.2,
                               color=vector(0.2, 0.2, 0.2), opacity=0.3)
        self.initial_pos = pos

    def move_to(self, target_pos):
        while abs(self.car_body.pos.x - target_pos.x) > 0.05 or \
              abs(self.car_body.pos.z - target_pos.z) > 0.05 or \
              abs(self.car_body.pos.y - target_pos.y) > 0.05:
            rate(40)
            direction = vector(target_pos.x - self.car_body.pos.x,
                               target_pos.y - self.car_body.pos.y,
                               target_pos.z - self.car_body.pos.z).norm()
            self.car_body.pos += direction * 0.1
            self.shade.pos = self.car_body.pos
            time.sleep(0.01)

status_label = label(pos=vector(0, 15, 0), text="", height=15, box=False, color=color.white)

def update_status_label():
    filled_slots = len(occupied_slots)
    empty_slots = len(all_slots) - filled_slots
    status_label.text = f"Parking Slots - Filled: {filled_slots}, Empty: {empty_slots}"

update_status_label()

# Define ground floor robot positions
ground_floor_positions = [
    vector(-9, 0, -4),
    vector(-9, 0, -2),
    vector(-9, 0, 0),
    vector(-9, 0, 2),
    vector(-9, 0, 4)
]

# Add 5 robots to each floor at specified positions
robots = [RobotCar(pos=ground_floor_positions[i], color=color.green) for i in range(5)]  # Ground floor
robots += [RobotCar(pos=vector(ground_floor_positions[i].x, 5, ground_floor_positions[i].z), color=color.red) for i in range(5)]  # First floor
robots += [RobotCar(pos=vector(ground_floor_positions[i].x, 10, ground_floor_positions[i].z), color=color.blue) for i in range(5)]  # Second floor

# Initialize available slots for the second floor
second_floor_slots_list = ["201", "202", "203"]
available_second_floor_slots = second_floor_slots_list.copy()
second_floor_waiting_queue = Queue()

# Collect inputs for all robots upfront
robot_data = []
for i in range(len(robots)):
    if i < 5:
        floor = "Ground Floor"
        robot_num = i + 1
    elif i < 10:
        floor = "First Floor"
        robot_num = i - 4
    else:
        floor = "Second Floor"
        robot_num = i - 9

    slot_number = input(f"Enter the parking slot number for Robot {robot_num} in {floor}: ")
    while slot_number in occupied_slots:
        print(f"Slot {slot_number} is already occupied. Choose another.")
        slot_number = input(f"Enter a new slot number for Robot {robot_num} in {floor}: ")
    
    if floor == "Second Floor":
        if slot_number not in second_floor_slots_list:
            print(f"Invalid slot number for Second Floor. Available slots are: {', '.join(second_floor_slots_list)}")
            slot_number = input(f"Enter a new slot number for Robot {robot_num} in {floor} (must be 201, 202, or 203): ")
            while slot_number not in second_floor_slots_list:
                print(f"Invalid slot number for Second Floor. Available slots are: {', '.join(second_floor_slots_list)}")
                slot_number = input(f"Enter a new slot number for Robot {robot_num} in {floor} (must be 201, 202, or 203): ")

    while True:
        stay_time_minutes = float(input(f"Enter the time (minutes) Robot {robot_num} in {floor} should stay: "))
        if i < 5 and stay_time_minutes > 30:
            print("Ground Floor is only for users whose parking time is less than 30 minutes. Please enter a new time.")
        else:
            break
    
    robot_data.append({
        'robot': robots[i],
        'slot_number': slot_number,
        'stay_time_minutes': stay_time_minutes,
        'floor': floor,
        'robot_num': robot_num,
        'index': i,
        'completed': False
    })

# Define locks for thread safety
data_lock = Lock()
prompt_queue = Queue()
prompt_lock = Lock()

# Move robots to their slots (modified for second floor waiting)
for floor_name in ["Ground Floor", "First Floor", "Second Floor"]:
    floor_robots = [data for data in robot_data if data['floor'] == floor_name]
    for robot_info in floor_robots:
        robot = robot_info['robot']
        slot_number = robot_info['slot_number']

        if floor_name == "Second Floor":
            with data_lock:
                if available_second_floor_slots:  # If a slot is available, assign it immediately
                    assigned_slot = available_second_floor_slots.pop(0)
                    robot_info['slot_number'] = assigned_slot
                    slot_number = assigned_slot
                    occupied_slots[slot_number] = robot
                    target_slot = next(slot for slot in all_slots if slot['number'] == slot_number)
                    print(f"Robot {robot_info['robot_num']} in {robot_info['floor']} moving to Slot {slot_number}...")
                    robot.move_to(target_slot['pos'])
                    update_status_label()
                    print(f"Robot {robot_info['robot_num']} in {robot_info['floor']} staying in Slot {slot_number} for {robot_info['stay_time_minutes']} minutes...")
                else:  # No slots available, add to waiting queue
                    print(f"No slots available for Robot {robot_info['robot_num']} in {floor_name}. Added to waiting queue...")
                    second_floor_waiting_queue.put(robot_info)
                    continue
        else:  # Ground and First Floor robots move immediately
            print(f"Moving to slot {slot_number}...")
            target_slot = next(slot for slot in all_slots if slot['number'] == slot_number)
            print(f"Robot {robot_info['robot_num']} in {robot_info['floor']} moving to Slot {slot_number}...")
            robot.move_to(target_slot['pos'])
            occupied_slots[slot_number] = robot
            update_status_label()
            print(f"Robot {robot_info['robot_num']} in {robot_info['floor']} staying in Slot {slot_number} for {robot_info['stay_time_minutes']} minutes...")

# Wait and prompt function
def wait_and_prompt(robot_info, prompt_queue, available_second_floor_slots, second_floor_waiting_queue):
    stay_time_seconds = robot_info['stay_time_minutes'] * 60
    start_time = time.time()
    time.sleep(stay_time_seconds)
    intended_completion_time = start_time + stay_time_seconds
    with prompt_lock:
        if not robot_info['completed']:
            floor_priority = {"Ground Floor": 0, "First Floor": 1, "Second Floor": 2}[robot_info['floor']]
            prompt_queue.put((intended_completion_time, floor_priority, robot_info))

# Start threads for robots that have moved to slots
threads = []
for robot_info in robot_data:
    if robot_info['slot_number'] in occupied_slots:  # Only start threads for robots in slots
        thread = Thread(target=wait_and_prompt, args=(robot_info, prompt_queue, available_second_floor_slots, second_floor_waiting_queue))
        thread.start()
        threads.append(thread)

# Main loop (modified to handle second floor waiting robots)
while True:
    all_completed = all(data['completed'] for data in robot_data)
    if all_completed:
        print("All robots have completed their waiting time. Restarting from Ground Floor...")
        with data_lock:
            for data in robot_data:
                data['completed'] = False
            while not prompt_queue.empty():
                prompt_queue.get()
            available_second_floor_slots = second_floor_slots_list.copy()
            while not second_floor_waiting_queue.empty():
                second_floor_waiting_queue.get()

    if not prompt_queue.empty():
        time.sleep(1)  # Collect prompts
        waiting_robots = []
        with prompt_lock:
            while not prompt_queue.empty():
                waiting_robots.append(prompt_queue.get())
        
        # Sort by floor priority (Ground > First > Second)
        waiting_robots.sort(key=lambda x: (x[1], x[0]))
        
        for completion_time, floor_priority, robot_info in waiting_robots:
            robot = robot_info['robot']
            slot_number = robot_info['slot_number']

            response = input(f"Should Robot {robot_info['robot_num']} in {robot_info['floor']} (Slot {slot_number}) stay longer? (yes/no): ").strip().lower()
            if response == "yes":
                extra_time_minutes = float(input(f"Enter additional time (minutes) for Robot {robot_info['robot_num']} in {robot_info['floor']}: "))
                extra_time_seconds = extra_time_minutes * 60
                time.sleep(extra_time_seconds)
            else:
                robot.move_to(robot.initial_pos)
                with data_lock:
                    del occupied_slots[slot_number]
                    if robot_info['floor'] == "Second Floor":
                        available_second_floor_slots.append(slot_number)
                        available_second_floor_slots.sort()
                        if not second_floor_waiting_queue.empty():
                            next_robot_info = second_floor_waiting_queue.get()
                            next_slot = available_second_floor_slots.pop(0)
                            next_robot_info['slot_number'] = next_slot
                            occupied_slots[next_slot] = next_robot_info['robot']
                            print(f"Slot {next_slot} is now available. Robot {next_robot_info['robot_num']} in {next_robot_info['floor']} moving to Slot {next_slot}...")
                            target_slot = next(slot for slot in all_slots if slot['number'] == next_slot)
                            next_robot_info['robot'].move_to(target_slot['pos'])
                            update_status_label()
                            print(f"Robot {next_robot_info['robot_num']} in {next_robot_info['floor']} staying in Slot {next_slot} for {next_robot_info['stay_time_minutes']} minutes...")
                            # Start the timer only after the robot reaches the slot
                            thread = Thread(target=wait_and_prompt, args=(next_robot_info, prompt_queue, available_second_floor_slots, second_floor_waiting_queue))
                            thread.start()
                            threads.append(thread)
                    update_status_label()
                    print(f"Robot {robot_info['robot_num']} in {robot_info['floor']} left Slot {slot_number}.")

            robot_info['completed'] = True

    time.sleep(0.1)

for thread in threads:
    thread.join()

print("All robots have completed their tasks.")
