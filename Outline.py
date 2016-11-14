import pyglet

class Outlined:
    
    offset = ((-1, -1), (-1, 1), (1, -1), (1, 1))

    def __init__(self, string, font, size, x, y):
        self.data = {}
        self.front = pyglet.graphics.Batch()
        self.back = pyglet.graphics.Batch()
        self.data["string"] = string
        self.data["font"] = font
        self.data["size"] = size
        self.data["coords"] = x, y
        self.data["color"] = (0, 255, 0, 255)
        self.data["outline"] = (0, 0, 0, 255)
        self.text = pyglet.text.Label(string, font_name=font, font_size=size, x=x, 
                                      y=y, anchor_x = 'left', anchor_y = 'center', 
                                      batch=self.front)
        self.outline = []
        for i in self.offset:
            rx, ry = x + i[0], y + i[1]
            text = pyglet.text.Label(string, font_name=font, font_size=size, x=rx, 
                                    y=ry, anchor_x = 'left', anchor_y = 'center', 
                                    batch = self.back)
            self.outline.append(text)


    def Update(self):
        st, f, s = self.data["string"], self.data["font"], self.data["size"]
        x, y = self.data["coords"]
        color, outline = self.data["color"], self.data["outline"]
        self.text.text = st
        self.text.font = f
        self.text.size = s
        self.text.x, self.text.y = x, y
        self.text.color = color
        for i in range(len(self.outline)):
            self.outline[i].text = st
            self.outline[i].font = f
            self.outline[i].size = s
            #print(x, self.offset[i])
            self.outline[i].x = x + self.offset[i][0]
            self.outline[i].y = y + self.offset[i][1]
            self.outline[i].color = outline

    def Draw(self):
        #for i in self.outline:
        #    i.draw()
        #self.text.draw()
        self.back.draw()
        self.front.draw()
