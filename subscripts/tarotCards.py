from subscripts.cardUtils import Card, CLDisplayHand
from subscripts.spacesavers import *

def useTarotCard(card, save):
    tarotCardInfo = openjson("consumables/tarotDict")[card.number]
    print(f"{card.toString()}")

    # if the tarot card needs you to select cards from your hand (most of them)
    if tarotCardInfo["type"] == "handModifier":
        maxCardSelectAmount = tarotCardInfo["amnt"]
        # death is the only one that needs exactly two cards picked
        canSelectLessThanMax = True
        upTo = "up to "
        if card.number == "Death (XIII)":
            canSelectLessThanMax = False
            upTo = "exactly "

        # makes sure the user selects the correct amount of cards plus error handling
        selectedHandIndexes = []
        selectionIsValid = False
        while not selectionIsValid:
            print(f"Your hand:\n{CLDisplayHand(save.hand)}")
            cardSelection = input(f"Select {upTo}{maxCardSelectAmount} cards, separated by commas and spaces! "
                                  f"Type \"cancel\" to cancel.")
            try:
                selectedHandIndexes = [int(num) for num in cardSelection.split(", ")]
                if len(selectedHandIndexes) > maxCardSelectAmount:
                    print(f"You can't select more than {maxCardSelectAmount} cards at once!")
                elif all(1 <= index <= 8 for index in selectedHandIndexes):
                    if canSelectLessThanMax:
                        selectionIsValid = True
                    else:
                        if len(selectedHandIndexes) == maxCardSelectAmount:
                            selectionIsValid = True
                        else:
                            print(f"Select exactly {maxCardSelectAmount} cards!")
                else:
                    print("Numbers out of range!")
            except:
                print(f"Unrecognized hand indexes: {cardSelection}")

        # suit converters (star, moon, sun, world)
        if tarotCardInfo["modifier"] == "suit":
            for index in selectedHandIndexes:
                save.hand[index-1].suit = tarotCardInfo["suit"]

        # enhancer converters (magician, empress, hierophant, lovers, chariot, justice, devil, tower)
        elif tarotCardInfo["modifier"] == "enhancer":
            for index in selectedHandIndexes:
                save.hand[index-1].enhancement = tarotCardInfo["enhancement"]

        # rank converter (strength)
        elif tarotCardInfo["modifier"] == "rank":
            for index in selectedHandIndexes:
                save.hand[index-1].number = increaseCardVal(save.hand[index-1].number)

        # destroy converter (hanged man)
        elif tarotCardInfo["modifier"] == "destroy":
            for index in selectedHandIndexes:
                del save.hand[index-1]

        # convert converter (death)
        elif tarotCardInfo["modifier"] == "convert":
            save.hand[0] = save.hand[1]

        print(f"Success! New hand:\n{CLDisplayHand(save.hand)}")

def increaseCardVal(oldVal):
    face_cards = {"J": 11, "Q": 12, "K": 13, "A": 14}
    reverse_face_cards = {v: k for k, v in face_cards.items()}

    if oldVal in face_cards:
        value = face_cards[oldVal]
    else:
        value = int(oldVal)

    new_value = value + 1

    if new_value > 14:  # Reset after Ace (A)
        return "2"  # Wrap around back to 2
    return reverse_face_cards.get(new_value, str(new_value))