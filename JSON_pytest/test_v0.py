"""
Script: test.py
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

# Declare location of files and folders.
data_dir="/home/chinmai/src/ASIST/Study3"
team="TM000075"
meta_file="NotHSRData_TrialMessages_Trial-T000451_Team-TM000075_Member-na_CondBtwn-ASI-CMU-CRA_CondWin-na_Vers-1.metadata" 
meta_file_path = os.path.join(data_dir,team,meta_file)

test_file = "sample1.metadata"
"""
# These variables were declared as static variables in a trial class 
# object. For now I am declaring them as global variables for use.
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
"""

def main():
    # Open metadata file for reading.
    meta_fd = open(meta_file_path,'r')
    #data = json.dumps(meta_fd)
    # Create a Trial Object. Definition in Parser/Trial.py
    # Trial class atributes and methods defined by Paulo 
    trial = Trial()




    # Create an empty list to add multiple JSON objects in one line
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
                """
                if jsonMessage["topic"] == Trial.MAP_TOPIC:
                    groundTruthMessagesMap["map"] = jsonMessage
                elif jsonMessage["topic"] == Trial.VICTIM_LIST_TOPIC:
                    groundTruthMessagesMap["victim_list"] = jsonMessage
                """
                # Here the MAP_TOPIC, VICTIM_LIST_TOPIC and so on, are defined
                # as class attribures. Instead of Trial.MAP_TOPIC I am using
                # just MAP_TOPIC here.
                if jsonMessage["topic"] == RUBBLE_LIST_TOPIC:
                    groundTruthMessagesMap["rubble_list"] = jsonMessage
                if jsonMessage["topic"] == THREAT_PLATE_LIST_TOPIC:
                    groundTruthMessagesMap["threat_plate_list"] = jsonMessage
                if jsonMessage["topic"] == VICTIM_SIGNAL_PLATE_LIST_TOPIC:
                    groundTruthMessagesMap["victim_signal_plate_list"] = jsonMessage
                elif jsonMessage["topic"] in USED_TOPICS:
                    messages.append(jsonMessage)

        #self._parseGroundTruthMessages(groundTruthMessagesMap)

    sorted_messages = sorted(
        messages, key=lambda x: parse(x["header"]["timestamp"])
    )

    #jsonMessage.append(json_line)
    count += 1
    #if (count == 200):
    #    break
    # Removing 1 element from the list.Since it's the header and doesn't contain topic
    #del json_data[0]
    
    #s = set()
    #for item in json_data:
        #print (item["topic"])    
        #s.add(item['topic'])
        
    #s_sort= sorted(s)
    #for term in s_sort:print (term)

    #Pretty Printing JSON objects.
    #json_fmt_str = json.dumps(json_data[12], indent=2)
    #print (json_fmt_str)

    """
    count = 0
    
    # Lets read the lines of the metadata file one by one
    while True:
        count +=1 
        line = meta_fd.readline()

        if not line:
        #if count == 10:
            break
        #print("Line{}: {}".format(count,line.strip()))
        print(line.split(',',1)[0])
    """
main()
