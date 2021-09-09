
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import socket

SCOPES = ['https://www.googleapis.com/auth/documents','https://www.googleapis.com/auth/drive']

DOCUMENTS_BASE_FOLDER_NAME = "docs"

class GoogleDoc:
    # Attributes:
    # - credentials (object):    The result of reading a JSON credentials file
    # - content (list of dicts): List of the colors and startIndexes of all the spaces of the document

    def __init__(self, credentialsFile):
        # Parse the credentials file
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(credentialsFile, SCOPES)

        # Dinamycally calculate the ID of the document to use
        # It should be inside a folder called "docs" (DOCUMENTS_BASE_FOLDER_NAME)
        # The folder "docs" should only contain one file. If more than one file exists, the first
        # one listed will be used
        folderId = __getDocumentsFolderFromDrive__(DOCUMENTS_BASE_FOLDER_NAME, self.credentials)
        self.documentId = __getDocumentsFromDrive__(folderId, self.credentials)[0]["id"]

        # Read and parse the document content
        docContent = __getDocumentContent__(self.documentId, self.credentials)
        self.content = __parseDocumentContent__(docContent)

    # Returns the number of spaces in the document that can be used to hide information
    def getAvailableSpaceCount(self):
        return len(self.content)

    # Pushes a list of actions to the document in a single API call (one request)
    def commit(self, setElemList):
        i = 0
        updatesRequest = { "requests": [] }
        for elem in setElemList:
            if len(updatesRequest["requests"]) >= 50000:
                __updateDocumentContent__(self.documentId, updatesRequest, self.credentials)
                updatesRequest["requests"] = []

            updatesRequest["requests"].append(
                {
                    "updateTextStyle": {
                    "range": {
                      "startIndex": self.content[i]["startIndex"],
                      "endIndex":   self.content[i]["startIndex"]+1
                    },
                    "textStyle": {
                      "foregroundColor": {
                        "color": {
                          "rgbColor": {
                            "red":   elem.color[0]/255,
                            "green": elem.color[1]/255,
                            "blue":  elem.color[2]/255
                          }
                        }
                      }
                    },
                    "fields": "foregroundColor"
                    }
                }
            )
            i += 1

        retval = __updateDocumentContent__(self.documentId, updatesRequest, self.credentials)


################################### AUX FUNCTIONS ###################################
   
# Returns the text and the stype of the given ParagraphElement
# Args:
#   element: a ParagraphElement from a Google Doc
def read_paragraph_element(element):
    text_run = element.get('textRun')
    if not text_run:
        return ''
    return text_run.get('content'),text_run.get('textStyle')

# Recurses through a list of Structural Elements to read a document's
# text where text may be in nested elements
# Args:
#    elements: a list of Structural Elements.
def __parseDocumentContent__(documentContent):
    output = []

    # Iterate over each of the "document sections" in the JSON
    for value in documentContent:
        if not 'paragraph' in value:
            continue

        paragraphElements = value.get('paragraph').get('elements')
        for elem in paragraphElements:
            # Extract the paragraph content and style
            content,style = read_paragraph_element(elem)

            # If the text fragment does not contain a space it can be ignored
            if " " not in content:
                continue

            # Get all the spaces in the text fragment
            spaceOffsets = [i for i, c in enumerate(content) if c == " "]

            # Calculate the start index of the space
            startIndex = elem.get("startIndex")
            
            # Calculate the color of the space
            color = []
            if not style:
                # When the default color is used, it is not included in the respponse
                color = [0,0,0]
            else:
                # Extract the color from the element
                rawColor = style.get('foregroundColor').get('color').get('rgbColor')
                for colorName in ["red", "green", "blue"]:
                    colorValue = rawColor.get(colorName) if colorName in rawColor else 0
                    color.append(round(colorValue * 255))

            # For each space, append it to the final list of spaces
            for spaceOffset in spaceOffsets:
                spaceIndex = startIndex + spaceOffset

                output.append({
                    "startIndex": spaceIndex,
                    "color": color
                    })

    return output

################################### API FUNCTIONS ###################################

# Finds and returns a folder named after tha value of "folderName"
def __getDocumentsFolderFromDrive__(folderName, credentials):
    service_drive = build('drive', 'v3', credentials=credentials)
    results = service_drive.files().list(fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])


    folders = [elem["id"] for elem in items if elem["name"] == folderName]

    return folders[0] if folders else None

# Gets all the documents inside a folder
def __getDocumentsFromDrive__(folderId, credentials):
    service_drive = build('drive', 'v3', credentials=credentials)
    results = service_drive.files().list(
        pageSize=1, fields="nextPageToken, files(id, name)", q="'" + folderId + "' in parents").execute()

    items = results.get('files', [])

    return items if items else None

# Gets all the contents from a document
def __getDocumentContent__(documentId, credentials):
    # Change the default socket timeout
    socket.setdefaulttimeout(300)

    service_docs = build('docs', 'v1', credentials=credentials)
    document = service_docs.documents().get(documentId=documentId).execute()

    return document.get('body').get('content')
        
# Pushes changes to a document
def __updateDocumentContent__(documentId, updateRequest, credentials):
    # Change the default socket timeout
    socket.setdefaulttimeout(300)

    service_docs = build('docs', 'v1', credentials=credentials)
    result = service_docs.documents().batchUpdate(
            documentId=documentId, body=updateRequest).execute()

    return result
