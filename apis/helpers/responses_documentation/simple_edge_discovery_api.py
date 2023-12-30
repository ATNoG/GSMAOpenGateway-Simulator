# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-14 19:47:52
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-30 20:54:34

# flake8: noqa
import config #noqa
from common.apis.simple_edge_discovery_schemas import (
    ErrorResponse,
    MecPlatform
)
from typing import List


class SimpleEdgeDiscoveryResponses:
    
    GET_MEC_PLATFORMS = {
        200: {
            "model": List[MecPlatform],
            "description": "Successful reaponse, returning the closest MEC "
            "platform to the user device identified in the request header",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/MecPlatform"
                    },
                    "example": [
                        {
                            "edgeCloudProvider": "Altice",
                            "edgeResourceName": "alb-wl1-ave-wlz-012"
                        }
                    ]
                }
            }
        },
        400: {
            "model": ErrorResponse,
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponse"
                    },
                    "example": {
                        "status": 400,
                        "code": "INVALID_ARGUMENT",
                        "message": "Insufficient parameters: At least one of "
                        "Network-Access-Identifier, Phone-Number or "
                        "IP-Address must be specified, or, the API must be "
                        "called by a client on a netwok-attached device "
                        "(hence passing the source IP in the request header)"
                    }
                }
            }
        },
        404: {
            "model": ErrorResponse,
            "description": "Device Not found",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponse"
                    },
                    "example": {
                        "status": 404,
                        "code": "NOT_FOUND",
                        "message": "No device found for the specified "
                        "parameters."
                    }
                }
            }
        },
        412: {
            "model": ErrorResponse,
            "description": "**[Simulation Specific]**\n\nSimulation Not "
            "Running",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponse"
                    },
                    "example": {
                        "status": 412,
                        "code": "SIMULATION.NOT_RUNNING",
                        "message": "The simulation is not running. Thus, you "
                        "cannot get its generated data"
                    }
                }
            }
        },
    }
