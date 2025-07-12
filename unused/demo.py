def passwordDemo():
    notGuessed = True

    while notGuessed:
        userInput = input("put in the password!")
        password = "abc123"

        if userInput == password:
            notGuessed = False
        else:
            print("Try again!")

    print("success!")


class Person:
    def __init__(self, name, age, profession):
        self.name = name
        self.age = age
        self.profession = profession

    def toString(self):
        return f"Name: {self.name}\nAge: {self.age}\nProfession: {self.profession}\n"

    def toDict(self):
        return {
            "name": self.name,
            "age": self.age,
            "profession": self.profession
        }


def personFromDict(personDict):
    return Person(personDict["name"], personDict["age"], personDict["profession"])

personDict = {'name': 'dave', 'age': 24, 'profession': 'doctor'}

dave = personFromDict(personDict)

print(dave.toString())

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