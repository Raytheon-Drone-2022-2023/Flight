from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
import time
import argparse
from enum import Enum
import math
import pydle
import time

class Units(Enum):
	meters = 1
	yards = 2

#Run this first
def initialize():
	global vehicle
	print('Connecting to vehicle...')
	vehicle = connect('/dev/ttyACM0', wait_ready=True, baud=57600)
	print("Ready")
	return 0

def deinitialize():
	vehicle.close()

#Arm the drone and take off. targetAlt is target altitude in meters
def arm_and_takeoff(targetAlt, gps=True):
	if gps:
		print("Set mode to GUIDED")
		vehicle.mode = VehicleMode("GUIDED")
	else:
		print("Set mode to GUIDED_NOGPS")
		vehicle.mode = VehicleMode("GUIDED_NOGPS")

	time.sleep(1)
	print("Arm drone")
	vehicle.arm()
	time.sleep(1)
	print("Taking off to " + str(targetAlt) + " meters")
	vehicle.simple_takeoff(targetAlt)
	while vehicle.location.global_relative_frame.alt < targetAlt * 0.95:
		print('Current height: %d meters\r' % vehicle.location.global_relative_frame.alt, end="")
	print("\nReached target altitude")

#Safely land the drone
def land():
	print("Deinitializing...")
	vehicle.mode = VehicleMode("LAND")
	while vehicle.armed:
		continue  
	print("Deinitialization complete")

def set_attitude(roll_angle = 20.0, pitch_angle = -20.0, yaw_rate = 20.0, thrust = 0.5, duration = 0):

    msg = vehicle.message_factory.set_attitude_target_encode(0,0,0,0b00000000,to_quaternion(roll_angle, pitch_angle),0,0,math.radians(yaw_rate),thrust)
    
    if duration != 0:
        modf = math.modf(duration)
        time.sleep(modf[0])
        for x in range(0,int(modf[1])):
            time.sleep(1)
            vehicle.send_mavlink(msg)

#Converts roll, pitch, and yaw to a quaternion value
def to_quaternion(roll = 0.0, pitch = 0.0, yaw = 0.0):
    t0 = math.cos(math.radians(yaw * 0.5))
    t1 = math.sin(math.radians(yaw * 0.5))
    t2 = math.cos(math.radians(roll * 0.5))
    t3 = math.sin(math.radians(roll * 0.5))
    t4 = math.cos(math.radians(pitch * 0.5))
    t5 = math.sin(math.radians(pitch * 0.5))

    w = t0 * t2 * t4 + t1 * t3 * t5
    x = t0 * t3 * t4 - t1 * t2 * t5
    y = t0 * t2 * t5 + t1 * t3 * t4
    z = t1 * t2 * t4 - t0 * t3 * t5

    return [w, x, y, z]

def get_coordinates_ahead(distance, direction=0, units=Units.meters):
    if units is Units.yards:
        distance /= 1.094

    R = 6378.1
    brng = math.radians(vehicle.heading + direction) # adjust bearing to desired direction
    d = float(distance) / 1000.0
    lat1 = math.radians(vehicle.location.global_relative_frame.lat)
    lon1 = math.radians(vehicle.location.global_relative_frame.lon)
    lat2 = math.asin(math.sin(lat1) * math.cos(d / R) +
                     math.cos(lat1) * math.sin(d / R) * math.cos(brng))
    lon2 = lon1 + math.atan2(math.sin(brng) * math.sin(d / R) *
                             math.cos(lat1), math.cos(d / R) - math.sin(lat1) * math.sin(lat2))
    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)
    
    return LocationGlobalRelative(lat2, lon2, vehicle.location.global_relative_frame.alt)


def get_distance_to(location, units=Units.meters):
    lat1 = vehicle.location.global_relative_frame.lat
    lng1 = vehicle.location.global_relative_frame.lon
    lat2 = location.lat
    lng2 = location.lon
    r = 6371000
    dLat = deg_to_rad(lat2 - lat1)
    dLng = deg_to_rad(lng2 - lng1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(deg_to_rad(lat1)) * \
        math.cos(deg_to_rad(lat2)) * math.sin(dLng / 2) * math.sin(dLng / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = r * c
    if units is Units.yards:
        distance *= 1.094

    return distance


def fly_to_point(location, speed=1):
    if check_status():
        print("Flying to target location")
        vehicle.simple_goto(location, groundspeed=speed)
        while get_distance_to(location) > 1:
            # time.sleep(1)
            print('%d yards away            \r' % get_distance_to(location, Units.yards), end="")

        print('\nReached target location')
    else:
        print('EMERGENCY!\nLanding...')
    
def check_status():
    return vehicle.system_status != 'EMERGENCY' or vehicle.system_status != 'CRITICAL'
    
def fly_to_points(locations, speed=1):
    for i in range(len(locations)):
        if check_status():
            print('Flying to target', i + 1)
            vehicle.simple_goto(locations[i], groundspeed=speed)
            while get_distance_to(locations[i]) > 1:
                time.sleep(1)
                print('%d yards away            \r' % get_distance_to(locations[i], Units.yards), end="")
                
            print('\nReached target', i + 1)
            
        else:
            land()
            vehicle.close()
            
    return 0

def send_ned_velocity(velocity_x, velocity_y, velocity_z, duration):
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, # frame relative to current heading
        0b0000111111000111, # type_mask (only speeds enabled)
        0, 0, 0, # x, y, z positions (not used)
        velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
        0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

    for x in range(0, duration):
        vehicle.send_mavlink(msg)
        time.sleep(1)
        
def fly_simple_zig_zag(zigs=3, distance=15):
    fly_to_point(get_coordinates_ahead(distance), 1.5)
    for i in range(zigs):
        if i % 2 == 0:
            fly_to_point(get_coordinates_ahead(2, 90), 1.5)
            fly_to_point(get_coordinates_ahead(distance,90), 1.5)
        else:
            fly_to_point(get_coordinates_ahead(2, -90), 1.5)
            fly_to_point(get_coordinates_ahead(distance,-90), 1.5)

# Simple echo bot.
class MyOwnBot(pydle.Client):
    async def on_connect(self):
        await self.join('#RTXDrone')
        initialize()
        time.sleep(5)
        await self.messsage('#RTXDrone', "Taking off...")
        arm_and_takeoff(2.5, gps=True)
        await self.messsage('#RTXDrone', "Starting zig zag...")
        fly_simple_zig_zag()
        await self.messsage('#RTXDrone', "Landing...")
        land()
        vehicle.close()

    async def on_message(self, target, source, message):
         # don't respond to our own messages, as this leads to a positive feedback loop
         if source != self.nickname:
            await self.message(target, 'test')

vehicle = None

deg_to_rad = lambda deg: deg * (math.pi / 180)

client = MyOwnBot('MyBot', realname='My Bot')
client.run('chat.freenode.net', tls=True, tls_verify=False)

# initialize()
# time.sleep(5)
# arm_and_takeoff(2.5, gps=True)
# fly_simple_zig_zag()
# land()
# vehicle.close()