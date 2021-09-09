
# This class represents something that has the ability to represent information
# in the stego-channel
# In this case, it represents the possible actions that can be performed in the document
# As all the considered actions are related with changing the color of the text, the content
# of the class is very simple, as there is no need to distinguish between action types, for example
# This class can be read as: "An action that consists on changing the color of some text to a specific RGB value"
class SetElem:
    # Attributes:
    # - color (list): A list of 3 numbers between 0-255 that represent
    #                 an RGB color. The order of the components MUST BE R,G,B

    def __init__(self, color):
        self.color = color
