# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-14 19:47:52
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2024-01-11 19:23:29

# flake8: noqa
from typing import List  # noqa: F401
import config #noqa
from common.apis.device_status_schemas import (
    Device,
    ErrorInfo,
    RoamingStatusResponse,
    SubscriptionInfo,
    SubscriptionAsync
)


class DeviceStatusResponses:
    
    POST_CONNECTIVITY = {
        200: {
            "model": Device,
            "description": "Get the current connectivity status information",
            "content": {
                "application/json": {
                    "examples": {
                        
                        "Connected-With-SMS": {
                            "value": {
                                "connectivityStatus": "CONNECTED_SMS"
                            }
                        },
                        "Connected-With-DATA": {
                            "value": {
                                "connectivityStatus": "CONNECTED_DATA"
                            }
                        },
                        "Not-Connected": {
                            "value": {
                                "connectivityStatus": "NOT_CONNECTED"
                            }
                        }
                    }
                }
            }
        },
        400: {
                "model": ErrorInfo,
                "description": "Problem with the client " +
                "request.",
                "content": {
                    "application/json": {
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
                "description": "Resource Not Found",
                "content": {
                    "application/json": {
                       "example": {
                            "status": 404,
                            "code": "NOT_FOUND",
                            "message": "The specified resource is not found."
                        }
                    }
                }
             },
        412: {
            "model": Device,
            "description": "`[SIMULATION-SPECIFIC]`" +
            "\n\nImpossible to retrieve locations for Simulation. This " +
            "Simulation is not running. It must be started first.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 412,
                        "code": "SIMULATION.NOT_RUNNING",
                        "message": "The simulation is not running. Thus, " +
                        "you cannot get its generated data"
                    }
                }
            }
        }
    }
    
    
    POST_ROAMING = {
        200: {
            "model": RoamingStatusResponse,
            "description": "Contains information about current roaming status",
            "content": {
                "application/json": {
                    "examples": {
                        "No-Country-Name": {
                            "value": {
                                "roaming": True,
                                "countryCode": 901,
                                "countryName": []
                            }
                        },
                        "Single-Country-Name": {
                            "value": {
                                "roaming": True,
                                "countryCode": 901,
                                "countryName": [
                                    "DE"
                                ]
                            }
                        },
                        "Multiple-Country-Name": {
                            "value": {
                                "roaming": True,
                                "countryCode": 901,
                                "countryName": [
                                    "BL",
                                    "GF",
                                    "GP",
                                    "MF",
                                    "MQ"
                                ]
                            }
                        }
                    }
                }
            }
        },
        400: {
                "model": ErrorInfo,
                "description": "Problem with the client " +
                "request.",
                "content": {
                    "application/json": {
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
                "description": "Resource Not Found",
                "content": {
                    "application/json": {
                       "example": {
                            "status": 404,
                            "code": "NOT_FOUND",
                            "message": "The specified resource is not found."
                        }
                    }
                }
             },
        412: {
            "model": Device,
            "description": "`[SIMULATION-SPECIFIC]`" +
            "\n\nImpossible to retrieve locations for Simulation. This " +
            "Simulation is not running. It must be started first.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 412,
                        "code": "SIMULATION.NOT_RUNNING",
                        "message": "The simulation is not running. Thus, " +
                        "you cannot get its generated data"
                    }
                }
            }
        }
    }
    
    
    POST_SUBSCRIPTION = {
        201: {
            "model": SubscriptionInfo,
            "description": "Create a device status event subscription for "
            "a device",
            
        },
        400: {
                "model": ErrorInfo,
                "description": "Problem with the client " +
                "request.",
                "content": {
                    "application/json": {
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
                "description": "Resource Not Found",
                "content": {
                    "application/json": {
                       "example": {
                            "status": 404,
                            "code": "NOT_FOUND",
                            "message": "The specified resource is not found."
                        }
                    }
                }
             },
        412: {
            "model": Device,
            "description": "`[SIMULATION-SPECIFIC]`" +
            "\n\nImpossible to retrieve locations for Simulation. This " +
            "Simulation is not running. It must be started first.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 412,
                        "code": "SIMULATION.NOT_RUNNING",
                        "message": "The simulation is not running. Thus, " +
                        "you cannot get its generated data"
                    }
                }
            }
        }
    }
    
    
    GET_SUBSCRIPTIONS = {
        200: {
            "model":  List[SubscriptionInfo],
            "description": "List of event subscription details",
            
        },
        400: {
                "model": ErrorInfo,
                "description": "Problem with the client " +
                "request.",
                "content": {
                    "application/json": {
                       "example": {
                            "status": 400,
                            "code": "INVALID_ARGUMENT",
                            "message": "Client specified an invalid argument, "
                            "request body or query param"
                        }
                    }
                }
             },
        412: {
            "model": Device,
            "description": "`[SIMULATION-SPECIFIC]`" +
            "\n\nImpossible to retrieve locations for Simulation. This " +
            "Simulation is not running. It must be started first.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 412,
                        "code": "SIMULATION.NOT_RUNNING",
                        "message": "The simulation is not running. Thus, " +
                        "you cannot get its generated data"
                    }
                }
            }
        }
    }
    
    GET_SUBSCRIPTION = {
        200: {
            "model":  SubscriptionInfo,
            "description": "OK",
            
        },
        400: {
                "model": ErrorInfo,
                "description": "Problem with the client " +
                "request.",
                "content": {
                    "application/json": {
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
                "description": "Resource Not Found",
                "content": {
                    "application/json": {
                       "example": {
                            "status": 404,
                            "code": "NOT_FOUND",
                            "message": "The specified resource is not found."
                        }
                    }
                }
        },
        412: {
            "model": Device,
            "description": "`[SIMULATION-SPECIFIC]`" +
            "\n\nImpossible to retrieve locations for Simulation. This " +
            "Simulation is not running. It must be started first.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 412,
                        "code": "SIMULATION.NOT_RUNNING",
                        "message": "The simulation is not running. Thus, " +
                        "you cannot get its generated data"
                    }
                }
            }
        }
    }
    
    DELETE_SUBSCRIPTION = {
        202: {
            "model":  SubscriptionAsync,
            "description": "Request accepted to be processed. It applies "
            "for async deletion process."
            
        },
        400: {
                "model": ErrorInfo,
                "description": "Invalid input",
                "content": {
                    "application/json": {
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
                "description": "Resource Not Found",
                "content": {
                    "application/json": {
                       "example": {
                            "status": 404,
                            "code": "NOT_FOUND",
                            "message": "The specified resource is not found."
                        }
                    }
                }
            },
        412: {
            "model": Device,
            "description": "`[SIMULATION-SPECIFIC]`" +
            "\n\nImpossible to retrieve locations for Simulation. This " +
            "Simulation is not running. It must be started first.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 412,
                        "code": "SIMULATION.NOT_RUNNING",
                        "message": "The simulation is not running. Thus, " +
                        "you cannot get its generated data"
                    }
                }
            }
        }
    }