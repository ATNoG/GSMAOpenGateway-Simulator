# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-27 11:15:07
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-27 11:38:07
# coding: utf-8

from datetime import datetime
from fastapi import APIRouter, Body
import config # noqa
from common.apis.sim_swap_schemas import (
    CheckSimSwapInfo,
    CreateCheckSimSwap,
    SimSwapInfo,
    ErrorInfo,
    CreateSimSwapDate
)

router = APIRouter()


@router.post(
    "/check",
    responses={
        200: {"model": CheckSimSwapInfo,
              "description":
                  "Returns whether a SIM swap has been performed "
                  "during a past period"},
        400: {
            "model": ErrorInfo,
            "description": "Problem with the client request"
        },
        401: {
            "model": ErrorInfo,
            "description": "Authentication problem with the client request"
        },
        403: {
            "model": ErrorInfo,
            "description": "Client does not have sufficient permission"
        },
        404: {
            "model": ErrorInfo,
            "description": "Resource Not Found"
        },
        409: {
            "model": ErrorInfo,
            "description": "Conflict"
        },
        500: {
            "model": ErrorInfo,
            "description": "Server error"
        },
        503: {
            "model": ErrorInfo,
            "description": "Service unavailable. Typically the server is down"
        },
        504: {
            "model": ErrorInfo,
            "description": "Request time exceeded. If it happens "
            "repeatedly, consider reducing the request complexity"
        },
    },
    tags=["Check SIM swap"],
    response_model_by_alias=True,
)
async def check_sim_swap(
    create_check_sim_swap: CreateCheckSimSwap = Body(
        None,
        description="Create a check SIM swap request for a MSISDN identifier. "
    ),
) -> CheckSimSwapInfo:
    return CheckSimSwapInfo(
        swapped=True
    )


@router.post(
    "/retrieve-date",
    responses={
        200: {
            "model": SimSwapInfo,
            "description": "Contains information about SIM swap change"
        },
        400: {
            "model": ErrorInfo,
            "description": "Problem with the client request"
        },
        401: {
            "model": ErrorInfo,
            "description": "Authentication problem with the client request"
        },
        403: {
            "model": ErrorInfo,
            "description": "Client does not have sufficient permission"
        },
        404: {
            "model": ErrorInfo,
            "description": "Resource Not Found"
        },
        409: {
            "model": ErrorInfo,
            "description": "Conflict"
        },
        500: {
            "model": ErrorInfo,
            "description": "Server error"
        },
        503: {
            "model": ErrorInfo,
            "description": "Service unavailable. Typically the server is down"
        },
        504: {
            "model": ErrorInfo,
            "description": "Request time exceeded. If it happens "
            "repeatedly, consider reducing the request complexity"
        },
    },
    tags=["Retrieve SIM swap date"],
    response_model_by_alias=True,
)
async def retrieve_sim_swap_date(
    create_sim_swap_date: CreateSimSwapDate = Body(
        None,
        description="Create a SIM swap date request for a MSISDN identifier. "
    ),

) -> SimSwapInfo:

    return SimSwapInfo(
        latest_sim_change=datetime.utcnow()
    )
