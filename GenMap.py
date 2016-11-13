from code_and_map import *
from DecodeReplay import *
from PIL import Image

import sys, os, traceback, string, time, json, pyglet


class GenMap:
    files = {}
    script_path = os.path.dirname(__file__)
    files["tiles"] = script_path + "/img/Tiles.png"
    files["portal"] = script_path + "/img/Portal.png"
    files["boost"] = script_path + "/img/Boost.png"
    files["blue boost"] = script_path + "/img/Blue Boost.png"
    files["red boost"] = script_path + "/img/Red Boost.png"
    functions = {"tiles" : tiles_map
               #, "portal" : portal_map, "boost" : boost_map, 
               #  "red boost" : boost_red_map, "blue boost" : boost_blue_map}
               }
    dynamic = ["bomb", "bomb off", "neutral flag", "neutral flag away", "red flag", 
               "red flag away", "blue flag", "blue flag away", "gate off", 
               "gate neutral", "gate red", "gate blue", "tagpro", "jukejuice", 
               "rolling bomb", "powerup off", "mars ball", "portal", "portal off", 
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
        excluded = ("black", "wall", "floor", "gate off", "gate neutral", "gate red", 
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


    def __init__(self, map_data):
        self.t = 0
        h =len(map_data["map"][0])
        w = len(map_data["map"])
        self.data = {}
        self.data["height"] = h*40
        self.data["width"] = w*40
        self.data["map height"] = h
        self.data["map width"] = w
        self.last = False
        self.map_data = map_data
        self._toStrings()
        #self.tiles = pyglet.image.load(self.files["tiles"])
        self.s_batch = pyglet.graphics.Batch()
        self._gen_rects()
        self._back_tiles()
        self._gen_smooth()
        self._gen_Tile_Objs()
        self.img = Image.new("RGBA", (w*40, h*40), "black")

    def RenderMap(self):
        m_height = self.data["height"]
        excluded = ["315 tile", "45 tile", "225 tile", "135 tile"]
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

    def draw(self, dt, offset=None):
        #self.t += dt
        #w, h = self.data["width"], self.data["height"]
        #hr, wr = float(w)/h, float(h)/w
        #top = w
        #if h > w:
        #    top = h
        #x, y = -(self.t*w/8 % top), -(self.t*h/8 % top)
        #if self.t*h/top > 8 or self.t*w/top > 8:
        #    self.t = 0
        if offset:
            self.sprite.x += offset[0]
            self.sprite.x += offset[1]
        self.sprite.draw()

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
    backGr = (0, 0, 0)
    filen = sys.argv[1]
    replay = DecodeReplay(filen)
    tp_map = GenMap(replay.data)
    tp_map.RenderMap()
    w, h = 1080, 800
    win = pyglet.window.Window(w, h, visible=False, caption="", vsync=0)
    win.set_visible()
    win.PYGLET_VSYNC = 0
    pyglet.clock.schedule(back)  
    pyglet.clock.schedule(tp_map.draw)  
    #tp_map.RenderMap(win)
    pyglet.app.run()
    



if __name__ == "__main__":
    main()

