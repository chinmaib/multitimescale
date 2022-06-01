"""
Script: annotate_study3.py
Author: Chinmaib

Description: Parsing messages from the Minecraft messages bus which are in JSON format.
"""
from typing import Any, Dict, List, Set, TextIO
import os
import json
from dateutil.parser import parse
import numpy as np
from Parser.Map import Map
from Parser.Trial import Trial, Position
from Common.Constants import Constants
import matplotlib.pyplot as plt

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
    #trial = Trial()
    #trial.parse(meta_fd)

    # Create an empty list to add multiple JSON objects in one line
    map_msg = []
    messages = []
    groundTruthMessagesMap: Dict[str, Any] = {}
    
    count = 0
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
                elif jsonMessage["topic"] == VICTIM_LIST_TOPIC:
                    groundTruthMessagesMap["victim_list"] = jsonMessage
                if jsonMessage["topic"] == RUBBLE_LIST_TOPIC:
                    groundTruthMessagesMap["rubble_list"] = jsonMessage
                if jsonMessage["topic"] == THREAT_PLATE_LIST_TOPIC:
                    groundTruthMessagesMap["threat_plate_list"] = jsonMessage
                if jsonMessage["topic"] == VICTIM_SIGNAL_PLATE_LIST_TOPIC:
                    groundTruthMessagesMap["victim_signal_plate_list"] = jsonMessage
                elif jsonMessage["topic"] in USED_TOPICS:
                    messages.append(jsonMessage)

    #trial._parseGroundTruthMessages(groundTruthMessagesMap)

    sorted_messages = sorted(
        messages, key=lambda x: parse(x["header"]["timestamp"])
    )
    missionStarted = False
    playerIdToColor = {}
    metadata = {}

    # Sorted messages basically contains all the messages under USED TOPICS
    # except for ground truth information.

    #fw = open("sample_out.json","w")
    count = 0
    for message in sorted_messages:
        #json_obj = json.dumps(message)
        if (message["topic"].lower() == "trial"):
            print (message["header"]["message_type"])
        count +=1
    #fw.close()
    
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
