from typing import Any, Dict, List, Set, TextIO
import os
import json
from dateutil.parser import parse
import numpy as np
import pickle

from Parser.Map import Map
from Common.Constants import Constants


class ChatMessage:
    """
    This class represents a chat message in the trial. It encapsulates information about the sender, the message and
    the addressee. It is used so we can create a set of messages to get rid of duplicate ones.
    """

    def __init__(self, sender: str, addressee: str, color: str, text: str):
        self.sender = sender
        self.addressee = addressee
        self.color = color
        self.text = text

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                getattr(other, 'sender', None) == self.sender and
                getattr(other, 'addressee', None) == self.addressee and
                getattr(other, 'text', None) == self.text)

    def __hash__(self):
        return hash(f"{self.sender}#{self.addressee}#{self.text}")


class Position:

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                getattr(other, 'x', None) == self.x and
                getattr(other, 'y', None) == self.y)

    def __hash__(self):
        return hash(f"{self.x}#{self.y}")

    def __repr__(self):
        return f"{self.x}#{self.y}"


class Marker:
    def __init__(self, markerType: Constants.MarkerType, x: float, y: float):
        super().__init__()
        self.markerType = markerType
        self.position = Position(x, y)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                getattr(other, 'markerType', None) == self.markerType and
                getattr(other, 'position', None) == self.position)

    def __hash__(self):
        return hash(f"{self.markerType}#{self.position}")

    def __repr__(self):
        return f"{self.markerType}#{self.position}"


class Victim:
    def __init__(self, victimType: Constants.VictimType, x: float, y: float):
        super().__init__()
        self.victimType = victimType
        self.position = Position(x, y)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                getattr(other, 'victimType', None) == self.victimType and
                getattr(other, 'position', None) == self.position)

    def __hash__(self):
        return hash(f"{self.victimType}#{self.position}")

    def __repr__(self):
        return f"{self.victimType}#{self.position}"


class Trial:

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
        "observations/events/player/victim_evacuated",
        "observations/events/player/signal"
#        "agent/asr/final"
    ]

    MAP_TOPIC = "ground_truth/semantic_map/initialized"
    VICTIM_LIST_TOPIC = "ground_truth/mission/victims_list"
    RUBBLE_LIST_TOPIC = "ground_truth/mission/blockages_list"
    THREAT_PLATE_LIST_TOPIC = "ground_truth/mission/threatsign_list"
    VICTIM_SIGNAL_PLATE_LIST_TOPIC = "ground_truth/mission/freezeblock_list"

    def __init__(self, timeSteps: int = 900):
        self.timeSteps = timeSteps

        # Ground truth
        self.map = None
        self.victimList = []
        self.rubbleList = []
        self.threatPlateList = []
        self.victimSignalPlateList = []

        self.metadata = {}
        self.scores = np.array([])
        self.placedMarkers: List[Set[Marker]] = []
        self.removedMarkers: List[Set[Marker]] = []
        self.activeBlackout: List[bool] = []
        self.savedVictims: List[Set[Victim]] = []
        self.pickedUpVictims: List[Set[Victim]] = []
        self.placedVictims: List[Set[Victim]] = []

        # List of rubbles added or removed in each position per time step
        self.rubbleCounts: List[Dict[Position, int]] = []

        # Each list contains 3 entries. One per player. For each player there will be #timeSteps entries. And for each
        # of these, there might be multiple values (e.g. chat messages)
        self.playersPositions: List[List[List[Position]]] = []
        self.playersYaws: List[List[float]] = []
        self.chatMessages: List[List[Set[ChatMessage]]] = []
        self.speechTranscriptions: List[List[List[str]]] = []
        self.playersActions: List[List[Constants.Action]] = []
        self.playersEquippedItems: List[List[Constants.EquippedItem]] = []

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        trialPackage = {
            "map": self.map,
            "metadata": self.metadata,
            "scores": self.scores,
            "players_positions": self.playersPositions,
            "players_yaws": self.playersYaws,
            "placed_markers": self.placedMarkers,
            "removed_markers": self.removedMarkers,
            "chat_messages": self.chatMessages,
            "players_actions": self.playersActions,
            "rubble_counts": self.rubbleCounts,
            "active_blackout": self.activeBlackout,
            "saved_victims": self.savedVictims,
            "picked_up_victims": self.pickedUpVictims,
            "placed_victims": self.placedVictims,
            "players_equipped_items": self.playersEquippedItems,
            "victim_list": self.victimList,
            "rubble_list": self.rubbleList,
            "threat_plate_list": self.threatPlateList,
            "victim_signal_plate_list": self.victimSignalPlateList,
            "speech_transcriptions": self.speechTranscriptions
        }

        with open(filepath, "wb") as f:
            pickle.dump(trialPackage, f)

    def load(self, filepath: str):
        with open(filepath, "rb") as f:
            trialPackage = pickle.load(f)

        self.map = trialPackage["map"]
        self.metadata = trialPackage["metadata"]
        self.scores = trialPackage["scores"]
        self.playersPositions = trialPackage["players_positions"]
        self.playersYaws = trialPackage["players_yaws"]
        self.placedMarkers = trialPackage["placed_markers"]
        self.removedMarkers = trialPackage["removed_markers"]
        self.chatMessages = trialPackage["chat_messages"]
        self.playersActions = trialPackage["players_actions"]
        self.rubbleCounts = trialPackage["rubble_counts"]
        self.activeBlackout = trialPackage["active_blackout"]
        self.savedVictims = trialPackage["saved_victims"]
        self.pickedUpVictims = trialPackage["picked_up_victims"]
        self.placedVictims = trialPackage["placed_victims"]
        self.playersEquippedItems = trialPackage["players_equipped_items"]
        self.victimList = trialPackage["victim_list"]
        self.rubbleList = trialPackage["rubble_list"]
        self.threatPlateList = trialPackage["threat_plate_list"]
        self.victimSignalPlateList = trialPackage["victim_signal_plate_list"]
        self.speechTranscriptions = trialPackage["speech_transcriptions"]

    def parse(self, trialMessagesFile: TextIO):
        messages = self._parseGroundTruthAndSortRemainingMessages(trialMessagesFile)

        if len(messages) == 0:
            return

        nextTimeStep = 0
        missionStarted = False
        playerIdToColor = {}
        self.metadata = {}

        # Cleaning global variables
        self.scores = np.zeros(self.timeSteps, dtype=np.int32)
        self.placedMarkers = []
        self.removedMarkers = []
        self.rubbleCounts = []
        self.playersPositions = [[] for _ in range(Constants.NUM_ROLES)]
        self.playersYaws = [[] for _ in range(Constants.NUM_ROLES)]
        self.chatMessages = [[] for _ in range(Constants.NUM_ROLES)]
        self.speechTranscriptions = [[] for _ in range(Constants.NUM_ROLES)]
        self.playersActions = [[] for _ in range(Constants.NUM_ROLES)]
        self.activeBlackout = []
        self.savedVictims = []
        self.playersEquippedItems = [[] for _ in range(Constants.NUM_ROLES)]

        # These variables contain valid values per time step.
        # Some will have their value reset in the end of a time step.
        currentScore = 0
        currentPlayersPositions: List[List[Position]] = [[] for _ in range(Constants.NUM_ROLES)]
        currentPlayersYaws: List[float] = [0 for _ in range(Constants.NUM_ROLES)]
        currentPlacedMarkers = set()
        currentRemovedMarkers = set()
        currentChatMessages: List[Set[ChatMessage]] = [set() for _ in range(Constants.NUM_ROLES)]
        currentSpeechTranscriptions: List[List[str]] = [[] for _ in range(Constants.NUM_ROLES)]
        currentPlayersActions = [Constants.Action.NONE for _ in range(Constants.NUM_ROLES)]
        currentRubbleCounts = {}
        collapsedRubbleCounts: Set[Position] = set()
        currentActiveBlackout = False
        currentSavedVictims = set()
        currentPickedUpVictims = set()
        currentPlacedVictims = set()
        currentPlayersEquippedItems = [Constants.EquippedItem.HAMMER for _ in range(Constants.NUM_ROLES)]
        for message in messages:
            if Trial._isMessageOf(message, "event", "Event:MissionState"):
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
            elif Trial._isMessageOf(message, "event", "Event:RoleSelected"):
                role = Trial._getRoleFromStringType(message["data"]["new_role"].lower())
                playerId = message["data"]["participant_id"]
                playerColor = playerIdToColor[playerId]

                if playerColor == "red":
                    self.metadata["red_role"] = role
                elif playerColor == "green":
                    self.metadata["green_role"] = role
                else:
                    self.metadata["blue_role"] = role
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

            if missionStarted:
                if Trial._isMessageOf(message, "observation", "Event:Scoreboard"):
                    currentScore = message["data"]["scoreboard"]["TeamScore"]

                elif Trial._isMessageOf(message, "event", "Event:MarkerPlaced"):
                    # We don't care about who placed it for the moment
                    markerType = Trial._getMarkerTypeFromStringType(message["data"]["type"])
                    x = message["data"]["marker_x"] - self.map.metadata["min_x"]
                    y = message["data"]["marker_z"] - self.map.metadata["min_y"]

                    marker = Marker(markerType, x, y)
                    if marker in currentRemovedMarkers:
                        # It was added previously, and added to be removed in this time step. We just need to remove it
                        # from the list of removals.
                        currentRemovedMarkers.discard(marker)
                    else:
                        # It was never added. We include it in the list of markers to be created
                        currentPlacedMarkers.add(marker)

                elif Trial._isMessageOf(message, "event", "Event:MarkerRemoved"):
                    markerType = Trial._getMarkerTypeFromStringType(message["data"]["type"])
                    x = message["data"]["marker_x"] - self.map.metadata["min_x"]
                    y = message["data"]["marker_z"] - self.map.metadata["min_y"]

                    marker = Marker(markerType, x, y)
                    if marker in currentPlacedMarkers:
                        # It was placed and removed within a time step.
                        # Just remove from the list of markers to be added.
                        currentPlacedMarkers.discard(marker)
                    else:
                        # It was added previously, so we must add it to the list of removals of the current time step
                        currentRemovedMarkers.add(marker)

                elif Trial._isMessageOf(message, "chat", "Event:Chat"):
                    sender = message["data"]["sender"]
                    jsonText = json.loads(message["data"]["text"])
                    for playerId in message["data"]["addressees"]:
                        playerColor = playerIdToColor[playerId]
                        chatMessage = ChatMessage(sender, playerId, jsonText["color"], jsonText["text"])
                        currentChatMessages[Constants.PLAYER_COLOR_MAP[playerColor].value].add(chatMessage)

                elif Trial._isMessageOf(message, "event", "Event:VictimPickedUp"):
                    playerId = message["data"]["participant_id"]
                    playerColor = playerIdToColor[playerId]
                    currentPlayersActions[
                        Constants.PLAYER_COLOR_MAP[playerColor].value] = Constants.Action.CARRYING_VICTIM

                    x = message["data"]["victim_x"] - self.map.metadata["min_x"]
                    y = message["data"]["victim_z"] - self.map.metadata["min_y"]
                    victimType = self._getVictimTypeFromStringType(message["data"]["type"])
                    victim = Victim(victimType, x, y)

                    if victim in currentPlacedVictims:
                        # Victim was picked up again before the within a time step. Just remove it from the list of
                        # victims that were placed
                        currentPlacedVictims.remove(victim)
                    else:
                        currentPickedUpVictims.add(victim)

                elif Trial._isMessageOf(message, "event", "Event:VictimPlaced"):
                    playerId = message["data"]["participant_id"]
                    playerColor = playerIdToColor[playerId]
                    currentPlayersActions[
                        Constants.PLAYER_COLOR_MAP[playerColor].value] = Constants.Action.NONE

                    x = message["data"]["victim_x"] - self.map.metadata["min_x"]
                    y = message["data"]["victim_z"] - self.map.metadata["min_y"]
                    victimType = self._getVictimTypeFromStringType(message["data"]["type"])
                    victim = Victim(victimType, x, y)

                    if victim in currentPickedUpVictims:
                        # Victim was picked up and placed immediately in the same location, just never pick it up.
                        currentPickedUpVictims.remove(victim)
                    else:
                        currentPlacedVictims.add(victim)

                elif Trial._isMessageOf(message, "event", "Event:Triage"):
                    playerId = message["data"]["participant_id"]
                    playerColor = playerIdToColor[playerId]

                    if message["data"]["triage_state"].lower() == "in_progress":
                        currentPlayersActions[
                            Constants.PLAYER_COLOR_MAP[playerColor].value] = Constants.Action.HEALING_VICTIM
                    else:
                        currentPlayersActions[
                            Constants.PLAYER_COLOR_MAP[playerColor].value] = Constants.Action.NONE
                        if message["data"]["triage_state"].lower() == "successful":
                            x = message["data"]["victim_x"] - self.map.metadata["min_x"]
                            y = message["data"]["victim_z"] - self.map.metadata["min_y"]
                            victimType = self._getVictimTypeFromStringType(message["data"]["type"])
                            currentSavedVictims.add(Victim(victimType, x, y))

                elif Trial._isMessageOf(message, "event", "Event:ToolUsed"):
                    tool = message["data"]["tool_type"].lower()
                    target_block = message["data"]["target_block_type"].lower()
                    if tool == "hammer" and target_block == "minecraft:gravel":
                        playerId = message["data"]["participant_id"]
                        playerColor = playerIdToColor[playerId]
                        currentPlayersActions[
                            Constants.PLAYER_COLOR_MAP[playerColor].value] = Constants.Action.DESTROYING_RUBBLE

                elif Trial._isMessageOf(message, "event", "Event:RubbleDestroyed"):
                    x = message["data"]["rubble_x"] - self.map.metadata["min_x"]
                    y = message["data"]["rubble_z"] - self.map.metadata["min_y"]
                    position = Position(x, y)

                    if position in currentRubbleCounts:
                        currentRubbleCounts[position] -= 1
                    else:
                        currentRubbleCounts[position] = -1

                    collapsedRubbleCounts.discard(position)

                elif Trial._isMessageOf(message, "event", "Event:Perturbation"):
                    if message["data"]["type"].lower() == "blackout":
                        currentActiveBlackout = message["data"]["state"].lower() == "start"

                elif Trial._isMessageOf(message, "event", "Event:RubbleCollapse"):
                    # How many are stacked on top of each other
                    counts = abs(message["data"]["toBlock_y"] - message["data"]["fromBlock_y"]) + 1

                    for x in range(message["data"]["fromBlock_x"], message["data"]["toBlock_x"] + 1):
                        for y in range(message["data"]["fromBlock_z"], message["data"]["toBlock_z"] + 1):
                            position = Position(x - self.map.metadata["min_x"], y - self.map.metadata["min_y"])
                            if position not in collapsedRubbleCounts:
                                currentRubbleCounts[position] = counts
                                collapsedRubbleCounts.add(position)

                elif Trial._isMessageOf(message, "observation", "asr:transcription"):
                    playerId = message["data"]["participant_id"]
                    playerColor = playerIdToColor[playerId]
                    text = message["data"]["text"].strip()
                    currentSpeechTranscriptions[Constants.PLAYER_COLOR_MAP[playerColor].value].append(text)

                elif Trial._isMessageOf(message, "observation", "State"):
                    # Collect observations for the current time step
                    missionTimer = message["data"]["mission_timer"]
                    elapsedSeconds = self._missionTimerToElapsedSeconds(missionTimer)

                    if elapsedSeconds >= nextTimeStep:
                        for t in range(nextTimeStep, elapsedSeconds + 1):
                            self.scores[t] = currentScore
                            self.placedMarkers.append(currentPlacedMarkers.copy())
                            self.removedMarkers.append(currentRemovedMarkers.copy())
                            for playerIdx, positions in enumerate(self.playersPositions):
                                if len(currentPlayersPositions[playerIdx]) == 0:
                                    positions.append([self.playersPositions[playerIdx][-1][-1]])
                                else:
                                    positions.append(currentPlayersPositions[playerIdx].copy())
                                currentPlayersPositions[playerIdx].clear()
                            for playerIdx, yaws in enumerate(self.playersYaws):
                                yaws.append(currentPlayersYaws[playerIdx])
                            for playerIdx, messages in enumerate(self.chatMessages):
                                messages.append(currentChatMessages[playerIdx].copy())
                                currentChatMessages[playerIdx].clear()
                            for playerIdx, texts in enumerate(self.speechTranscriptions):
                                texts.append(currentSpeechTranscriptions[playerIdx].copy())
                                currentSpeechTranscriptions[playerIdx].clear()
                            for playerIdx, actions in enumerate(self.playersActions):
                                actions.append(currentPlayersActions[playerIdx])
                                if currentPlayersActions[playerIdx] != Constants.Action.CARRYING_VICTIM:
                                    # If the players are carrying victims. The action only stops after they place them.
                                    currentPlayersActions[playerIdx] = Constants.Action.NONE
                            self.rubbleCounts.append(currentRubbleCounts.copy())
                            self.activeBlackout.append(currentActiveBlackout)
                            self.savedVictims.append(currentSavedVictims.copy())
                            self.pickedUpVictims.append(currentPickedUpVictims.copy())
                            self.placedVictims.append(currentPlacedVictims.copy())
                            for playerIdx, equippedItems in enumerate(self.playersEquippedItems):
                                equippedItems.append(currentPlayersEquippedItems[playerIdx])

                        nextTimeStep = elapsedSeconds + 1

                        currentPlacedMarkers.clear()
                        currentRemovedMarkers.clear()
                        currentRubbleCounts.clear()
                        currentSavedVictims.clear()
                        currentPickedUpVictims.clear()
                        currentPlacedVictims.clear()

                    if nextTimeStep == self.timeSteps:
                        break

    def _parseGroundTruthAndSortRemainingMessages(self, trialMessagesFile: TextIO) -> List[Any]:
        messages = []
        groundTruthMessagesMap: Dict[str, Any] = {}

        for line in trialMessagesFile:
            jsonMessage = None
            try:
                jsonMessage = json.loads(line)
            except:
                print(f"Bad json line of len: {len(line)}, {line}")

            if jsonMessage is not None:
                if "topic" in jsonMessage:
                    if jsonMessage["topic"] == Trial.MAP_TOPIC:
                        groundTruthMessagesMap["map"] = jsonMessage
                    elif jsonMessage["topic"] == Trial.VICTIM_LIST_TOPIC:
                        groundTruthMessagesMap["victim_list"] = jsonMessage
                    if jsonMessage["topic"] == Trial.RUBBLE_LIST_TOPIC:
                        groundTruthMessagesMap["rubble_list"] = jsonMessage
                    if jsonMessage["topic"] == Trial.THREAT_PLATE_LIST_TOPIC:
                        groundTruthMessagesMap["threat_plate_list"] = jsonMessage
                    if jsonMessage["topic"] == Trial.VICTIM_SIGNAL_PLATE_LIST_TOPIC:
                        groundTruthMessagesMap["victim_signal_plate_list"] = jsonMessage
                    elif jsonMessage["topic"] in Trial.USED_TOPICS:
                        messages.append(jsonMessage)

        self._parseGroundTruthMessages(groundTruthMessagesMap)

        sorted_messages = sorted(
            messages, key=lambda x: parse(x["header"]["timestamp"])
        )

        return sorted_messages

    def _parseGroundTruthMessages(self, groundTruthMessagesMap: Dict[str, Any]):
        self._parseMap(groundTruthMessagesMap["map"])
        self._parseVictimList(groundTruthMessagesMap["victim_list"])
        self._parseRubbleList(groundTruthMessagesMap["rubble_list"])
        self._parseThreatPlateList(groundTruthMessagesMap["threat_plate_list"])
        self._parseVictimSignalPlateList(groundTruthMessagesMap["victim_signal_plate_list"])

    def _parseMap(self, message: Dict[str, Any]):
        self.map = Map()
        self.map.parse(message["data"]["semantic_map"])

    def _parseVictimList(self, message: Dict[str, Any]):
        for victimInfo in message["data"]["mission_victim_list"]:
            x = victimInfo["x"] - self.map.metadata["min_x"]
            y = victimInfo["z"] - self.map.metadata["min_y"]
            victimType = Trial._getVictimTypeFromBlockStringType(victimInfo["block_type"])
            self.victimList.append(Victim(victimType, x, y))

    def _parseRubbleList(self, message: Dict[str, Any]):
        for blockInfo in message["data"]["mission_blockage_list"]:
            x = blockInfo["x"] - self.map.metadata["min_x"]
            y = blockInfo["z"] - self.map.metadata["min_y"]
            self.rubbleList.append(Position(x, y))

    def _parseThreatPlateList(self, message: Dict[str, Any]):
        for blockInfo in message["data"]["mission_threatsign_list"]:
            x = blockInfo["x"] - self.map.metadata["min_x"]
            y = blockInfo["z"] - self.map.metadata["min_y"]
            self.threatPlateList.append(Position(x, y))

    def _parseVictimSignalPlateList(self, message: Dict[str, Any]):
        pass

    def _missionTimerToElapsedSeconds(self, timer: str):
        if timer.find(":") >= 0:
            minutes = int(timer[:timer.find(":")])
            seconds = int(timer[timer.find(":") + 1:])
            return self.timeSteps - (seconds + minutes * 60)

        return -1

    @staticmethod
    def _isMessageOf(message: json, type: str, subType: str):
        return message["header"]["message_type"].lower() == type.lower() and message["msg"][
            "sub_type"].lower() == subType.lower()

    @staticmethod
    def _getRoleFromStringType(stringType: str) -> Constants.Role:
        role = None
        if "transport" in stringType:
            role = Constants.Role.TRANSPORTER
        elif "engineering" in stringType:
            role = Constants.Role.ENGINEER
        elif "medical" in stringType:
            role = Constants.Role.MEDIC

        return role

    @staticmethod
    def _getMarkerTypeFromStringType(stringType: str) -> Constants.MarkerType:
        markerType = None
        if "novictim" in stringType:
            markerType = Constants.MarkerType.NO_VICTIM
        elif "abrasion" in stringType:
            markerType = Constants.MarkerType.VICTIM_A
        elif "bonedamage" in stringType:
            markerType = Constants.MarkerType.VICTIM_B
        elif "regularvictim" in stringType:
            markerType = Constants.MarkerType.REGULAR_VICTIM
        elif "criticalvictim" in stringType:
            markerType = Constants.MarkerType.CRITICAL_VICTIM
        elif "threat" in stringType:
            markerType = Constants.MarkerType.THREAT_ROOM
        elif "rubble" in stringType:
            markerType = Constants.MarkerType.RUBBLE
        elif "sos" in stringType:
            markerType = Constants.MarkerType.SOS

        return markerType

    @staticmethod
    def _getVictimTypeFromStringType(stringType: str) -> Constants.VictimType:
        victimType = None
        if "victim_a" in stringType:
            victimType = Constants.VictimType.A
        elif "victim_b" in stringType:
            victimType = Constants.VictimType.B
        elif "victim_c" in stringType:
            victimType = Constants.VictimType.CRITICAL
        if "victim_saved_a" in stringType:
            victimType = Constants.VictimType.SAFE_A
        elif "victim_saved_b" in stringType:
            victimType = Constants.VictimType.SAFE_B
        elif "victim_saved_c" in stringType:
            victimType = Constants.VictimType.SAFE_CRITICAL

        return victimType

    @staticmethod
    def _getItemTypeFromStringType(stringType: str) -> Constants.EquippedItem:
        itemType = None
        if "hammer" in stringType:
            itemType = Constants.EquippedItem.HAMMER
        elif "medical_kit" in stringType:
            itemType = Constants.EquippedItem.MEDICAL_KIT
        elif "stretcher" in stringType:
            itemType = Constants.EquippedItem.STRETCHER
        elif "novictim" in stringType:
            itemType = Constants.EquippedItem.NO_VICTIM
        elif "abrasion" in stringType:
            itemType = Constants.EquippedItem.VICTIM_A
        elif "bonedamage" in stringType:
            itemType = Constants.EquippedItem.VICTIM_B
        elif "regularvictim" in stringType:
            itemType = Constants.EquippedItem.REGULAR_VICTIM
        elif "criticalvictim" in stringType:
            itemType = Constants.EquippedItem.CRITICAL_VICTIM
        elif "threat" in stringType:
            itemType = Constants.EquippedItem.THREAT_ROOM
        elif "rubble" in stringType:
            itemType = Constants.EquippedItem.RUBBLE
        elif "sos" in stringType:
            itemType = Constants.EquippedItem.SOS

        return itemType

    @staticmethod
    def _getVictimTypeFromBlockStringType(stringType: str) -> Constants.VictimType:
        victimType = None
        if "victim_1" in stringType:
            victimType = Constants.VictimType.A
        elif "victim_1b" in stringType:
            victimType = Constants.VictimType.B
        elif "victim_proximity" in stringType:
            victimType = Constants.VictimType.CRITICAL

        return victimType
