# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-14 19:47:52
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-19 11:56:20

# flake8: noqa

from common.apis.device_location_schemas import (
    VerifyLocationResponse,
    ErrorInfo,
)


class LocationVerificationResponses:
    
    POST_VERIFY = {
        200: {
            "model": VerifyLocationResponse,
            "description": "Location retrieval result",
            "content": {
                "application/json": {
                    "examples": {
                        "Match": {
                            "lastLocationTime": "2023-10-17T13:18:23.682Z",
                            "verificationResult": "TRUE"
                        },
                        "No match": {
                            "lastLocationTime": "2023-10-17T13:18:23.682Z",
                            "verificationResult": "FALSE"
                        },
                        "Unknown": {
                            "lastLocationTime": "2023-10-17T13:18:23.682Z",
                            "verificationResult": "PARTIAL",
                            "matchRate": 74
                        },
                        
                    }
                }
            }
        },
        400: {
                "model": ErrorInfo,
                "description": "Invalid input",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/ErrorInfo"
                        },
                        "examples": {
                            "InvalidArgument": {
                                "value": {
                                    "status": 400,
                                    "code": "INVALID_ARGUMENT",
                                    "message": "Invalid input"
                                }
                            },
                            "MaxAgeIssue": {
                                "value": {
                                    "status": 400,
                                    "code": "LOCATION_RETRIEVAL." +
                                    "MAXAGE_INVALID_ARGUMENT",
                                    "message": "maxAge threshold cannot " +
                                    "be satisfied"
                                }
                            }
                        }
                    }
                }
             },
        410: {
            "model": ErrorInfo,
            "description": "`[SIMULATION-SPECIFIC]`" +
            "\n\nImpossible to verify locations for Simulation. This " +
            "Simulation is not running. It must be started first.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 410,
                        "code": "SIMULATION.NOT_RUNNING",
                        "message": "The simulation is not running. Thus, " +
                        "you cannot get its generated data"
                    }
                }
            }
        }
    }