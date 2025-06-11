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