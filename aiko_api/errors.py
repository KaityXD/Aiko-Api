class AikoException(Exception):
    """Base exception for aiko_api."""
    pass

class HTTPException(AikoException):
    """Exception that's raised when an HTTP request operation fails."""
    def __init__(self, response, message):
        self.response = response
        self.status = response.status_code
        self.message = message
        super().__init__(f"{self.status} {self.message}")

class Forbidden(HTTPException):
    """Exception that's raised for a 403 status code."""
    pass

class NotFound(HTTPException):
    """Exception that's raised for a 404 status code."""
    pass

class DiscordServerError(HTTPException):
    """Exception that's raised for a 500 range status code."""
    pass

class LoginFailure(AikoException):
    """Exception that's raised when the token is invalid."""
    pass
