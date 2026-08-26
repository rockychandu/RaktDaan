from flask import jsonify, Response
from typing import Any, Dict, Optional

class ApiResponse:
    """
    Standardized API Response Builder for enterprise REST endpoints.
    Enforces consistent JSON structure across all success and error responses.
    """

    @classmethod
    def success(
        cls,
        data: Any = None,
        message: str = "Request processed successfully.",
        status_code: int = 200,
        meta: Optional[Dict[str, Any]] = None
    ) -> Response:
        payload = {
            "success": True,
            "message": message,
            "data": data if data is not None else {}
        }
        if meta:
            payload["meta"] = meta

        return jsonify(payload), status_code

    @classmethod
    def error(
        cls,
        message: str = "An error occurred while processing request.",
        status_code: int = 400,
        errors: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None
    ) -> Response:
        payload = {
            "success": False,
            "message": message,
            "detail": errors or message
        }
        if error_code:
            payload["error_code"] = error_code

        return jsonify(payload), status_code
