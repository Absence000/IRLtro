from subscripts.spacesavers import *

class Spectral:
    def __init__(self, name, negative=None):
        self.name = name
        self.negative = negative

    def toString(self, mode=None):
        isNegative = ""
        if self.negative:
            isNegative = "Negative "
        if mode is None:
            return f"{isNegative}{self.name}: {openjson('consumables/spectralDict')[self.name]['description']}"
        else:
            return f"{isNegative}{self.name}"

    def toDict(self):
        return{
            "name": self.name,
            "negative": self.negative,
            "type": "spectral"
        }

    def toBinary(self):
        nameIndex = list(openjson('consumables/spectralDict').keys()).index(self.name)
        negativeBit = "0"
        if self.negative:
            negativeBit = "1"
        binaryEncoder = "101" + str(format(nameIndex, '05b')) + negativeBit + "00000000"
        return int(binaryEncoder, 2)