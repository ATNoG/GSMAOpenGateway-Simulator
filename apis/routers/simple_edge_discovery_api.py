# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-19 12:13:53
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-27 20:35:53
# coding: utf-8

import config # noqa
from sqlalchemy.orm import Session
import logging
from typing import List  # noqa: F401
from fastapi import APIRouter, Header, Body, Path, Depends, Query
from common.apis.simple_edge_discovery_schemas import (
    MecPlatform,
    ErrorResponse,
)
from fastapi import status
from common.database import connections_factory as DBFactory
from helpers.responses_documentation.geofencing_api import (
    GeofencingResponses
)
from common.database import crud

router = APIRouter()


@router.get(
    "/mec-platforms",
    responses={
        200: {
            "model": List[MecPlatform],
            "description": "Successful reaponse, returning the closest "
            "MEC platform to the user device identified in the request header"
            },
        400: {
            "model": ErrorResponse,
            "description": "Bad Request"},
        401: {
            "model": ErrorResponse,
            "description": "Unauthorized"},
        403: {
            "model": ErrorResponse,
            "description": "Forbidden"},
        404: {
            "model": ErrorResponse,
            "description": "Subscriber Not Found"},
        405: {
            "model": ErrorResponse,
            "description": "Method Not Allowed"},
        406: {
            "model": ErrorResponse,
            "description": "Not Acceptable"},
        429: {
            "model": ErrorResponse,
            "description": "Too Many Requests"},
        500: {
            "model": ErrorResponse,
            "description": "Internal Server Error"},
        502: {
            "model": ErrorResponse,
            "description": "Bad Gateway"},
        503: {
            "model": ErrorResponse,
            "description": "Service Unavailable"},
        504: {
            "model": ErrorResponse,
            "description": "Gateway Time-Out"},
    },
    tags=["Discovery"],
    summary="Returns the name of the MEC platform closest to user device "
    "identified in the request.",
    response_model_by_alias=True,
)
async def get_mecplatforms(
    filter: str = Query(
        None,
        description="filter the MEC Platforms according to the parameter "
        "value. For this API the only supported value is &#x60;closest&#x60;"
    ),
    ip_address: str = Header(
        None,
        description="The public IP allocated to the device."
    ),
    network_access_identifier: str = Header(
        None,
        description="3GPP network access identifier for the subscription "
        "being used by the device"
    ),
    phone_number: str = Header(
        None,
        description="MSISDN in E.164 format (starting with country code) "
        "of the mobile subscription being used by the device. Optionally "
        "prefixed with &#39;+&#39;.", regex=r"/^\+?[0-9]{5,15}$/"
        ),
) -> List[MecPlatform]:
    return []
