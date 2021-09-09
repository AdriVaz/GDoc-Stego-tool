# GDoc Stego Tool

This steganography tool is able to hide a file inside a Google Document, encoding it in the colors of the space characters in the document.

The tool also allows to read a previously stored message.

Before uploading it, the tool encrypts the file using an RSA key pair and an AES session key, using a sheme similar to PGP, providing security to the message.


## Requirements

The required Python packages are listed in the `requirements.txt`file. To install then, just run
```
pip install -r requirements.txt
```

## Launch

To easily launch the tool, a "launch.sh" script is provided. It contains some sample invocations, as well as a list of the arguments accepted by the program (running it with -h shows more complete information)

## API Keys

In order to access the Google account that contains the document used to store the messages, an API Key is needed. The file `secret_service_account.json` is an example of the file needed. You may also need to use a client account in your project, depending on the security settings imposed by Google at the time.

The `public.pem` and `private.pem` are not related to the Google authentication. They are used by the tool's encryption process, that happens before any information leaves the computer.

## Limitations

The tool has some important limitations, some of them are listed below
- The Google Document has to be long enough to hold the complete message. As the tool uses the color of the spaces to store information, and each color is encoded using 3 Bytes, the amount of spaces that the document must have is calculated dividing the size of the file by 3. The tool will do this verifications before doing anything to avoid missing information.
- The performance of the tool is reduced notably when big files are used (bigger than 1MB)
- The information encoded in the document is not deleted after it is read. When a new message is written, the old message is not "set to 0" first, so the performance of the tool is degradated after big files are uploaded, even after they are overwritten with a smaller file.

## Attribution

The design of the algorithm and the implementation was made by:
- Edgar Loyola
- Jaime Guardiola
- Tarek Mellouk
- Me (Adrian Vazquez)
