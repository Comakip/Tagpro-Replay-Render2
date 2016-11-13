from code_and_map import *
from DecodeReplay import *
from GenMap import *
from PIL import Image

import sys, os, traceback, string, time, json, random

class DynamicElements:

    files = {}
    script_path = os.path.dirname(__file__)
    files["tiles"] = script_path + "/img/tiles.png"
    files["portal"] = script_path + "/img/portal.png"
    files["boost"] = script_path + "/img/Boost.png"
    files["blue boost"] = script_path + "/img/Blue Boost.png"
    files["red boost"] = script_path + "/img/Red Boost.png"
    functions = {"tiles" : tiles_map
               , "portal" : portal_map, "boost" : boost_map, 
                 "red boost" : boost_red_map, "blue boost" : boost_blue_map
                 }
    dynamic = ["bomb", "bomb off", "neutral flag", "neutral flag away", "red flag", 
               "red flag away", "blue flag", "blue flag away", "gate off", 
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



    def __init__(self, replay_data):
        self.data = {}
        w = len(replay_data["map"])*40
        h = len(replay_data["map"][0])*40
        self.data["width"], self.data["height"] = w, h
        self.t = 0
        self.data["frame"] = 0
        self.data["replay"] = replay_data
        self.sprites = []
        self._toStrings()
        self._gen_Tile_Objs()


    def NewFrame(self, dt, offset = None):
        frame = self.data["frame"]
        dyn = self.data["dynamic"]
        animated = self.animated
        w,h = self.data["width"]/40, self.data["height"]/40
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
        #w, h = self.data["width"], self.data["height"]
        #self.t += dt
        #top = w
        #if h > w:
        #    top = h
        #x, y = -(self.t*w/8 % top), -(self.t*h/8 % top)
        #if self.t*h/top > 8 or self.t*w/top > 8:
        #    self.t = 0
        #fps = pyglet.clock.ClockDisplay()
        #fps.draw()
        self.NewFrame(dt)

def draw(dt, funcs):
    back()
    for i in funcs:
        i.draw(dt)

def back():
    quad = (0, 800, 1080, 800, 1080, 0, 0, 0)
    color = 'c3B', (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', quad), color)

def main():
    BackGr = (0, 0, 0)
    filen = sys.argv[1]
    replay = DecodeReplay(filen)
    Newmap = GenMap(replay.data)
    Newmap.RenderMap()
    dynamic = DynamicElements(replay.data)
    old_time = time.time()
    w, h = 1080, 800
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

