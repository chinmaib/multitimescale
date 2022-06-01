"""
Script: annotate_study3.py
Author: Chinmaib
Description: Parsing messages from the Minecraft messages bus which are in JSON format.
"""

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
import matplotlib.pyplot as plt
from sample_class import *
from utils import *

# Declare location of files and folders.
data_dir="/home/chinmai/src/ASIST/Study3"
team="TM000075"
meta_file="NotHSRData_TrialMessages_Trial-T000451_Team-TM000075_Member-na_CondBtwn-ASI-CMU-CRA_CondWin-na_Vers-1.metadata" 

class Block:
    """
    This class represents a block in the map. The map will be defined as a set of blocks because we will perform
    set operations do define the empty space inside complex areas.
    """

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                getattr(other, 'x', None) == self.x and
                getattr(other, 'y', None) == self.y)

    def __hash__(self):
        return hash(f"{self.x},{self.y}")

def main():
    # Open metadata file for reading.
    meta_file_path = os.path.join(data_dir,team,meta_file)
    meta_fd = open(meta_file_path,'r')

    # Create a Trial Object. Definition in Parser/Trial.py
    # Trial class atributes and methods defined by Paulo 

    # Create an empty list to add multiple JSON objects in one line
    #map_msg = []        # RMV?
    messages = []
    missionMessages = []     # Only messages realted to the mission.
    trialMessage=[]
    groundTruthMessagesMap: Dict[str, Any] = {} # RMV
  
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

    # Extract trail informaion.
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

    # Sorted messages basically contains all the messages under USED TOPICS
    # except for ground truth information, mission, and trial

    # Define a counter.
    C = Counter()
    tools = []
    
    # Mission start time
    missionStart = ''
    missionStop  = ''
    
    for message in missionMessages:
        if (message["data"]["mission_state"] == "Start"):
            missionStart=message["header"]["timestamp"]
        if (message["data"]["mission_state"] == "Stop"):
            missionStop=message["header"]["timestamp"]

    print ("Mission Start: ",missionStart)
    print ("Mission Stop : ",missionStop)

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
    #t1 = t1 + datetime.timedelta(seconds=603)
    #t2 = t1 + datetime.timedelta(milliseconds=100)
    t2 = t1 + datetime.timedelta(seconds=1)
    #print(mission_start_round)
    #print(mission_stop_round)

    """
    To extract all the topics present in the metadata file.
    topics = set()
    for message in sorted_messages:
        topics.add(message["topic"])
    for item in topics:
        print (item)

    """
   
    while (t2 < mission_stop_round):
        C.count1 += 1       # Count 1 to keep track of total time steps.
        #print (t1, t2)
        
        for message in sorted_messages:
            message_time = parse(message["header"]["timestamp"])
            if (message_time >= t1 and message_time < t2):
                #print (message_time)
                print (message["topic"])
                C.count2 += 1
            if (message_time > t2):
                break
        print ('Total messages within range: ',C.count2)
        C.resetCount2()
        
        t1 = t2
        #t2 = t2 + datetime.timedelta(milliseconds=100)
        t2 = t2 + datetime.timedelta(seconds=1)
        print (C.count1)
    print ('Total time steps: ',C.count1)
    C.resetCount1()

    """
    for message in sorted_messages:
        if (message["topic"].lower() == "observations/events/player/tool_used"):
            if 'RED' in message["data"]["playername"]:
                red_count += 1
                rx = message["data"]["x"]
                ry = message["data"]["y"]
                rz = message["data"]["z"]
                red_coords.append([rx,ry,rz])

            elif 'BLUE' in message["data"]["playername"]:
                blue_count += 1
            elif 'GREEN' in message["data"]["playername"]:
                green_count += 1
            #print (message["header"]["message_type"])
            count +=1
         
        if (message["topic"].lower() == "observations/events/player/marker_placed"):
            marker_count += 1
            markers.add(message["data"]["type"])
    for item in markers:
        print (item)

    print ('Total no. of markers placed',marker_count)
    #fw.close()
    print ('Observation state messages: ',count)
    print ('Observation state RED messages: ',red_count)
    print ('Observation state GREEN messages: ',green_count)
    print ('Observation state BLUE messages: ',blue_count)
    print (len(red_coords))
    red_coords_array = np.asarray(red_coords)
    print (red_coords_array.shape)
    """

    exit(1)
    ############################################################################

    for message in sorted_messages:
        # First checking if the mission starts
        # NOTE: For different versions of the study, the mission timer starts at
        # different values. 15:03 or 17:00 in the latest version of the testbed.

        if isMessageOf(message, "event", "Event:MissionState"):
            state = message["data"]["mission_state"].lower()
            if state == "start":
                missionStarted = True

        # Check if trial ends.
        elif isMessageOf(message, "trial", "stop"):
            # Trial finished. Nothing else to parse.
            break

        # Check if trial starts, if yes then record all the data.
        elif isMessageOf(message, "trial", "start"):
            metadata["map_block_filename"] = message["data"]["map_block_filename"]
            metadata["trial_number"] = message["data"]["trial_number"]
            #Trial name
            name = message["data"]["name"]
            metadata["team_number"] = name[:name.find("_")]
            metadata["player_ids"] = [playerId.strip() for playerId in message["data"]["subjects"]]
            # The field client info in the JSON message contains nested JSON objects.
            # Here we extract those values. 
            # Client info is a list. Hence we use a for loop.
            for info in message["data"]["client_info"]:
                # We retrive information about player color and link it their ID.
                playerColor = info["callsign"].lower()  # Callsign is the color red, green or blue
                playerId = info["participant_id"]
                # NOT SURE WHATS THIS IS FOR.
                playerIdToColor[playerId] = playerColor

                if playerColor == "red":
                    metadata["red_id"] = playerId
                if playerColor == "green":
                    metadata["green_id"] = playerId
                else:
                    metadata["blue_id"] = playerId
        # A trial starts before the players can select roles. 
        # Here we are assuming that some of the variables are already populated
        # For example the playerIdToColor list.

        elif isMessageOf(message, "event", "Event:RoleSelected"):
            role = getRoleFromStringType(message["data"]["new_role"].lower())
            playerId = message["data"]["participant_id"]
            # Retrieve player color from player ID.
            playerColor = playerIdToColor[playerId]
            # NOTE: From Study 3 onwards, the player color to role is always fixed!
            if playerColor == "red":
                metadata["red_role"] = role
            elif playerColor == "green":
                metadata["green_role"] = role
            else:
                metadata["blue_role"] = role
        
        # Processing observation/state, which is mainly player position
        # For this, I will need the MAP to be parsed first.
        elif Trial._isMessageOf(message, "observation", "State"):
            playerId = message["data"]["participant_id"]
            playerColor = playerIdToColor[playerId]
            x = message["data"]["x"] - self.map.metadata["min_x"]
            y = message["data"]["z"] - self.map.metadata["min_y"]
            yaw = message["data"]["yaw"]
            position = Position(x, y)

            currentPlayersYaws[Constants.PLAYER_COLOR_MAP[playerColor].value] = yaw

            if len(currentPlayersPositions[Constants.PLAYER_COLOR_MAP[playerColor].value]) > 0:
                if currentPlayersPositions[Constants.PLAYER_COLOR_MAP[playerColor].value][-1] != position:
                    # Only add the new position if the player moved
                    currentPlayersPositions[Constants.PLAYER_COLOR_MAP[playerColor].value].append(position)
            else:
                currentPlayersPositions[Constants.PLAYER_COLOR_MAP[playerColor].value].append(position)

        elif Trial._isMessageOf(message, "event", "Event:ItemEquipped"):
            playerId = message["data"]["participant_id"]
            playerColor = playerIdToColor[playerId]

            itemName = message["data"]["equippeditemname"]
            currentPlayersEquippedItems[
                Constants.PLAYER_COLOR_MAP[playerColor].value] = Trial._getItemTypeFromStringType(itemName)
    """
    rooms = {}
    roomParts = {}
    roomBlocks = set()

    for location in groundTruthMessagesMap["map"]["data"]["semantic_map"]["locations"]:

        if "child_locations" in location:
            rooms[location["id"]] = {"parts": location["child_locations"]}
        else:
            coordinates = location["bounds"]["coordinates"]
            x1 = coordinates[0]["x"]
            y1 = coordinates[0]["z"]
            x2 = coordinates[1]["x"]
            y2 = coordinates[1]["z"]
            bounds = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
            if "_part" in location["type"]:
                roomParts[location["id"]] = {"bounds": bounds}
            else:
                for x in range(x1 - 1, x2 + 1, 1):
                    roomBlocks.add(Block(x, y1 - 1))
                    roomBlocks.add(Block(x, y2))
                for y in range(y1 - 1, y2 + 1, 1):
                    roomBlocks.add(Block(x1 - 1, y))
                    roomBlocks.add(Block(x2, y))
    """
    meta_fd.close()


main()
