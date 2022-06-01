"""
Defining a series of static methods
"""
from typing import Any, Dict, List, Set, TextIO
import os
import json
from dateutil.parser import parse
import numpy as np
from Common.Constants import Constants

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

def getRoleFromStringType(stringType: str) -> Constants.Role:
    role = None
    if "transport" in stringType:
        role = Constants.Role.TRANSPORTER
    elif "engineering" in stringType:
        role = Constants.Role.ENGINEER
    elif "medical" in stringType:
        role = Constants.Role.MEDIC

    return role

def isMessageOf(message: json, type: str, subType: str):
    return message["header"]["message_type"].lower() == type.lower() and message["msg"][
        "sub_type"].lower() == subType.lower()

