
import random
import hashlib

from modules.SetElem import SetElem

# This class represents the set of actions that can be used to encode information
# Each of the groups in which the message has been divided is mapped with one SetElem.
# The message is sent through the channel by executing all the actions that represent it
class Set:
    # Attributes:
    # - groupSize (int):              The message will be divided in groups of "groupSize"
    #                                 bits. The length of the set is determined by this number
    #
    # - scramblingDisplacement (int): As the actions of the Set can be calculated mathematically,
    #                                 a way of scrambling the set is needed. A ROT-N """cipher""" is 
    #                                 used to do this, where N is this argument
    #
    # - scramblingModulo (int):       The modulo for the ROT-N operation

    def __init__(self, groupSize, scramblingPassword):
        self.groupSize = groupSize

        # Run the "scramblingPassword" though a SHA-256 hash and get two bytes from it
        myhash = hashlib.sha256(scramblingPassword.encode())
        twoBytes = int(myhash.hexdigest()[14:18], 32)

        # Use the two bytes obtained from the hash as the N value of a ROT-N
        self.scramblingDisplacement = twoBytes

        # The modulo for the ROT-N operation must be the number of elements in the set
        # In this case, this number sould be calculated, as the set is not defined
        # using an array, but using some rules
        self.scramblingModulo = pow(2, groupSize)

    # Implements a ROT-N operation for "scrambling" the set
    def __applyScrambling__(self, index):
        return (index + self.scramblingDisplacement) % self.scramblingModulo

    # Implements the operation needed to undo the ROT-N operation
    def __unapplyScrambling__(self, scrambledIndex):
        return ((self.scramblingModulo - self.scramblingDisplacement) + scrambledIndex) % self.scramblingModulo

    # Alternative scrambling function. This function sould be called manually after instantiating
    # this class. It implements a "better" scrambling algorithm, but the performance of it in a large
    # list like the one needed here (length of 2^24 elements) is bad
    # def scramble(self, password):
    #     # Fill the array with sequential numbers
    #     # self.scramblingArray = []
    #     for i in range(0, pow(2, self.groupSize)):
    #         self.scramblingArray.append(i)
    #
    #     # Shuffle the numbers in the array using the Fisher-Yates scrambling algorithm
    #     seed = int("".join([str(ord(e)) for e in password]))
    #     random.seed(seed)
    #
    #     for i in range(len(self.scramblingArray)-1, 0, -1):
    #         # Select a random index between 0 and i
    #         j = random.randint(0, i+1)
    #         # Swap position i and j
    #         self.scramblingArray[i], self.scramblingArray[j] = self.scramblingArray[j], self.scramblingArray[i]

    # All the SetElems have some attributes that allow some kind of ordering
    # Instead of looking for the SetElem in the array, we extract this
    #  "sortable" attributes and compute the index manually, as they follow
    #  a predictable pattern
    # The function calculates the position of the SetElem based on the
    # action it represents, in this case, related with color changes
    def getIndexOf(self, setElem):
        elemColor = setElem.color
        index  = elemColor[0] * (256*256)
        index += elemColor[1] * 256
        index += elemColor[2]

        return self.__unapplyScrambling__(index)
        # return self.scramblingArray.index(index)

    # Returns the element at a certain position AFTER using the "scramblingArray"
    def getElemAt(self, index):
        # scrambledIndex = self.scramblingArray.index(index)
        scrambledIndex = self.__applyScrambling__(index)

        # From the unscrambled index it is possible to calculate which
        # action is in it without the need of having the array physically
        # in memory, because the elements follow an order that can be
        # expressed mathematically.
        # In this case, converting a 27-bit number into 3 independent bytes
        # that represent an RGB color, taking the R component as the ones with
        # the Most-Significant-Bits, and B as the one with Less-Significant-Bits
        color = [None] * 3

        color[2] = scrambledIndex % 256
        scrambledIndex //= 256
        color[1] = scrambledIndex % 256
        color[0] = scrambledIndex // 256

        return SetElem(color)
