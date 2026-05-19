class SHLAssessmentException(Exception):
    """Base exception for the SHL Assessment Recommender application"""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AgentException(SHLAssessmentException):
    """Exception raised during Conversational Agent execution"""
    def __init__(self, message: str):
        super().__init__(message, status_code=502)


class CatalogException(SHLAssessmentException):
    """Exception raised for catalog validation or querying errors"""
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class DatabaseException(SHLAssessmentException):
    """Exception raised during SQL database operations"""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class ValidationException(SHLAssessmentException):
    """Exception raised for invalid inputs or turn length violations"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class TimeoutException(SHLAssessmentException):
    """Exception raised when an API or agent operations exceeds allowed timelines"""
    def __init__(self, message: str):
        super().__init__(message, status_code=504)
