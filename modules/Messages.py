
from modules.SetElem import SetElem

# Represents a message that is not encoded to be sent thorugh the stego-channel
class PlainMessage:
    # Attributes
    # - groups (list): List of groups of N bits that conform the message.
    #                  This list must include the lengthIndicator and the paddingIndicator groups

    def __init__(self, groups):
        self.groups = groups

    # Mimic some kind of "constructor overloading" by using a "factory function" pattern
    @classmethod
    def fromBytes(cls, messageString, groupSize) -> "PlainMessage":
        # Convert the message into binary
        bits = "".join([format(byte, "08b") for byte in messageString])

        # Calculate how much padding is needed
        remainderBitNumber = len(bits) % groupSize
        paddingLength = 0 if remainderBitNumber == 0 else groupSize - remainderBitNumber

        # Add padding to the bits
        bits += "0" * paddingLength

        # Add padding indicator bits
        bits += "0" * (groupSize - paddingLength) + "1" * paddingLength

        # Split the bits into groups of length "groupSize"
        groups = [(bits[i:i+groupSize]) for i in range(0, len(bits), groupSize)]

        # Prepend a "length indicator" group to the message (number of groups, including
        # padding indicator and excluding the length indicator itself)
        lengthIndicator = format(len(groups), "0" + str(groupSize) + "b")
        groups.insert(0, lengthIndicator)
        
        return cls(groups)

    # Convert all the groups into a list of SetElems
    # The elements are returned inside a EncodedMessage object
    def encode(self, Set):
        elems = []
        for group in self.groups:
            index = int(group, 2)
            elems.append(Set.getElemAt(index))

        return EncodedMessage(elems)

    # Assemble a bytes-like object from the groups. This function handles all the
    # added extra groups, like the length indicator and the padding indicator
    def getMessage(self):
        # If there are no groups, the message is empty
        if len(self.groups) == 0:
            return bytes([])

        # The first group encodes how many groups actually contain
        # the message (including the padding indicator group)
        lengthIndicator = int(self.groups[0], 2)

        # Check if the document has enough groups as required by
        # the length indicator
        if len(self.groups) < lengthIndicator:
            print("ERROR\nThe message is supposed to have " + str(lengthIndicator) +
                    " groups, but only " + str(len(self.groups)) + " were found")
            exit()

        # Calculate how much padding has been added
        # by counting the number of 1s in the padding indicator
        # (the last group of the message)
        # paddingSize = len([c for i,c in enumerate(self.groups[-1]) if c == "1"])
        paddingSize = len([c for i,c in enumerate(self.groups[lengthIndicator]) if c == "1"])

        # Join all the groups into a string of bits
        # except the last group, which is a padding indicator
        # and the first group, which is a length indicator
        # and remove the padding
        bits = "".join(self.groups[1:lengthIndicator])
        bits = bits if paddingSize == 0 else bits[:-paddingSize]

        # Group the bits into bytes
        byteList = [int(bits[i:i+8], 2) for i in range(0, len(bits), 8)]

        # Returns a bytes-like object for later file write
        return bytes(byteList)

    # Calculates how many SetElems are needed to encode this message
    def calculateEncodedSize(self):
        # Same as the formula N = (8xmessageByteSize)/(log2(setLength))
        return len(self.groups)

# Represents a message that is ready to be sent through the stego-channel
class EncodedMessage:
    # Attributes
    # - values (array of SetElem): SORTED array that represents the encoded message

    def __init__(self, setElemList):
        self.values = setElemList

    @classmethod
    def fromGoogleDoc(cls, gdoc) -> "EncodedMessage":
        # If the document does not contain any slot, the message is empty
        if len(gdoc.content) == 0:
            return cls([])

        # Convert each slot in the google document into a
        # SetElem object, each one representing one action that
        # has been applied to the document
        elems = []
        for space in gdoc.content:
            elems.append(SetElem(space["color"]))

        return cls(elems)

    # Covnerts each object of the class SetElem into a group of bits
    def decode(self, Set):
        groups = []
        # Convert each SetElem into a group
        for setElem in self.values:
            # Find the SetElem in the set. The position of the element
            # in the Set is the decoded message
            index = Set.getIndexOf(setElem)

            # Convert the index into a group of bits with a fixed
            # "groupSize" length "adding leeading zeros if necessary)
            group = format(index, "0" + str(Set.groupSize) + "b")

            groups.append(group)

        return PlainMessage(groups)

    # Updates the document by parforming all the actions that represent the
    # encoded message in the correct order
    def sendToDoc(self, gdoc):
        gdoc.commit(self.values)

