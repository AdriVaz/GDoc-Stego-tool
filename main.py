
import argparse, os, sys
import zipfile, io

from modules.Set import Set
from modules.GoogleDoc import GoogleDoc
from modules.Messages import PlainMessage, EncodedMessage
from modules.PGP import PGP

def compress(fileName):
    buffer = io.BytesIO()
    zf = zipfile.ZipFile(buffer, "w")

    toCompress = open(fileName, "rb").read()
    zf.writestr(fileName, toCompress)

    zf.close()
    buffer.seek(0)

    return buffer.read()

def decompress(buffer, dirName):
    buffer = io.BytesIO(buffer)
    zf = zipfile.ZipFile(buffer, "r")
    zf.extractall(dirName)

if __name__ == "__main__":
    ################################# PARAMS #################################
    # Params:
    # - direction:          <s or r> send or receive
    # - scramblingKey:      The key used to scramble the set
    # - rsaKeyFile:         Public or private RSA keys in PEM format
    # - credentialsFile:    The JSON file with the credentials for the API
    # - messageFile:        A file that contains the file to send
    ##########################################################################

    argParser  = argparse.ArgumentParser(description="Google Docs stego-tool")

    argParser.add_argument("direction", metavar="<direction>", choices=["s", "r"], help='"s" to send a message. "r" to receive a message')
    argParser.add_argument("scramblingKey", metavar="<scramblingKey>", type=str, help='The "stego key" used to scramble the set used in encoding and decoding')
    argParser.add_argument("rsaKeyFile", metavar="<rsaKeyFile>", help="If sending, the public key of the receiver (to encrypt). If receiving, the private key of the reveiver (to decrypt)")
    argParser.add_argument("credentialsFile", metavar="<credentialsFile>", help="JSON file that contains the login access of the account used")
    argParser.add_argument("file", metavar="<file>", help="If sending, the input file. If receiving, the folder where the received file will be written")

    args = argParser.parse_args()

    ################################################################################

    # Check that the reveiverPublicKeyFile exists
    if not os.path.isfile(args.rsaKeyFile):
        print("ERROR: The rsaKeyFile must exist")
        exit()

    # Check that the credentialsFile exists
    if not os.path.isfile(args.credentialsFile):
        print("ERROR: The credentialsFile must exist")
        exit()

    # Check the input or output file
    if args.direction == "s":
        # The input file must exist
        if not os.path.isfile(args.file):
            print("ERROR: The input file must exist")
            exit()
    elif args.direction == "r":
        #The output file cannot exist
        if os.path.isfile(args.file):
            print("ERROR: the output directory exists, and it is a file")
            exit()
        # The output dir cannot exist, because it is created by "zipfile"
        if os.path.isdir(args.file):
            print("The output directory already exists. Aborting.")
            exit()
    else:
        # Should not be reached. Already treated by argparse
        print('ERROR: The direction should be "s" or "r"')
        exit()

    ################################################################################

    # Create the set that will be used to convert groups into SetElems
    print("Generating encoding set...  ", end="")
    sys.stdout.flush()

    # The group size depends on the length of the encoding set exclusively
    GROUP_SIZE = 24
    myset = Set(GROUP_SIZE, args.scramblingKey)

    print("Done")

    # Read and parse the Google document
    print("Reading Google document...  ", end="")
    sys.stdout.flush()

    gdoc = GoogleDoc(args.credentialsFile)

    print("Done\n")

    # Choose between "send" and "receive" operations
    if args.direction == "s":
        # Read the file content and encrypt it
        print("Compressing the file...     ", end="")
        sys.stdout.flush()

        fileContent = compress(args.file)

        print("Done")


        # Encrypt the message before sending
        print("Encrypting message...       ", end="")
        sys.stdout.flush()

        pgp = PGP()
        pgp.addPublicKey(args.rsaKeyFile)

        ciphertext = pgp.encrypt(fileContent)

        print("Done")


        print("Encoding the message...     ", end="")
        sys.stdout.flush()

        plainMsg = PlainMessage.fromBytes(ciphertext, myset.groupSize)

        # Check if the document is long enough to hold the whole message
        availableSlotCount = gdoc.getAvailableSpaceCount()
        neededSlotCount    = plainMsg.calculateEncodedSize()

        if availableSlotCount < neededSlotCount:
            print("ERROR\nThe document does not have the necessary length to fully hold the message to transmit. " + 
                    "The document has", availableSlotCount, "slots, but", neededSlotCount, "are required")
            exit()

        # Encode the message
        encoded = plainMsg.encode(myset)

        print("Done")


        # Upload the message to the document
        print("Uploading the message...    ", end="")
        sys.stdout.flush()

        encoded.sendToDoc(gdoc)

        print("Done")


        # Success
        print("\nThe message has been successfully uploaded")

    elif args.direction == "r":
        # Create an encoded message by reading the document
        print("Reading the message...      ", end="")
        sys.stdout.flush()

        encoded = EncodedMessage.fromGoogleDoc(gdoc)

        print("Done")


        # Decode the content of the document
        print("Decoding the message...     ", end="")
        sys.stdout.flush()

        decoded = encoded.decode(myset)
        encryptedMessage = decoded.getMessage()

        print("Done")


        # Decrypt the message
        print("Decrypting the message...   ", end="")
        sys.stdout.flush()

        pgp = PGP()
        pgp.addPrivateKey(args.rsaKeyFile)

        plainText = pgp.decrypt(encryptedMessage)

        print("Done")


        # Write the message to the output file
        print("Writing the output file...  ", end="")
        sys.stdout.flush()

        # os.mkdir(args.file)
        decompress(plainText, args.file)

        print("Done")


        # Success
        print("\nThe message has been successfully read into the file ", args.file)
