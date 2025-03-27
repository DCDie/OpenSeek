class OpenSeekException(BaseException):
    pass


class MissingCredentials(OpenSeekException):
    pass


class InvalidCredentials(OpenSeekException):
    pass


class ServerDown(OpenSeekException):
    pass


class MissingInitialization(OpenSeekException):
    pass
