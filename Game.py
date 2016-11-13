#from code_and_map import *
from DecodeReplay import *
from GenMap import *
from DynamicElements import *
from Players import *
import pyglet

import sys, os, traceback, string, time, json, random


class Game:

    def __init__(self, filepath, w, h):
        self.data = {}
        replay = DecodeReplay(filepath)
        self.data["window"] = w, h
        self.data["replay"] = replay.data
        self.data["map"] = GenMap(replay.data)
        self.data["dynamic"] = DynamicElements(replay.data)
        self.data["players"] = Players(replay.data)
        h, w = self.data["map"].data["height"], self.data["map"].data["width"]
        self.data["height"], self.data["width"] = h, w
        self.data["follow"] = False
        self.data["end"] = float(replay.data["gameEndsAt"][0])/1000
        self.ended = False

    def _time_diff(self):
        utc = time.gmtime()
        utc_stamp = time.mktime(utc)
        cur_time = time.time()
        self.data["time difference"] = int(round((cur_time - utc_stamp) / 60))
        
    def _finalfix(self, min, sec):
        if min > 12:
            if min % 60 > 12:
                min += 12
            min %= 60
        elif min < 0:
            min += 60
        min = str(min)
        sec_str = ""
        if len(str(sec)) == 1:
            sec_str = "0"
        sec_str += str(sec)
        return min, sec_str

    def _times(self):
        self._time_diff()
        #"2016-02-09T17:05:22.462Z"
        clock = self.data["replay"]["clock"]
        self.data["times"] = []
        for i in clock:
            if type(i) != int:
                year = int(i[0:4])
                month = int(i[5:7])
                day = int(i[8:10])
                hour = int(i[11:13])
                minute = int(i[14:16])
                second = int(i[17:19])
#               print(hour, minute, second, "   "),
                micro = int(i[20:23]) *1000
                dt = datetime.datetime(year, month, day, hour, minute, second, micro)
                t_stamp = time.mktime(dt.timetuple())
                time_l = self.data["end"] - t_stamp
                sec = int(time_l % 60)
                min = int(time_l / 60)
                #min = min - self.data["time difference"]
                min, sec = self._finalfix(min, sec)
                self.data["times"].append(min + ":" + sec)
            else:
                self.data["times"].append("00:00")
        text = Text(self.data["times"][0])
        text.Modify("color", (255, 255, 255))
        text.Modify("size", 50)
        text.Modify("outline", (0, 0, 0))
        text.data["center"] = True
        w, h = self.data["window"]
        text.Modify("coords", (w/2, h - 50))
        self.data["clock"] = text

    #deprecated
    def _surfaces(self):
        self.surfaces = {}
        self.rsurf = {}
        h, w = self.data["height"], self.data["width"]
        self.surfaces["map"] = Surface(w, h)
        #self.surfaces["map"].Modify("transparent", (63, 213, 212))
        self.surfaces["dynamic"] = Surface(w, h)
        self.surfaces["players"] = Surface(w, h)
        self.rsurf["map"] = self.surfaces["map"].data["surface"]
        self.rsurf["players"] = self.surfaces["players"].data["surface"]
        self.rsurf["dynamic"] = self.surfaces["dynamic"].data["surface"]

    def Generate(self, screen):
        #self._surfaces()
        self._times()
        self.data["map"].RenderMap(self.rsurf["map"])
        #self.surfaces["map"].Finalize()
        #self.surfaces["map"].FinalizeAlpha()
        #self.surfaces["map"].AlphaBlit(screen)
        self.data["frame"] = 0

    def GetMe(self):
        players = self.data["players"].players
        for i in players:
            if players[i]["me"] == "me":
                return i

    def Follow(self, player, width, height):
        self.data["follow"] = player
        self.data["win height"] = height
        self.data["win width"] = width

    def _position(self):
        h, w = self.data["win height"], self.data["win width"]
        frame = self.data["frame"]
        follow = self.data["follow"]
        x = self.data["players"].players[follow]["x"][frame]
        y = self.data["players"].players[follow]["y"][frame]
        self.data["rel pos"] = [-x + w/2, -y + h/2]

    def _check_end(self, time_l):
        frame = self.data["frame"]
        score = self.data["replay"]["score"][frame]
        ended = False
        players = self.data["players"].players
        if type(score) != int:
            for i in score:
                if score[i] == 3:
                    ended = True
                    for j in players:
                        if players[j]["x"][frame] != \
                        players[j]["x"][frame + 1]:
                            ended = False
        if ended:
            self.ended = time_l


    def NewFrame(self, screen):
        if self.data["frame"] == 0:
            self.ended = False
        self.data["rel pos"] = None
        if self.data["follow"]:
            self._position()
            self.surfaces["map"].Modify("coords", self.data["rel pos"])
        self.surfaces["map"].AlphaBlit(screen)
        self.data["dynamic"].NewFrame(screen, self.data["rel pos"])
        self.data["players"].NewFrame(screen, self.data["rel pos"])
        self.data["frame"] = self.data["players"].data["frame"]
        time_l = self.data["times"][self.data["frame"]]
        w, h = self.data["window"]
        self.data["clock"].Modify("coords", (w/2, h - 50))
        if not self.ended:
            self.data["clock"].Modify("string", time_l)
            self._check_end(time_l)
        else:
            self.data["clock"].Modify("string", self.ended)
        self.data["clock"].Blit(screen)

    def __del__(self):
        self = None

def main():
    backGr = (0, 0, 0)
    filen = sys.argv[1]
    fullpath = filen
    w, h = 1300, 800
    win = Window("Map Preview", w, h)
    win.Modify("background", backGr)
    screen = win.Get("screen")
    ngame = Game(fullpath, w, h)
    ngame.Generate(screen)
    foc_player = ngame.GetMe()
    ngame.Follow(foc_player, w, h)
    win.Update()
    old_time = time.time()
    fps_o = Text("0")
    d_time = 0.01666666
#    d_time = 0
    fps_time = time.time()
    frames = 0
    while True:
        new_time = time.time()
        if new_time - old_time >= d_time:
            win.Event()
            event = win.Get("event")
            if event == "quit" or event == "q":
                win.Quit()
            win.Blit()
            ngame.NewFrame(screen)
            fps_o.Blit(screen)
            win.Update()
            #print(new_time - old_time)
            old_time = new_time
            frames += 1
        if new_time - fps_time >= 1.0:
            fps_o.Modify("string", str(frames))
            frames = 0
            fps_time = time.time()






if __name__ == "__main__":
    main()

