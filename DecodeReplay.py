import json


class DecodeReplay:

    playern = ("player1", "player2", "player3", "player4", "player5", "player6",
               "player7", "player8")

    def __init__(self, repfile):
        json_data = open(repfile, "r")
        self.data = json.load(json_data)
        self.players = []
        for i in self.playern:
            if i in self.data:
                self.players.append(self.data[i])

    def Players(self):
        return self.players


    def __str__(self):
        out = ""
        for i in self.data:
            out += i + ", "
        return out


def main():
    filen = sys.argv[1]
    fullpath = filen
    fullpath = path + filen
    replay = DecodeReplay(fullpath)
    print(replay)
    print(type(replay.Players()[0]))


if __name__ == "__main__":
    main()

