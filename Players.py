from code_and_map import *
from DecodeReplay import *
from GenMap import *
from DynamicElements import *
from Outline import *

import pyglet

import sys, os, traceback, string, time, json, random, datetime

class Players:
    files = {}
    script_path = os.path.dirname(__file__)
    files["tiles"] = script_path + "/img/Tiles.png"
    files["flairs"] =script_path + "/img/Flair.png"
    functions = {"tiles" : tiles_map
                 }
    balls = ("blue ball", "red ball")
    flag = ("neutral flag", "red flag", "blue flag")

    def _gen_Tile_Objs(self):
        self.tiles = {}
        for i in self.balls:
            newtile = pyglet.image.load(self.files["tiles"])
            h = newtile.height
            rx, ry = self.functions["tiles"][i]
            subtile = newtile.get_region(x=rx, y=h-40 -ry, width=40, height=40)
            subtile.anchor_x = subtile.width/2
            subtile.anchor_y = subtile.height/2
            subtile = pyglet.sprite.Sprite(subtile, batch=self.batch)
            self.tiles[i] = subtile
        for i in self.flag:
            newtile = pyglet.image.load(self.files["tiles"])
            h = newtile.height
            rx, ry = self.functions["tiles"][i]
            subtile = newtile.get_region(x=rx, y=h-40 -ry, width=40, height=40)
            subtile = pyglet.sprite.Sprite(subtile, batch=self.batch)
            self.tiles[i] = subtile
        self.flairs = pyglet.image.load((self.files["flairs"]))


    def _gen_names(self):
        self.names = {}
        for i in self.players:
            name = self.players[i]["name"]
            text = Outlined(i, "Times New Roman", 10, 0, 0)
            self.names[i] = text

    def __init__(self, replay_data):
        self.t = 0
        self.data = {}
        self.data["frame"] = 0
        self.data["replay"] = replay_data
        self.data["width"] = len(replay_data["map"])
        self.data["height"] = len(replay_data["map"][0])
        n = 0
        self.players = {}
        self.batch = pyglet.graphics.Batch()
        for i in replay_data:
            if "player" in i:
                if True in replay_data[i]["draw"]:
                    self.players[i] = replay_data[i]
        self._gen_Tile_Objs()
        self._gen_names()


    def _angle(self, cur):
        frame = self.data["frame"]
        angle = cur["angle"][frame]
        if angle:
            angle = angle*360/(2*3.14)
        return angle

    def _drawplayer(self, p_data):
        x, y, draw, dead, team, name, angle = p_data[0:7]
        if draw and not dead and team:
            if angle:
                self.tiles[team].rotation = -angle
            self.tiles[team].x, self.tiles[team].y = x, y
            self.tiles[team].draw()

    def _drawname(self, p_data, player):
        x, y, draw, dead, team, name = p_data[0:6]
        if draw and not dead and team:
            self.names[player].data["coords"] = (x + 18, y + 32)
            self.names[player].data["string"] = name
            self.names[player].Update()
            self.names[player].Draw()

    def _drawflag(self, p_data):
        x, y, draw, dead, team, name, angle, flag = p_data[0:8]
        if draw and not dead and team:
            self.tiles[flag].x, self.tiles[flag].y = x + 10, y + 20
            self.tiles[flag].draw()


    def _drawflair(self, p_data):
        x, y, draw, dead, team, name, angle, flag, flair = p_data[0:9]
        h = self.flairs.height
        if flair and draw and not dead and team:
            rx, ry = flair["x"]*16, h - flair["y"]*16
            subtile = self.flairs.get_region(x = rx, y = ry, width=16, height=16)
            subtile = pyglet.sprite.Sprite(subtile)
            subtile.x, subtile.y = x  - 6, y + 27
            subtile.draw()


    def NewFrame(self, dt, offset = None):
        bool = {"false" : False, "true" : True}
        teams = {2 : "blue ball", 1 : "red ball", 0 : False, None : False}
        flags = {1 : "red flag", 2 : "blue flag", 3 : "neutral flag", 0 : False, 
                 None : False}
        frame = self.data["frame"]
        players = self.players
        h = self.data["height"]
        w = self.data["width"]
        p_data = {}
        for i in players:
            cur = players[i]
            x, y = cur["x"][frame] + 20, h*40 - cur["y"][frame] - 20
            if offset and x and y:
                x, y = x + offset[0], y + offset[1]
            flag = flags[cur["flag"][frame]]
            angle = self._angle(cur)
            team = teams[cur["team"][frame]]
            draw, dead = cur["draw"][frame],  cur["dead"][frame]
            name, flair = cur["name"][frame], cur["flair"][frame]
            p_data[i] = [x, y, draw, dead, team, name, angle, flag, flair]
            self._drawplayer(p_data[i])
            if flag:
                self._drawflag(p_data[i])
        #print(x, y, h, offset)
        for i in p_data:
            self._drawflair(p_data[i])
            self._drawname(p_data[i], i)
        self.data["frame"] += 1
        self.data["frame"] = self.data["frame"] % len(cur["x"])

    def draw(self, dt):
        w, h = self.data["width"]*40, self.data["height"]*40
        self.t += dt
        top = w
        if h > w:
            top = h
        x, y = - (self.t*w/8 % top), - (self.t*h/8 % top)
        if self.t*h/top > 8 or self.t*w/top > 8:
            self.t = 0
        self.NewFrame(dt)

def draw(dt, funcs):
    back()
    for i in funcs:
        i.draw(dt)
    #print(dt)

def main():
    backGr = (0, 0, 0)
    filen = sys.argv[1]
    replay = DecodeReplay(filen)
    Newmap = GenMap(replay.data)
    Newmap.RenderMap()
    dynamic = DynamicElements(replay.data)
    players = Players(replay.data)
    w, h = 1000, 800
    win = pyglet.window.Window(w, h, visible=False, caption="", vsync=0)
    win.set_visible()
    d_time = 1.0/60
    funcs = (Newmap, dynamic, players)
    pyglet.clock.schedule_interval(draw, d_time, funcs)
    pyglet.app.run()


if __name__ == "__main__":
    main()

