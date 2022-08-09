"""
Script: display_player_info.py
Author: Chinmaib

"""

import os
import sys
import json
# Adding parent folder to import search.
sys.path.append("..")

from utils import *

if len(sys.argv) != 2:
    print ('Usage: python3 display_player_info.py <filename.metadata>')
    exit(1)


def main():
    meta_fname  = sys.argv[1]
    data_dir    = '/home/chinmaib/tomcat/study3_data'
    meta_file_path = os.path.join(data_dir,meta_fname)
    meta_fd = open(meta_file_path,'r')
    
    messages = []
    trialMessage = []

    topics = set()
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

                if jsonMessage["topic"] == TRIAL_MSG:
                    trialMessage.append(jsonMessage)
                    break


    #################### EXTRACT PLAYER/TRIAL INFO ##########################
    # Player names, ID's, and matching colors.
    msg = trialMessage[0]
    # Client info field is a list of dictionary item with player information
    trial_name = msg["data"]["name"]
    trial_num  = msg["data"]["trial_number"]
    sub_info = msg["data"]["client_info"]

    # Client info is a list of player information.
    for i in range(0,3):        #3 players
        #print ('PID: ',sub_info[i]['participant_id'],'\tSign: ',sub_info[i]["callsign"], \
        #        '\tName:',sub_info[i]["playername"])

        print (sub_info[i]['participant_id'],',',sub_info[i]["callsign"],',', \
                sub_info[i]["playername"])
        #if sub_info[i]["callsign"] == "Red":
        #    P1 = Player(sub_info[i]["playername"],sub_info[i]["participant_id"], \
        #        sub_info[i]["callsign"])
        #    break

    # Close meta file.
    meta_fd.close()

main()

