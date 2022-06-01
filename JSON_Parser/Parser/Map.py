import json
import os
import pickle
from typing import Tuple, Set

import numpy as np


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


class Map:
    WALL = 1
    DOOR = 2

    def __init__(self):
        self.metadata = {}
        self.grid = np.array([])

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        mapPackage = {
            "metadata": self.metadata,
            "grid": self.grid
        }

        with open(filepath, "wb") as f:
            pickle.dump(mapPackage, f)

    def load(self, filepath: str):
        with open(filepath, "rb") as f:
            mapPackage = pickle.load(f)

        self.metadata = mapPackage["metadata"]
        self.grid = mapPackage["grid"]

    def parse(self, jsonMap: json):
        wallBlocks, doorBlocks = self._getStaticBlocks(jsonMap)
        self._fillMetadata(wallBlocks)
        self._fillGrid(wallBlocks, doorBlocks)

    def _fillMetadata(self, wallBlocks: Set[Block]):
        # Get map bounds and add to the metadata file
        minX = None
        minY = None
        maxX = None
        maxY = None
        for block in wallBlocks:
            minX = block.x if minX is None else min(minX, block.x)
            minY = block.y if minY is None else min(minY, block.y)
            maxX = block.x if maxX is None else max(maxX, block.x)
            maxY = block.y if maxY is None else max(maxY, block.y)
        self.metadata["min_x"] = minX
        self.metadata["min_y"] = minY
        self.metadata["max_x"] = maxX
        self.metadata["max_y"] = maxY

    def _fillGrid(self, wallBlocks: Set[Block], doorBlocks: Set[Block]):
        width = self.metadata["max_x"] - self.metadata["min_x"] + 1
        height = self.metadata["max_y"] - self.metadata["min_y"] + 1
        self.grid = np.zeros((height, width), dtype=np.int8)

        for block in wallBlocks:
            self.grid[block.y - self.metadata["min_y"]][block.x - self.metadata["min_x"]] = Map.WALL

        for block in doorBlocks:
            self.grid[block.y - self.metadata["min_y"]][block.x - self.metadata["min_x"]] = Map.DOOR

    def _getStaticBlocks(self, jsonMap: json) -> Tuple[Set[Block], Set[Block]]:
        rooms = {}
        roomParts = {}
        roomBlocks = set()
        for location in jsonMap["locations"]:
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

        # For each room that has parts, compute the blocks that define the contour of the room
        for _, room in rooms.items():
            if "parts" in room:
                emptyBlocks = set()
                wallBlocks = set()
                for part_id in room["parts"]:
                    x1 = roomParts[part_id]["bounds"]["x1"]
                    y1 = roomParts[part_id]["bounds"]["y1"]
                    x2 = roomParts[part_id]["bounds"]["x2"]
                    y2 = roomParts[part_id]["bounds"]["y2"]

                    for x in range(x1, x2):
                        for y in range(y1, y2):
                            emptyBlocks.add(Block(x, y))

                    for x in range(x1 - 1, x2 + 1, 1):
                        wallBlocks.add(Block(x, y1 - 1))
                        wallBlocks.add(Block(x, y2))
                    for y in range(y1 - 1, y2 + 1, 1):
                        wallBlocks.add(Block(x1 - 1, y))
                        wallBlocks.add(Block(x2, y))

                roomBlocks = roomBlocks.union(wallBlocks.difference(emptyBlocks))

        # Add connections to the openings
        doorBlocks = set()
        openingBlocks = set()
        for location in jsonMap["connections"]:
            coordinates = location["bounds"]["coordinates"]
            x1 = coordinates[0]["x"]
            y1 = coordinates[0]["z"]
            x2 = coordinates[1]["x"]
            y2 = coordinates[1]["z"]

            if "door" in location["type"]:
                for x in range(x1, x2):
                    for y in range(y1, y2):
                        doorBlocks.add(Block(x, y))
            else:
                for x in range(x1, x2):
                    for y in range(y1, y2):
                        openingBlocks.add(Block(x, y))

        roomBlocks = roomBlocks.difference(openingBlocks)

        return roomBlocks, doorBlocks
