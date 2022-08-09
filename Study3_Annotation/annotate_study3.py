"""
Script: annotate_study3.py
Author: Chinmaib
Description: Parsing messages from the Minecraft messages bus which are in JSON format.
"""
import socket
from typing import Any, Dict, List, Set, TextIO
import os
import json
from dateutil.parser import parse
from dateutil.relativedelta import *
import datetime

import numpy as np
from Parser.Map import Map
from Parser.Trial import Trial, Position
from Common.Constants import Constants
from Common.Player import*

import matplotlib.pyplot as plt
from utils import *

# Declare location of files and folders.
if socket.gethostname() == 'kraken':
    data_dir="/home/chinmaib/tomcat/study3_data"
else:
    data_dir="/home/chinmai/src/ASIST/Scripts/JSON_Parser"

#team="TM000093"
#meta_file="Trial-T000451_Team-TM000075.metadata" 

meta_file='Trial-T000486_Team-TM000093.metadata'

def main():
    # Open metadata file for reading.
    meta_file_path = os.path.join(data_dir,meta_file)
    meta_fd = open(meta_file_path,'r')

    #################### PARSE METADATA JSON OBJECTS ##########################
    # Create an empty list to add multiple JSON objects in one line
    messages = []
    missionMessages = []     # Only messages realted to the mission.
    planningMessages= []     # Only messages realted to planning mission.
    trialMessage    = []
    groundTruthMessagesMap: Dict[str, Any] = {} 
  
    topics = set()
    # Go through the file line by line.
    for line in meta_fd:
        jsonMessage = None
        try:
            jsonMessage = json.loads(line)
        # json_line contains the JSON objects loaded.
        except:
            print (f"Bad json line of len:{len(line)},{line}")
        
        if jsonMessage is not None:

            if "topic" in jsonMessage:
                topics.add(jsonMessage["topic"])

                if jsonMessage["topic"] == MAP_TOPIC:
                    groundTruthMessagesMap["map"] = jsonMessage
                elif jsonMessage["topic"] == TRIAL_MSG:
                    trialMessage.append(jsonMessage)
                elif jsonMessage["topic"] == VICTIM_LIST_TOPIC:
                    groundTruthMessagesMap["victim_list"] = jsonMessage
                elif jsonMessage["topic"] == RUBBLE_LIST_TOPIC:
                    groundTruthMessagesMap["rubble_list"] = jsonMessage
                elif jsonMessage["topic"] == THREAT_PLATE_LIST_TOPIC:
                    groundTruthMessagesMap["threat_plate_list"] = jsonMessage
                elif jsonMessage["topic"] == VICTIM_SIGNAL_PLATE_LIST_TOPIC:
                    groundTruthMessagesMap["victim_signal_plate_list"] = jsonMessage
                elif jsonMessage["topic"] == MISSION_MSG:
                    missionMessages.append(jsonMessage)
                elif jsonMessage["topic"] == PLANNING_MSG:
                    planningMessages.append(jsonMessage)
                elif jsonMessage["topic"] in USED_TOPICS:
                    messages.append(jsonMessage)

    #trial._parseGroundTruthMessages(groundTruthMessagesMap)
    # Using the time stamp value in the header in the JSON file/messages, 
    # we sort the list of messages into a sorted list.
    sorted_messages = sorted(
        messages, key=lambda x: parse(x["header"]["timestamp"])
    )

    playerIdToColor = {}
    metadata = {}

    #################### EXTRACT PLAYER INFO ##########################
    # Player names, ID's, and matching colors.
    msg = trialMessage[0]
    # Client info field is a list of dictionary item with player information
    sub_info = msg["data"]["client_info"]
    # Player class is defined in sample_class
    P1 = Player(sub_info[0]["playername"],sub_info[0]["participant_id"], \
            sub_info[0]["callsign"])
    P2 = Player(sub_info[1]["playername"],sub_info[1]["participant_id"], \
            sub_info[1]["callsign"])
    P3 = Player(sub_info[2]["playername"],sub_info[2]["participant_id"], \
            sub_info[2]["callsign"])
    # P1 is Red
    # Define a counter.
    C = Counter()
    
    #################### EXTRACT MAP INFO ##########################
    rooms = []
    hallways = []
    treatmentAreas = []
    # PARSE MAP into rooms, hallways, and corridors.
    # NOTE: For older versions, extract bounding boxes and using player coordinates,
    # we will infer where they are in the MAP.
    # Rooms and areas are listed as list of places in the MAP JSON object.
    for location in groundTruthMessagesMap["map"]["data"]["semantic_map"]["locations"]:
    # List all location names and ID's separated by comma
        if ('Part' not in location["name"]) and ('UNKNOWN' not in location["name"]):
            if location["type"] == "room" or location["type"] == "bathroom":
                rooms.append(location["id"])
                #rooms.append((location["id"],location["name"]))
            elif location["type"] == "hallway":
                hallways.append(location["id"])
                #hallways.append((location["id"],location["name"]))
            elif location["type"] == "treatment":
                treatmentAreas.append(location["id"])
                #treatmentAreas.append((location["id"],location["name"]))
            #print(location["name"],',',location["id"],',',location["type"])
    #NOTE: staging area to be placed under hallways and not rooms.
    #################### EXTRACT START STOP TIMES ##########################

    # Mission start time
    missionStart = ''
    missionStop  = ''
    
    for message in missionMessages:
        if (message["data"]["mission_state"] == "Start"):
            missionStart=message["header"]["timestamp"]
        if (message["data"]["mission_state"] == "Stop"):
            missionStop=message["header"]["timestamp"]

    #print ("Mission Start: ",missionStart)
    #print ("Mission Stop : ",missionStop)

    #Planning session start stop. Once planning stops, actual mission begins.
    planningStop = ''
    if (len(planningMessages) < 2):
        print ("Error: Unable to retrieve planning messages\n")
        exit(0)
    for message in planningMessages:
        if (message["data"]["state"] == "Stop"):
            planningStop=message["header"]["timestamp"]
    planning_stop_time = parse(planningStop)

    # Round off Start time
    mission_start_time = parse(missionStart)
    # Rounding off the start time to the nearest microsecond.
    start_microsec = mission_start_time.microsecond
    delta = start_microsec%100000
    mission_start_round = mission_start_time - datetime.timedelta(microseconds=delta)

    # Round off Stop time to next millisecond.
    mission_stop_time = parse(missionStop)
    # Rounding off the start time to the nearest microsecond.
    stop_microsec = mission_stop_time.microsecond
    delta = 100000-(stop_microsec%100000)
    mission_stop_round = mission_stop_time + datetime.timedelta(microseconds=delta)

    t1 = mission_start_round
    t2 = t1 + datetime.timedelta(seconds=1)

    """ 
    # To extract all the topics present in the metadata file.
    topics = set()
    for message in sorted_messages:
        topics.add(message["topic"])
    for item in topics:
        print (item)
    """
    
    #################### EXTRACT PLAYER  MESSAGES ##########################
    #NOTE: Use a for loop here, for 3 players in player list.
    p1_msgs = []
    for message in sorted_messages:
        message_time = parse(message["header"]["timestamp"])
        # Messages should be within mission start to end.
        # We will not include planning messages here.
        if message_time < planning_stop_time or message_time > mission_stop_time:
            continue

        #if message["data"].has_key("participant_id"):
        if "participant_id" in message["data"]:
            if (message["data"]["participant_id"] == P1.pid):
                C.count1 += 1
                p1_msgs.append(message)
                #print ('Time :',message_time,'\t',message["data"]["mission_timer"],'\t', \
                #        message["topic"])
    print ('Total P1 player messages: ', C.count1)
    C.resetCount1()

    #################### GENERATE SEQUENCE ##########################
    #NOTE: Can be merged with above section
    # All players start from staging area.
    player_loc  = "hallway"
    triage      = "inactive"
    transport   = "inactive"
    label_sequence = []

    for msg in p1_msgs:
        label = []
        # UPDATE player location.
        if (msg["topic"] == "observations/events/player/location"):
            if "locations" in msg["data"]:
                if msg["data"]["locations"][0]["id"] in rooms:
                    player_loc = "room"
                elif msg["data"]["locations"][0]["id"] in hallways:
                    player_loc = "hallway"
                elif  msg["data"]["locations"][0]["id"] in treatmentAreas:
                    player_loc = "treatment"

        # Observations state indicates us about the players position and velocity
        if (msg["topic"].lower() == "observations/state"):
            # Player is stationary
            if msg["data"]["motion_x"] == 0 and msg["data"]["motion_z"] == 0:
                continue
                #print ("ST,0,",msg["data"]["mission_timer"])
            else:
                if player_loc == "hallway" or player_loc =="treatment":
                        continue
                        #print ("NV,1,",msg["data"]["mission_timer"])
                elif player_loc == "room":
                        continue
                    #print ("SR,2,",msg["data"]["mission_timer"])
                # There is a location called UNKOWN, we will ignore for now.
        
        # Door - LABEL
        if (msg["topic"].lower() == "observations/events/player/door"):
                if msg["data"]["open"] == True:
                        print ('Door opened at :',msg["data"]["mission_timer"])
                                # Open door label is 3
                                
        # Triage - ACTION
        if msg["topics"].lower() == "observations/events/player/triage":
            if triage == 'active':
                if msg["data"]["triage_state"] == "SUCCESSFUL":
                    triage = 'inactive'
                elif msg["data"]["triage_state"] == "UNSUCCESSFUL":
                    triage = 'inactive'
                        
            else:
                if msg["data"]["triage_state"] == "IN_PROGRESS":
                    traige = "active"
     
        # Victim pickup - ACTION
        # NOTE: There is a scenario where victim gets evacuated.
        if msg["topics"].lower() == "observations/events/player/victim_picked_up":
            transport = "active"
            
        # Victim dropped - ACTION
        if msg["topics"].lower() == "observations/events/player/victim_placed":
            transport = "inactive"

        # Marker placed. - LABEL
        if msg["topics"].lower() == "observations/events/player/marker_placed":

        # Marker removed. - LABEL
        if msg["topics"].lower() == "observations/events/player/marker_removed":

        # Tool Used, or selecting tool - LABEL
        if msg["topics"].lower() == "observations/events/player/tool_used":
        

    meta_fd.close()


main()
