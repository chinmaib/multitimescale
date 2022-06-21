from enum import Enum


class Constants:
    MIN_WINDOW_SIZE = QSize(1800, 1020)

    NUM_ROLES = 3

    class Role(Enum):
        MEDIC = 0
        ENGINEER = 1
        TRANSPORTER = 2

    class Player(Enum):
        RED = 0
        GREEN = 1
        BLUE = 2

    PLAYER_COLOR_MAP = {
        "red": Player.RED,
        "green": Player.GREEN,
        "blue": Player.BLUE,
    }

    class Action(Enum):
        NONE = -1
        CARRYING_VICTIM = 0
        HEALING_VICTIM = 1
        DESTROYING_RUBBLE = 2

    class Colors(Enum):
        RED_PLAYER = "#E30B21"
        GREEN_PLAYER = "#13D200"
        BLUE_PLAYER = "#0045FA"
        VICTIM_A = "#02B860"
        VICTIM_B = "#02B860"
        CRITICAL_VICTIM = "#FACC09"
        SAFE_VICTIM = "#0AB7FC"
        THREAT_ACTIVATION = "#8400EB"
        RUBBLE = "#808080"
        MARKER = "#DE87F0"
        INCONSISTENCY = "#FA8B03"
        DOOR = "#000000"
        APP_BACKGROUND = "#E8E0E7"
        SEARCH_FIELD_BACKGROUND = "#FF7DAF"

    # TODO - remove?
    class BlockType(Enum):
        RUBBLE = 0
        MARKER = 1
        VICTIM_A = 2
        VICTIM_B = 3
        CRITICAL_VICTIM = 4
        SAFE_VICTIM = 5

    class MarkerType(Enum):
        NO_VICTIM = 0
        VICTIM_A = 1
        VICTIM_B = 2
        REGULAR_VICTIM = 3
        CRITICAL_VICTIM = 4
        THREAT_ROOM = 5
        SOS = 6
        RUBBLE = 7

    class VictimType(Enum):
        A = 0
        B = 1
        CRITICAL = 2
        SAFE_A = 3
        SAFE_B = 4
        SAFE_CRITICAL = 5

    class EquippedItem(Enum):
        HAMMER = 0
        MEDICAL_KIT = 1
        STRETCHER = 2
        NO_VICTIM = 3
        VICTIM_A = 4
        VICTIM_B = 5
        REGULAR_VICTIM = 6
        CRITICAL_VICTIM = 7
        THREAT_ROOM = 8
        SOS = 9
        RUBBLE = 10

    class Font(Enum):
        TINY_REGULAR = QFont("Inconsolata", 11)
        SMALL_BOLD = QFont("Inconsolata", 14, QFont.Bold)
        SMALL_REGULAR = QFont("Inconsolata", 14)
        LARGE_BOLD = QFont("Inconsolata", 50, QFont.Bold)
        HUGE_BOLD = QFont("Inconsolata", 70, QFont.Bold)

    MARKER_TYPE_MAP = {
        MarkerType.NO_VICTIM: "O",
        MarkerType.VICTIM_A: "A",
        MarkerType.VICTIM_B: "B",
        MarkerType.REGULAR_VICTIM: "V",
        MarkerType.CRITICAL_VICTIM: "C",
        MarkerType.THREAT_ROOM: "T",
        MarkerType.SOS: "S",
        MarkerType.RUBBLE: "R",
    }





