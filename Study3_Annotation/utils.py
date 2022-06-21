"""
Defining a series of static methods
"""
from typing import Any, Dict, List, Set, TextIO
import os
import json
import numpy as np

USED_TOPICS = [
#   "trial",
#   "observations/events/mission",
    "observations/state",
    #"observations/events/scoreboard",
    #"observations/events/player/role_selected",
    "observations/events/player/marker_placed",
    #"minecraft/chat",
    "observations/events/player/triage",
    "observations/events/player/victim_picked_up",
    "observations/events/player/victim_placed",
    "observations/events/player/tool_used",
    "observations/events/player/marker_removed",
    "observations/events/player/rubble_destroyed",
    #"observations/events/mission/perturbation",
    #"observations/events/player/rubble_collapse",
    "observations/events/player/itemequipped",
    #"observations/events/server/victim_evacuated",
    "observations/events/player/signal",
    "observations/events/player/location",
    "observations/events/player/door"
    #   "agent/asr/final"
]
# May be the agent messages are not required for me.
# What about minecraft/chat

TRIAL_MSG = "trial"
MISSION_MSG = "observations/events/mission"
PLANNING_MSG = "observations/events/mission/planning"
MAP_TOPIC = "ground_truth/semantic_map/initialized"
VICTIM_LIST_TOPIC = "ground_truth/mission/victims_list"
RUBBLE_LIST_TOPIC = "ground_truth/mission/blockages_list"
THREAT_PLATE_LIST_TOPIC = "ground_truth/mission/threatsign_list"
VICTIM_SIGNAL_PLATE_LIST_TOPIC = "ground_truth/mission/freezeblock_list"

def isMessageOf(message: json, type: str, subType: str):
    return message["header"]["message_type"].lower() == type.lower() and message["msg"][
        "sub_type"].lower() == subType.lower()

