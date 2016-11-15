from code_and_map import *
from DecodeReplay import *
from GenMap import *
from PIL import Image

import sys, os, traceback, string, time, json, random

class DynamicElements:

    files = {}
    script_path = os.getcwd()
    files["tiles"] = script_path + "/img/tiles.png"
    files["portal"] = script_path + "/img/portal.png"
    files["boost"] = script_path + "/img/boost.png"
    files["blue boost"] = script_path + "/img/blue boost.png"
    files["red boost"] = script_path + "/img/red boost.png"
    functions = {"tiles" : tiles_map
               , "portal" : portal_map, "boost" : boost_map, 
                 "red boost" : boost_red_map, "blue boost" : boost_blue_map
                 }
    dynamic = ["bomb", "bomb off", "neutral flag", "neutral flag away", "red flag", 
               "red flag away", "blue flag", "blue flag away", 
               "gate neutral", "gate red", "gate blue", "tagpro", "jukejuice", 
               "rolling bomb", "powerup off", "mars ball", "portal off", 
                "boost off", "red boost off", "blue boost off", "black"]
    animated = ["boost", "red boost", "blue boost", "portal"]


    def _toStrings(self):
        pot_animated = {"boost" : "boost", "boost off" : "boost", 
                        "red boost" : "red boost", "red boost off" : "red boost",
                        "blue boost" : "blue boost", "blue boost off" : "blue boost",
                        "portal" : "portal", "portal off" : "portal"}
        self.data["dynamic"] = []
        self.tile_frame = []
        floortiles = self.data["replay"]["floorTiles"]
        for i in floortiles:
            x, y = int(i["x"]), int(i["y"])
            t_codes = i["value"]
            n_codes = []
            for j in t_codes:
                cur_tile = map_codes[str(j)]
                n_codes.append(cur_tile)
            self.data["dynamic"].append({"x" : x, "y" : y, "tiles" : n_codes})
            frame = None
            for j in n_codes:
                if j in pot_animated:
                    function = self.functions[pot_animated[j]]
                    frame = random.randint(0, len(function[pot_animated[j]]) - 1)
            self.tile_frame.append(frame)




    def _gen_Tile_Objs(self):
        self.tiles = {}
        self.tiles_ani = {}
        for element in self.functions:
            newtile = pyglet.image.load(self.files[element])
            for i in self.functions[element]:
                if i in self.dynamic:
                    rx, ry = self.functions[element][i]
                    h = newtile.height
                    #print(rx, ry, self.files[element])
                    newtile_sub = newtile.get_region(x=rx, y = h - 40 - ry, 
                                                     width = 40, height = 40)
                    newsprite = pyglet.sprite.Sprite(newtile_sub)
                    self.tiles[i] = newsprite
                if i in self.animated:
                    self.tiles_ani[i] = []
                    for j in self.functions[element][i]:
                        rx, ry = j[0], j[1]
                        h = newtile.height
                        newtile_sub = newtile.get_region(x=rx, y= h - 40 - ry, 
                                                         width = 40, height = 40)
                        newsprite = pyglet.sprite.Sprite(newtile_sub)
                        self.tiles_ani[i].append(newsprite)

    def focus(self):
        replay = self.data["replay"]
        players = {}
        for i in replay:
            if "player" in i:
                if True in replay[i]["draw"]:
                    players[i] = replay[i]
        for i in players:
            if players[i]["me"] == "me":
                return players[i]


    def __init__(self, replay_data, win):
        self.data = {}
        w = len(replay_data["map"])*40
        h = len(replay_data["map"][0])*40
        self.data["width"], self.data["height"] = w, h
        self.t = 0
        self.data["frame"] = 0
        self.data["replay"] = replay_data
        self.data["win"] = win
        self.sprites = []
        self._toStrings()
        self._gen_Tile_Objs()
        self.follow = False
        self.data["player"] = self.focus()


    def NewFrame(self, dt, offset = None):
        frame = self.data["frame"]
        dyn = self.data["dynamic"]
        animated = self.animated
        w,h = self.data["width"]/40, self.data["height"]/40
        off = ["gate off", "powerup off", "red flag away", 
                "blue flag away", "yellow flag away", "bomb off"]
        for i in range(len(dyn)):
            x, y = dyn[i]["x"], h - 1 - dyn[i]["y"]
            #print(x)
            if dyn[i]["tiles"][frame] in animated:
                n = int(self.tile_frame[i])
                tile = dyn[i]["tiles"][frame]
                rect = (x*40, y*40)
                if offset:
                    rect = (x*40 + offset[0], y*40 + offset[1])
                self.tiles_ani[tile][n].x, self.tiles_ani[tile][n].y = rect
                self.tiles_ani[tile][n].draw()
                self.tile_frame[i] += 0.25
                self.tile_frame[i] = self.tile_frame[i] % len(self.tiles_ani[tile])
            else:
                if dyn[i]["tiles"][frame] not in off:
                    tile = dyn[i]["tiles"][frame]
                    rect = (x*40, y*40)
                    if offset:
                        rect = (x*40 + offset[0], y*40 + offset[1])
                    self.tiles[dyn[i]["tiles"][frame]].x = rect[0]
                    self.tiles[dyn[i]["tiles"][frame]].y = rect[1]
                    self.tiles[dyn[i]["tiles"][frame]].draw()
        self.data["frame"] += 1
        self.data["frame"] = self.data["frame"] % len(dyn[0]["tiles"])

    def draw(self, dt):
        w, h = self.data["win"]
        mh = self.data["height"]
        frame = self.data["frame"]
        x, y = 0, 0
        if self.follow:
            x = w/2 - self.data["player"]["x"][frame] - 20
            y = h/2 - mh + self.data["player"]["y"][frame] + 20
        self.NewFrame(dt, (x, y))

def draw(dt, funcs):
    back()
    for i in funcs:
        i.draw(dt)

def back():
    quad = (0, 800, 1080, 800, 1080, 0, 0, 0)
    color = 'c3B', (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', quad), color)

def main():
    w, h = 1080, 800
    BackGr = (0, 0, 0)
    filen = sys.argv[1]
    replay = DecodeReplay(filen)
    Newmap = GenMap(replay.data, (w, h))
    Newmap.RenderMap()
    dynamic = DynamicElements(replay.data, (w, h))
    old_time = time.time()
    win = pyglet.window.Window(w, h, visible=False, caption="", vsync=0)
    win.set_visible()
    d_time = 1.0/60
    funcs = (Newmap, dynamic)
    pyglet.clock.schedule_interval(draw, d_time, funcs)
    #pyglet.clock.schedule(Newmap.draw)
    #pyglet.clock.schedule(dynamic.draw)
    pyglet.app.run()


if __name__ == "__main__":
    main()

