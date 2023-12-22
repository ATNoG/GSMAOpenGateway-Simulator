# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-14 19:47:52
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-22 22:25:06

# flake8: noqa
import config #noqa
from common.apis.device_location_schemas import (
    SubscriptionInfo,
    ErrorInfo,
)
from typing import List


class GeofencingResponses:
    
    POST_GEOFENCE_SUBSCRIPTION = {
        201: {
            "model": SubscriptionInfo,
            "description": "Created (Successful creation of subscription)",
        },
        400: {
            "model": ErrorInfo,
            "description": "Invalid argument",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorInfo"
                    },
                    "example": {
                        "value": {
                            "status": 400,
                            "code": "INVALID_ARGUMENT",
                            "message": "Invalid input"
                        }
                    }
                }
            }
        },
    }
    
    GET_GEOFENCE_SUBSCRIPTIONS = {
        200: {
            "model": List[SubscriptionInfo],
            "description": "The list of subscriptions is retrieved.",
        },
        400: {
            "model": ErrorInfo,
            "description": "Invalid argument",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorInfo"
                    },
                    "example": {
                        "value": {
                            "status": 400,
                            "code": "INVALID_ARGUMENT",
                            "message": "Invalid input"
                        }
                    }
                }
            }
        },
    }
    
    GET_GEOFENCE_SUBSCRIPTION = {
        200: {
            "model": SubscriptionInfo,
            "description": "The list of subscriptions is retrieved.",
        },
        400: {
            "model": ErrorInfo,
            "description": "Invalid argument",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorInfo"
                    },
                    "example": {
                        "value": {
                            "status": 400,
                            "code": "INVALID_ARGUMENT",
                            "message": "Invalid input"
                        }
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
                        "value": {
                            "status": 400,
                            "code": "NOT_FOUND",
                            "message": "The specified resource is not found"
                        }
                    }
                }
            }
        },
    }

    DELETE_GEOFENCE_SUBSCRIPTION = {
        204: {
            "description": "Event subscription deleted",
            "content": {
                "application/json": {
                    "example": None
                }
            }
        },
        400: {
            "model": ErrorInfo,
            "description": "Invalid argument",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorInfo"
                    },
                    "example": {
                        "value": {
                            "status": 400,
                            "code": "INVALID_ARGUMENT",
                            "message": "Invalid input"
                        }
                    }
                }
            }
        },
    }