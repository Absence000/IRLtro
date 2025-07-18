class Colors:
    def __init__(self):
        self.backgroundColor = (60, 120, 90)
        self.red = (254, 76, 64)
        self.green = (52, 189, 133)
        self.blue = (0, 146, 255)
        self.white = (255, 255, 255)
        self.yellow = (245, 179, 68)
        self.uiOutline = (125, 62, 62)
        self.darkUI = (27, 38, 40)
        self.lightUI = (59, 80, 85)
        self.blindColors = [(15, 67, 96), (83, 69, 26), (87, 33, 34)]

    # TODO: make multiple colors for each boss blind
    def switchOutline(self, save):
        if save.state == "shop":
            self.uiOutline = (125, 62, 62)
        elif save.state == "playing":
            blindName = save.blindInfo[0]
            if blindName == "Small Blind":
                self.uiOutline = (1, 104, 174)
            elif blindName == "Big Blind":
                self.uiOutline = (164, 108, 0)
            elif blindName == "Boss Blind":
                self.uiOutline = (174, 20, 19)
