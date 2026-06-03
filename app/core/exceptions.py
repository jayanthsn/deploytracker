class AppException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details=None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class DeploymentNotFound(AppException):
    def __init__(self):
        super().__init__(
            code="DEPLOYMENT_NOT_FOUND",
            message="The requested deployment does not exist.",
            status_code=404,
        )
