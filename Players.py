from code_and_map import *
from DecodeReplay import *
from GenMap import *
from DynamicElements import *
from Outline import *
from PIL import Image

import pyglet

import sys, os, traceback, string, time, json, random, datetime

class Players:
    files = {}
    script_path = os.getcwd()
    files["tiles"] = script_path + "/img/tiles.png"
    files["flairs"] =script_path + "/img/flair.png"
    functions = {"tiles" : tiles_map
                 }
    balls = ("blue ball", "red ball")
    flag = ("neutral flag", "red flag", "blue flag")

    def _gen_Tile_Objs(self):
        self.tiles = {}
        newtile = Image.open(self.files["tiles"])
        for i in self.balls:
            self.tiles[i] = []
            rx, ry = self.functions["tiles"][i]
            subtile = newtile.crop((rx, ry, rx + 40, ry + 40))
            for j in range(360):
                n_img = subtile.rotate(j, resample=Image.BICUBIC)
                n_img = n_img.tobytes()
                pyg_img = pyglet.image.ImageData(40, 40, "RGBA", n_img)
                pyg_img.anchor_x = int(pyg_img.width/2)
                pyg_img.anchor_y = int(pyg_img.height/2)
                pyg_spr = pyglet.sprite.Sprite(pyg_img)
                self.tiles[i].append(pyg_spr)
        for i in self.flag:
            newtile = pyglet.image.load(self.files["tiles"])
            h = newtile.height
            rx, ry = self.functions["tiles"][i]
            subtile = newtile.get_region(x=rx, y=h-40 -ry, width=40, height=40)
            subtile = pyglet.sprite.Sprite(subtile, batch=self.batch)
            self.tiles[i] = subtile

    def _gen_flairs(self):
        #flairs
        flairs = pyglet.image.load((self.files["flairs"]))
        grid = pyglet.image.ImageGrid(flairs, 10, 11)
        self.flairs = pyglet.image.TextureGrid(grid)

    def _gen_names(self):
        self.names = {}
        for i in self.players:
            name = self.players[i]["name"]
            text = Outlined(i, "Times New Roman", 10, 0, 0)
            self.names[i] = text


    def focus(self):
        for i in self.players:
            if self.players[i]["me"] == "me":
                return self.players[i]

    def __init__(self, replay_data, win):
        self.t = 0
        self.data = {}
        self.data["frame"] = 0
        self.data["replay"] = replay_data
        self.data["width"] = len(replay_data["map"])
        self.data["height"] = len(replay_data["map"][0])
        self.data["win"] = win
        n = 0
        self.players = {}
        self.batch = pyglet.graphics.Batch()
        for i in replay_data:
            if "player" in i:
                if True in replay_data[i]["draw"]:
                    self.players[i] = replay_data[i]
        self._gen_Tile_Objs()
        self._gen_names()
        self._gen_flairs()
        self.data["player"] = self.focus()
        self.p_angle = 0

    def _angle(self, cur):
        frame = self.data["frame"]
        angle = cur["angle"][frame]
        if angle:
            angle = int(angle*360/(2*3.14))
        return angle

    def _drawplayer(self, p_data):
        x, y, draw, dead, team, name, angle = p_data[0:7]
        if draw and not dead and team:
            #if angle:
            #    if angle != self.p_angle:
            #        self.tiles[team].rotation = angle
            #        self.tiles[team].scale = 1
            angle = int(angle % 360)
            self.tiles[team][angle].x, self.tiles[team][angle].y = x, y
            self.tiles[team][angle].draw()

    def _drawname(self, p_data, player):
        x, y, draw, dead, team, name = p_data[0:6]
        x,y = int(x), int(y)
        if draw and not dead and team:
            self.names[player].data["coords"] = (x + 18, y + 32)
            self.names[player].data["string"] = name
            self.names[player].Update()
            self.names[player].Draw()

    def _drawflag(self, p_data):
        x, y, draw, dead, team, name, angle, flag = p_data[0:8]
        if draw and not dead and team:
            self.tiles[flag].x, self.tiles[flag].y = x - 7, y + 11
            self.tiles[flag].draw()


    def _drawflair(self, p_data):
        x, y, draw, dead, team, name, angle, flag, flair = p_data[0:9]
        h = self.flairs.height/16
        if flair and draw and not dead and team:
            rx, ry = flair["x"], h - 1 - flair["y"]
            rx, ry = int(rx), int(ry)
            pos = ry*11 + rx
            flair_t = self.flairs[(pos)]
            subtile = pyglet.sprite.Sprite(flair_t)
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
        #timea = time.time()
        for i in players:
            cur = players[i]
            x, y = cur["x"][frame] + 20, h*40 - cur["y"][frame] - 20
            if offset and x and y:
                x, y = x + offset[0], y + offset[1]
            x, y = int(x), int(y)
            flag = flags[cur["flag"][frame]]
            angle = self._angle(cur)
            team = teams[cur["team"][frame]]
            draw, dead = cur["draw"][frame],  cur["dead"][frame]
            name, flair = cur["name"][frame], cur["flair"][frame]
            p_data[i] = [x, y, draw, dead, team, name, angle, flag, flair]
            self._drawplayer(p_data[i])
            if flag:
                self._drawflag(p_data[i])
        for i in p_data:
            #self._drawflair(p_data[i])
            self._drawname(p_data[i], i)
        #timeb = time.time()
        #print(timeb - timea)
        self.data["frame"] += 1
        self.data["frame"] = self.data["frame"] % len(cur["x"])

    def draw(self, dt):
        w, h = self.data["win"]
        mh = self.data["height"]*40
        frame = self.data["frame"]
        x = w/2 - self.data["player"]["x"][frame] - 20
        y = h/2 - mh + self.data["player"]["y"][frame] + 20
        offset = x, y
        self.NewFrame(dt, offset)


def draw(dt, funcs, fps):
    #timea = time.time()
    back()
    for i in funcs:
        i.draw(dt)
    fps.draw()
    #timeb = time.time()
    #print(timea - timeb)
    #print(dt)

def main():
    w, h = 1000, 800
    backGr = (0, 0, 0)
    filen = sys.argv[1]
    replay = DecodeReplay(filen)
    Newmap = GenMap(replay.data, (w, h))
    Newmap.RenderMap()
    Newmap.follow = True
    dynamic = DynamicElements(replay.data, (w, h))
    dynamic.follow = True
    players = Players(replay.data, (w, h))
    win = pyglet.window.Window(w, h, visible=False, caption="")
    win.set_visible()
    fps= pyglet.clock.ClockDisplay()
    d_time = 1.0/60
    funcs = (Newmap, dynamic, players)
    #funcs = (dynamic, players)
    pyglet.clock.schedule_interval(draw, d_time, funcs, fps)
    pyglet.app.run()


if __name__ == "__main__":
    main()

