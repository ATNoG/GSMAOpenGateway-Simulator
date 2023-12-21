# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-14 19:47:52
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-19 11:55:36

# flake8: noqa
import config #noqa
from common.apis.device_location_schemas import (
    Location,
    ErrorInfo,
)


class LocationRetrievalResponses:
    
    POST_RETRIEVE = {
        200: {
            "model": Location,
            "description": "Location retrieval result",
            "content": {
                "application/json": {
                    "examples": {
                        "LOCATION_CIRCLE": {
                            "lastLocationTime": "2023-10-17T13:18:23.682Z",
                            "area": {
                                "areaType": "circle",
                                "center": {
                                    "latitude": 45.754114,
                                    "longitude": 4.860374
                                },
                                "radius": 800
                            }
                        }
                    }
                }
            }
        },
        400: {
                "model": ErrorInfo,
                "description": "Problem with the client " +
                "request. In addition to regular scenario of " +
                "`INVALID_ARGUMENT`, another scenarios may exist: " +
                "\n- maxAge threshold cannot be satisfied",
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
            "\n\nImpossible to retrieve locations for Simulation. This " +
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