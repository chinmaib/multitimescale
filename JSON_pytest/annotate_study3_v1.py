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
from Parser.Trial import Trial
from Common.Constants import Constants
import matplotlib.pyplot as plt

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

USED_TOPICS = [
    "trial",
    "observations/events/mission",
    "observations/state",
    "observations/events/scoreboard",
    "observations/events/player/role_selected",
    "observations/events/player/marker_placed",
    "minecraft/chat",
    "observations/events/player/triage",
    "observations/events/player/victim_picked_up",
    "observations/events/player/victim_placed",
    "observations/events/player/tool_used",
    "observations/events/player/marker_removed",
    "observations/events/player/rubble_destroyed",
    "observations/events/mission/perturbation",
    "observations/events/player/rubble_collapse",
    "observations/events/player/itemequipped",
    "agent/asr/final"
]

MAP_TOPIC = "ground_truth/semantic_map/initialized"
VICTIM_LIST_TOPIC = "ground_truth/mission/victims_list"
RUBBLE_LIST_TOPIC = "ground_truth/mission/blockages_list"
THREAT_PLATE_LIST_TOPIC = "ground_truth/mission/threatsign_list"
VICTIM_SIGNAL_PLATE_LIST_TOPIC = "ground_truth/mission/freezeblock_list"

def isMessageOf(message: json, type: str, subType: str):
    return message["header"]["message_type"].lower() == type.lower() and message["msg"][
        "sub_type"].lower() == subType.lower()



def main():
    # Open metadata file for reading.
    meta_file_path = os.path.join(data_dir,team,meta_file)
    #test_file = "sample1.metadata"
    meta_fd = open(meta_file_path,'r')

    # Create a Trial Object. Definition in Parser/Trial.py
    # Trial class atributes and methods defined by Paulo 
    #trial = Trial()
    #trial.parse(meta_fd)

    # The parse function takes care of everything here.
    # I want to print trial.metadata whi
    #print (trial.metadata.keys())
    #print (trial.metadata)

    # Printing player actions. There should be 900 of these
    # I will assime 0 - RED, 1 - GREEN, 2- BLUE
    #for act in trial.playersActions[2]:
    #    print (act)
    #json_fmt_str = json.dumps(trial.metadata, indent=2)
    #print (json_fmt_str)

    # First order of business will be to extract all the locations defined in the map
    #for location in trial.map["locations"]:
    #   print (location["name"])

    #plt.plot(trial.scores)
    #plt.show()

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
    # Sorted messages basically contains all the messages under USED TOPICS
    # except for ground truth information.

    for message in sorted_messages:
        if isMessageOf(message, "event", "Event:MissionState"):
            state = message["data"]["mission_state"].lower()
            if state == "start":
                missionStarted = True
            else:
                # Mission finished. Nothing else to parse.
                break
        elif Trial._isMessageOf(message, "trial", "start"):
            self.metadata["map_block_filename"] = message["data"]["map_block_filename"]
            self.metadata["trial_number"] = message["data"]["trial_number"]
            name = message["data"]["name"]
            self.metadata["team_number"] = name[:name.find("_")]
            self.metadata["player_ids"] = [playerId.strip() for playerId in message["data"]["subjects"]]
            for info in message["data"]["client_info"]:
                playerColor = info["callsign"].lower()
                playerId = info["participant_id"]
                playerIdToColor[playerId] = playerColor
                if playerColor == "red":
                    self.metadata["red_id"] = playerId
                if playerColor == "green":
                    self.metadata["green_id"] = playerId
                else:
                    self.metadata["blue_id"] = playerId
        elif Trial._isMessageOf(message, "trial", "stop"):
            # Trial finished. Nothing else to parse.
            break


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
    meta_fd.close()
main()
