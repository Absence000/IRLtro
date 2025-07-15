def updateJokers(attribute):
    jokerDict = openjson("jokerDict")
    for joker in jokerDict.items():
        if "type" not in joker[1]:
            typeDict = {
                "c": "chip",
                "m": "mult",
                "xm": "multmult",
                "+": "chipsAndMult",
                "!": "effect",
                "retrig": "retrig",
                "$": "econ"
            }
            index = input(joker[0])
            joker[1][attribute] = typeDict[index]
            savejson("jokerDict", jokerDict)

binaryTest = str(bin(32798)[2:]).zfill(17)
print(binaryTest)
print(binaryTest[3:5])
print(binaryTest[5:8])
print(binaryTest[8:11])
print(binaryTest[11:13])
print(binaryTest[13:17])