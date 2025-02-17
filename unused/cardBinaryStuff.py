from PIL import Image
from subscripts.cardUtils import Card
from cardCreationAndRecognition.cardImageCreator import createImageFromCard

# old experiment, unused rn
def binaryToFiducial(binary):
    width, height = 5, 4
    image = Image.new("1", (width, height))  # "1" mode for 1-bit pixels (black & white)
    pixels = image.load()

    for i in range(height):
        for j in range(width):
            pixels[j, i] = 0 if binary[i * width + j] == '1' else 1

    baseImage = Image.open("../cardCreationAndRecognition/blankFiducial.png")
    baseImage.paste(image, (2, 2))
    return baseImage


# binary = encodeCardToBinary(Card(subset="playing", number="A", suit="D", enhancement="steel", edition="polychrome", seal="purple"))
# print(binary)
# binaryToFiducial(binary).show()
# testCard = decodeBinaryToCard(binary)

# createImageFromCard(testCard).show()