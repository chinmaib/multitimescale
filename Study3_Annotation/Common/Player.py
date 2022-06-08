class Counter:
    """ 
    This class contains counters, one for each participant and one common one.

    """
    count1 = 0
    count2 = 0
    count3 = 0
    red_count = 0
    blue_count = 0
    green_count = 0
    
    def resetCount1(self):
        self.count1 = 0

    def resetCount2(self):
        self.count2 = 0

    def resetCount3(self):
        self.count3 = 0

    def resetAll(self):
        self.count1 = 0
        self.count2 = 0
        self.count3 = 0

class Player:
    """
    This class will define all the attributes a players posses in 
    the Minecraft search and resuce mission.
    """
    pid=''
    name=''
    color=''    #[Red, Blue, Green]
    # A list of coordinates. Which can be another class variable.
    # Where each coordinate contains x,y,z
    coordinates= []    
    events= []
    messages=[]
    tools = []

    def __init__(self,pname: str, player_id: str, callsign: str):
        self.pid   = player_id
        self.name  = pname
        self.color = callsign

    def __repr__(self):
        var = "Player ID:"+self.pid+"\nPlayer name:"+self.name+ \
        "\nPlayer sign:"+self.color+"\n"
        return var

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





















