from code_and_map import *
from DecodeReplay import *
from PIL import Image

import sys, os, traceback, string, time, json, pyglet


class GenMap:
    files = {}
    script_path = os.getcwd()
    files["tiles"] = script_path + "/img/tiles.png"
    files["portal"] = script_path + "/img/portal.png"
    files["boost"] = script_path + "/img/boost.png"
    files["blue boost"] = script_path + "/img/blue boost.png"
    files["red boost"] = script_path + "/img/bed boost.png"
    functions = {"tiles" : tiles_map
               #, "portal" : portal_map, "boost" : boost_map, 
               #  "red boost" : boost_red_map, "blue boost" : boost_blue_map}
               }
    dynamic = ["bomb", "neutral flag", "red flag", "blue flag", 
               "gate neutral", "gate red", "gate blue", "tagpro", "jukejuice", 
               "rolling bomb", "mars ball", "portal", "portal off", 
                "boost", "boost off", "red boost", "red boost off", "blue boost",
                "blue boost off"]
    with open('rotateCoords.json') as data_file:    
        smooth_coords = json.load(data_file)

    def _toStrings(self):
        self.map_layout = []
        for i in range(len(self.map_data["map"])):
            pixels_h = []
            for j in range(len(self.map_data["map"][i])):
                cur_pix = str(self.map_data["map"][i][j])
                cur_string = map_codes[cur_pix]
                pixels_h.append(cur_string)
            self.map_layout.append(pixels_h)



    def _back_tiles(self):
        excluded = ("black", "wall", "floor", "gate neutral", "gate red", 
                    "gate blue", "red endzone", "blue endzone")
        background = ("floor", "black", "red speed", "blue speed",
                      "red endzone", "blue endzone")
        self.back_tiles = []
        m_h = self.data["map height"]
        for i in range(len(self.tiles_id)):
            #print(self.tiles_id[i - m_w], self.tiles_id[i], 
            #      self.tiles_id[i + m_w])
            if self.tiles_id[i] in excluded:
                self.back_tiles.append(None)
            else:
                cur = "floor"
                for j in background:
                    try:
                        if self.tiles_id[i - 1] == j or self.tiles_id[i + 1] == j:
                            cur = j
                            break
                        if self.tiles_id[i - m_h] == j or \
                           self.tiles_id[i + m_h] == j:
                            cur = j
                            break
                    except:
                        pass
                self.back_tiles.append(cur)


    def _gen_rects(self):
        self.rects = [] 
        self.tiles_id = []
        for i in range(len(self.map_layout)):
            for j in range(len(self.map_layout[i])):
                new_rect = (i*40, j*40, (j+1)*40, (i+1)*40)
                self.rects.append(new_rect)
                self.tiles_id.append(self.map_layout[i][j])

    def _gen_smooth(self):
        s_c = self.smooth_coords
        self.smooth = {}
        smooth_obj = Image.open(self.files["tiles"])
        for i in s_c:
            rx, ry = s_c[i]["x"], s_c[i]["y"]
            rx, ry = int(rx*40), int(ry*40)
            box = (rx, ry, rx + 20, ry + 20)
            newtile_sub = smooth_obj.crop(box)
            self.smooth[i] = newtile_sub



    def _gen_Tile_Objs(self):
        self.tiles = {}
        for element in self.functions:
            newtile = Image.open(self.files[element])
            for i in self.functions[element]:
                if i not in self.dynamic:
                    rx, ry = self.functions[element][i]
                    box = (rx, ry, rx + 40, ry + 40)
                    newtile_sub = newtile.crop(box)
                    self.tiles[i] = newtile_sub

    def focus(self):
        players = {}
        for i in self.map_data:
            if "player" in i:
                if True in self.map_data[i]["draw"]:
                    players[i] = self.map_data[i]
        for i in players:
            if players[i]["me"] == "me":
                return players[i]

    def __init__(self, replay_data, win):
        self.t = 0
        h =len(replay_data["map"][0])
        w = len(replay_data["map"])
        self.data = {}
        self.data["height"] = h*40
        self.data["width"] = w*40
        self.data["map height"] = h
        self.data["map width"] = w
        self.data["win"] = win
        self.last = False
        self.map_data = replay_data
        self._toStrings()
        #self.tiles = pyglet.image.load(self.files["tiles"])
        self.s_batch = pyglet.graphics.Batch()
        self._gen_rects()
        self._back_tiles()
        self._gen_smooth()
        self._gen_Tile_Objs()
        self.img = Image.new("RGBA", (w*40, h*40), "black")
        self.follow = False
        self.data["player"] = self.focus()
        self.data["frame"] = 0

    def RenderMap(self):
        m_height = self.data["height"]
        excluded = ["315 tile", "45 tile", "225 tile", "135 tile"]
        off = {"gate red" : "gate off", "gate blue" : "gate off", 
                "gate green" : "gate off", "gate off" : "gate off", 
                "red flag" : "red flag away", "red flag away" : "red flag away", 
                "blue flag" : "blue flag away", "blue flag away" : "blue flag away", 
                "yellow flag" : "yellow flag away", 
                "yellow flag away" : "yellow flag away", "bomb" : "bomb off", 
                "bomb off" : "bomb off", "jukejuice" : "powerup off", 
                "rolling bomb" : "powerup off", "tagpro" : "powerup off", 
                "powerup off" : "powerup off"
                }
        newtile = pyglet.image.load(self.files["tiles"])
        for i in range(len(self.back_tiles)):
            if self.back_tiles[i]:
                rect = (self.rects[i][0], self.rects[i][1])
                subtile = self.tiles[self.back_tiles[i]]
                self.img.paste(subtile, rect, mask=subtile)
        for i in range(len(self.tiles_id)):
           if self.tiles_id[i] not in self.dynamic and self.tiles_id[i] not in excluded:
                rect = (self.rects[i][0], self.rects[i][1])
                subtile = self.tiles[self.tiles_id[i]]
                self.img.paste(subtile, rect, mask=subtile)
        for i in range(len(self.tiles_id)):
            if self.tiles_id[i] in off:
                rect = self.rects[i][0], self.rects[i][1]
                subtile = self.tiles[off[self.tiles_id[i]]]
                self.img.paste(subtile, rect, mask=subtile)
        w_map = self.map_data["wallMap"]
        rel_coord = [(0, 0), (0, 20), (20,20), (20, 0)]
        s_c = self.smooth_coords
        for i in range(len(w_map)):
            for j in range(len(w_map[i])):
                for k in range(len(w_map[i][j])):
                    if w_map[i][j][k] != 0:
                        key = w_map[i][j][k]
                        rx, ry = s_c[key]["x"], s_c[key]["y"]
                        square = rx*40, ry*40, 20, 20
                        y = j*40 + rel_coord[k][0]
                        y2 = y - 20
                        x = i*40 + rel_coord[k][1]
                        x2 = x + 20
                        self.img.paste(self.smooth[key], (x, y), mask=self.smooth[key])
        self.img.save("test.png")
        self.img = self.img.transpose(Image.FLIP_TOP_BOTTOM)
        raw_img = self.img.tobytes()
        w, h = self.data["width"], self.data["height"]
        raw_img = pyglet.image.ImageData(w, h, "RGBA", raw_img)
        spr_ = pyglet.sprite.Sprite(raw_img)
        spr_.x, spr_.y = 0, 0
        self.sprite = spr_

    def draw(self, dt):
        frame = self.data["frame"]
        w, h = self.data["win"]
        mh = self.data["height"]
        if self.follow:
            self.sprite.x = w/2 - self.data["player"]["x"][frame] - 20
            self.sprite.y = h/2 -mh + self.data["player"]["y"][frame] + 20
        self.sprite.draw()
        self.data["frame"] += 1
        self.data["frame"] = self.data["frame"] % len(self.data["player"]["x"])


    def __str__(self):
        out = ""
        for i in self.map_data:
            for j in i:
                out += j + ", "
        return out

def back(dt):
    quad = (0, 800, 1080, 800, 1080, 0, 0, 0)
    color = 'c3B', (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', quad), color)

def main():
    w, h = 1080, 800
    backGr = (0, 0, 0)
    filen = sys.argv[1]
    replay = DecodeReplay(filen)
    tp_map = GenMap(replay.data, (w, h))
    tp_map.follow = True
    tp_map.RenderMap()
    win = pyglet.window.Window(w, h, visible=False, caption="", vsync=0)
    win.set_visible()
    win.PYGLET_VSYNC = 0
    pyglet.clock.schedule(back)  
    pyglet.clock.schedule(tp_map.draw)  
    #tp_map.RenderMap(win)
    pyglet.app.run()
    



if __name__ == "__main__":
    main()

