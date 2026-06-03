class AppException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details=None):
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


class InvalidDeploymentData(AppException):
    def __init__(self, detail: str):
        super().__init__(
            code="INVALID_DEPLOYMENT_DATA",
            message=f"Invalid deployment data: {detail}",
            status_code=422,
        )
