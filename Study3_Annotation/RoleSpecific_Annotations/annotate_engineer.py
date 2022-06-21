"""
Script: annotate_engineer.py
Author: Chinmaib

Description: Parsing messages from the Minecraft messages bus which are in JSON format and
annotating basic set of actions performed by the engineer in the Minecraft SAR mission.
"""
import sys
# Adding parent folder to import search.
sys.path.append("..") 

# As a command line argument we should pass, team and trial
if (len(sys.argv) < 2):
    print ('Usage: python3 annotate_medic.py <TM000XXX> <Trial000XXX>')
    exit(0)

from typing import Any, Dict, List, Set, TextIO
import os
import json
from dateutil.parser import parse
from dateutil.relativedelta import *
import datetime

import numpy as np
from Parser.Map import Map
from Common.Player import*

from utils import *

# Declare location of files and folders.
#data_dir="/home/chinmai/src/ASIST/Study3/"
data_dir="/home/chinmaib/tomcat/HSR_noadvisor"
#out_dir ="/home/chinmai/src/ASIST/Scripts/Study3_Annotation/Output"
out_dir ="/home/chinmaib/tomcat/annotations"

#team="TM000093"
team  = sys.argv[1]
trial = sys.argv[2]
#meta_file="Trial-T000451_Team-TM000075.metadata" 

def main():
    # Open metadata file for reading.
    global data_dir, out_dir, team, trial
    meta_file = 'HSRData_TrialMessages_Trial-'+trial+'_Team-'+team+ \
            '_Member-na_CondBtwn-none_CondWin-na_Vers-5.metadata'
    #meta_file = 'Trial-'+trial+'_Team-'+team+'.metadata'
    meta_file_path = os.path.join(data_dir,meta_file)
    #meta_file_path = os.path.join(data_dir,team,meta_file)
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

    # Close meta file.
    meta_fd.close()

    #################### EXTRACT PLAYER INFO ##########################
    # Player names, ID's, and matching colors.
    msg = trialMessage[0]
    # Client info field is a list of dictionary item with player information
    trial_name = msg["data"]["name"]
    trial_num  = msg["data"]["trial_number"]
    sub_info = msg["data"]["client_info"]

    # Client info is a list of player information.
    for i in range(0,3):        #3 players
        if sub_info[i]["callsign"] == "Blue":
            PL = Player(sub_info[i]["playername"],sub_info[i]["participant_id"], \
                sub_info[i]["callsign"])
            break

    # PL is Blue - Engineer
    # Define a counter.
    C = Counter()
    
    #################### EXTRACT MAP INFO ##########################
    rooms = []
    hallways = []
    treatmentAreas = []
    # PARSE MAP into rooms, hallways, and corridors.
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

    # Round off Stop time to next millisecond.
    mission_stop_time = parse(missionStop)

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
            if (message["data"]["participant_id"] == PL.pid):
                C.count1 += 1
                p1_msgs.append(message)
                #print ('Time :',message_time,'\t',message["data"]["mission_timer"],'\t', \
                #        message["topic"])
    #print ('Total P1 player messages: ', C.count1)
    C.resetCount1()

    #################### GENERATE SEQUENCE ##########################
    #NOTE: Can be merged with above section
    # All players start from staging area.

    # FLAGS to check before generating sequence.
    # These flags can be added to the player object.
    player_loc  = "hallway"
    transport   = "inactive"
    label = []
    label_class = []

    for msg in p1_msgs:
 
        # Extract mission time.
        #print (msg["topic"],msg["header"]["timestamp"])
        if ("mission_timer" in msg["data"]):
            if (msg["data"]["mission_timer"] == "Mission Timer not initialized."):
                continue
            else:
                #print (msg["data"]["mission_timer"])
                (mm,ss) = parse_mission_time(msg["data"]["mission_timer"])
        else:
            print(msg["topic"],"doesn't contain mission timer value.")
            continue
         
        # UPDATE player location.
        # Location message only updates player location. NO LABEL.
        if (msg["topic"] == "observations/events/player/location"):
            if "locations" in msg["data"]:
                if msg["data"]["locations"][0]["id"] in rooms:
                    player_loc = "room"
                elif msg["data"]["locations"][0]["id"] in hallways:
                    player_loc = "hallway"
                elif  msg["data"]["locations"][0]["id"] in treatmentAreas:
                    player_loc = "treatment"
            continue

        # Update if player is transporting victim or not.
        # Transport - ACTION
        # NOTE: There is a scenario where victim gets evacuated.
        if msg["topic"].lower() == "observations/events/player/victim_picked_up":
            if transport == "active":
                print ("Error: Player already carrying victim. Exiting sequence generation.")
                exit(1)
            else:
                transport = "active"
            continue

        if msg["topic"].lower() == "observations/events/player/victim_placed":
            if transport == "inactive":
                print ("Error: Player NOT carrying victim. Exiting sequence generation.")
                exit(1)
            else:
                transport = "inactive"
            continue

        # LABEL - State
        # Observations state indicates us about the players position and velocity
        if (msg["topic"].lower() == "observations/state"):
            # Player is stationary
            if msg["data"]["motion_x"] == 0 and msg["data"]["motion_z"] == 0:
                # Is the player performing a ROLE specific action
                label.append(('ST',mm,ss))
                label_class.append(0)
                continue
                #print ("ST,0,",msg["data"]["mission_timer"])

            # Player is moving
            else:  
                if transport == "active":
                    label.append(('TV',mm,ss))
                    label_class.append(4)
                    continue
                else:
                    if player_loc == "hallway" or player_loc =="treatment":
                        label.append(('NV',mm,ss))
                        label_class.append(1)
                        continue
                        #print ("NV,1,",msg["data"]["mission_timer"])
                    elif player_loc == "room":
                        label.append(('SR',mm,ss))
                        label_class.append(2)
                        continue

                    #print ("SR,2,",msg["data"]["mission_timer"])
                    # There is a location called UNKOWN, we will ignore for now.

        # Rubble destroyed - LABEL
        if (msg["topic"].lower() == "observations/events/player/rubble_destroyed"):
            label.append(('RA',mm,ss))
            label_class.append(8)
            continue
            print ('Rubble destroyed at :',msg["data"]["mission_timer"])
            # Open door label is 3

        # Door - LABEL
        if (msg["topic"].lower() == "observations/events/player/door"):
            if msg["data"]["open"] == True:
                label.append(('OD',mm,ss))
                label_class.append(3)
                continue
                #print ('Door opened at :',msg["data"]["mission_timer"])
                # Open door label is 3
                                
        # Marker placed. - LABEL
        if msg["topic"].lower() == "observations/events/player/marker_placed":
            label.append(('PM',mm,ss))
            label_class.append(5)
            continue

        # Marker removed. - LABEL
        if msg["topic"].lower() == "observations/events/player/marker_removed":
            label.append(('RM',mm,ss))
            label_class.append(6)
            continue

        # Item Selected and Tool Used.
        if msg["topic"].lower() == "observations/events/player/tool_used":
            label.append(('TU',mm,ss))
            label_class.append(7)
            continue

        if msg["topic"].lower() == "observations/events/player/itemequipped":
            label.append(('IE',mm,ss))
            label_class.append(9)
            continue

    # Coming here mean label sequence has been generated.
    # Label list contains label(str), mission(mm), and seconds(ss).
    
    # Write sequences to a file.
    out_fname = team+'_'+trial_num+'_'+PL.pid+'_'+PL.name+'.seq'
    out_file = os.path.join(out_dir,out_fname)
    print (out_fname)
    fw = open(out_file,'w')
    for lab in label:
        fw.write(lab[0]+'\n')
    fw.close()
    
    ####################### LOW RES ANNOTATION #######################
    print (len(label))
    minutes = 15
    seconds = 0

    # Here, we are going to create a dictionary.
    # Dictionary will have mission timer as the key and associated with they key
    # there will be a list of ordered labels.
    lab_sec = {}  # Empty dictionary
    l_count = 0
    for i in range(0,901):
        # Generate key
        k = str(minutes)+' : '+str(seconds)
        ll = []

        prev = ''   # Previous label.
        for lab in label:
            if prev == lab[0]:
                continue

            if lab[1] == minutes and lab[2] == seconds:
                ll.append(lab[0])
                l_count += 1
                prev = lab[0]
        lab_sec[k] = ll

        # Towards the end, update timer
        if seconds == 0:
            seconds = 59
            minutes -= 1
        else:
            seconds -= 1
        #if index > 10:
        #    break
        #print ('Mission time is : ',minutes,':',seconds)

    print ('Total labels: ',l_count)
    # Write sequences to a file.
    out_fname = team+'_'+trial_num+'_'+PL.pid+'_'+PL.name+'_1s.seq'
    out_file  = os.path.join(out_dir,out_fname)
    print (out_fname)
    fw = open(out_file,'w')
    for v in lab_sec.values():
        # v is a list of labels.
        for symbol in v:
            fw.write(symbol+'\n')
    fw.close()
    
def parse_mission_time (mission_time):
    temp = mission_time.split(':')
    return int(temp[0]),int(temp[1])

main()
