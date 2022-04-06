import string

class FileKeyStore():
    def __init__(self, filePath: string) -> None:
        super().__init__()
        self.__readKeyFromFile(filePath)

    def __readKeyFromFile(self, filePath: string):
        try:
            with open(filePath) as keyFile:
                lines = keyFile.readlines()
                self.__api_key = lines[0].strip()
                self.__api_secret = lines[1].strip()
        except Exception as e:
            print("api_key FileRead error: ", e)

    def getAPIKey(self) -> string:
        return self.__api_key

    def getAPISecretKey(self) -> string:
        return self.__api_secret