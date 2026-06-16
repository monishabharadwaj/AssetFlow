class NotFoundError(Exception):
    def __init__(self, resource: str, identifier: str | None = None) -> None:
        if identifier:
            message = f"{resource} with id '{identifier}' not found"
        else:
            message = f"{resource} not found"
        self.resource = resource
        self.identifier = identifier
        super().__init__(message)


class ConflictError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class BusinessRuleError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
