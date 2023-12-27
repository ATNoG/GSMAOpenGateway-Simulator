# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-14 19:47:52
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-27 17:26:14

# flake8: noqa
import config #noqa
from common.apis.sim_swap_schemas import (
    CheckSimSwapInfo,
    SimSwapInfo,
    ErrorInfo,
)
from typing import List


class SIMSwapResponses:
    
    CHECK = {
        200: {
            "model": CheckSimSwapInfo,
            "description": "Returns whether a SIM swap has been performed "
            "during a past period",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/CheckSimSwapInfo"
                    },
                    "example": {
                        "swapped": True
                    }
                }
            }
        },
        400: {
            "model": ErrorInfo,
            "description": "Problem with the client request",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorInfo"
                    },
                    "example": {
                        "status": 400,
                        "code": "INVALID_ARGUMENT",
                        "message": "Client specified an invalid argument, "
                        "request body or query param"
                    }
                }
            }
        },
        404: {
            "model": ErrorInfo,
            "description": "Not found",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorInfo"
                    },
                    "example": {
                        "status": 404,
                        "code": "SIM_SWAP.UNKNOWN_PHONE_NUMBER",
                        "message": "SIM Swap can't be checked because the "
                        "phone number is unknown."
                    }
                }
            }
        },
    }

    RETRIEVE_DATE = {
        200: {
            "model": SimSwapInfo,
            "description": "Contains information about SIM swap change",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/SimSwapInfo"
                    },
                    "example": {
                        "latestSimChange": "2023-12-27T17:23:43.558Z"
                    }
                }
            }
        },
        400: {
            "model": ErrorInfo,
            "description": "Problem with the client request",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorInfo"
                    },
                    "example": {
                        "status": 400,
                        "code": "INVALID_ARGUMENT",
                        "message": "Client specified an invalid argument, "
                        "request body or query param"
                    }
                }
            }
        },
        404: {
            "model": ErrorInfo,
            "description": "Not found",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorInfo"
                    },
                    "example": {
                        "status": 404,
                        "code": "SIM_SWAP.UNKNOWN_PHONE_NUMBER",
                        "message": "SIM Swap can't be checked because the "
                        "phone number is unknown."
                    }
                }
            }
        },
    }