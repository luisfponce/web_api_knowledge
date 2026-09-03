from fastapi import HTTPException, status


class ApiError(HTTPException):
    def __init__(self, *, status_code: int, code: str, detail: str) -> None:
        super().__init__(status_code=status_code, detail={"code": code, "detail": detail})


def not_found(resource: str) -> ApiError:
    return ApiError(
        status_code=status.HTTP_404_NOT_FOUND,
        code="not_found",
        detail=f"{resource} was not found.",
    )


def conflict(detail: str, code: str = "conflict") -> ApiError:
    return ApiError(status_code=status.HTTP_409_CONFLICT, code=code, detail=detail)
