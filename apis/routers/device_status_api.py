# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2024-01-08 10:23:10
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2024-01-08 10:31:08
# coding: utf-8

from typing import List  # noqa: F401
from fastapi import APIRouter, Body, Path
import config # noqa
import logging # noqa
from common.apis.device_status_schemas import (
    ConnectivityStatusResponse,
    ErrorInfo,
    RequestConnectivityStatus,
    RoamingStatusResponse,
    RequestRoamingStatus,
    SubscriptionInfo,
    SubscriptionAsync,
    CreateSubscription
)

router = APIRouter()


@router.post(
    "/connectivity",
    responses={
        200: {
            "model": ConnectivityStatusResponse, 
            "description": "Contains information about current "
            "connectivity status"
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
        500: {
            "model": ErrorInfo,
            "description": "Server error"
        },
        503: {
            "model": ErrorInfo,
            "description": "Service unavailable. Typically the server is down."
        },
    },
    tags=["Device connectivity status"],
    summary="Get the current connectivity status information",
    response_model_by_alias=True,
)
async def get_connectivity_status(
    request_connectivity_status: RequestConnectivityStatus = Body(
        None, description=""
    ),

) -> ConnectivityStatusResponse:
    """Get the current connectivity status information"""
    return 


@router.post(
    "/roaming",
    responses={
        200: {
            "model": RoamingStatusResponse,
            "description": "Contains information about current roaming status"
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
        500: {
            "model": ErrorInfo,
            "description": "Server error"
        },
        503: {
            "model": ErrorInfo,
            "description": "Service unavailable. Typically the server is down."
        },
    },
    tags=["Device roaming status"],
    summary="Get the current roaming status and the country information",
    response_model_by_alias=True,
)
async def get_roaming_status(
    request_roaming_status: RequestRoamingStatus = Body(None, description=""),
) -> RoamingStatusResponse:
    """Get the current roaming status and the country information"""
    return


@router.post(
    "/subscriptions",
    responses={
        201: {
            "model": SubscriptionInfo,
            "description": "Created"
        },
        202: {
            "model": SubscriptionAsync,
            "description": "Request accepted to be processed. It applies "
            "for async creation process."
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
            "description": "Service unavailable. Typically the server is down."
        },
    },
    tags=["Device status subscription"],
    summary="Create a device status event subscription for a device",
    response_model_by_alias=True,
)
async def create_device_status_subscription(
    create_subscription: CreateSubscription = Body(None, description=""),
) -> SubscriptionInfo:
    """Create a device status event subscription for a device"""
    return


@router.delete(
    "/subscriptions/{subscriptionId}",
    responses={
        204: {
            "description": "event subscription deleted"
        },
        202: {
            "model": SubscriptionAsync,
            "description": "Request accepted to be processed. It applies "
            "for async deletion process."
        },
        400: {
            "model": ErrorInfo,
            "description": "Invalid input"
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
        500: {
            "model": ErrorInfo,
            "description": "Server error"
        },
        503: {
            "model": ErrorInfo,
            "description": "Service unavailable. Typically the server is down."
        },
    },
    tags=["Device status subscription"],
    summary="Delete a device status event subscription for a device",
    response_model_by_alias=True,
)
async def delete_subscription(
    subscriptionId: str = Path(
        None,
        description="Subscription identifier that was obtained from the "
        "create event subscription operation"
    ),
) -> SubscriptionAsync:
    """delete a  given event subscription."""
    return 


@router.get(
    "/subscriptions/{subscriptionId}",
    responses={
        200: {
            "model": SubscriptionInfo,
            "description": "OK"
        },
        400: {
            "model": ErrorInfo,
            "description": "Invalid input"
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
        500: {
            "model": ErrorInfo,
            "description": "Server error"
        },
        503: {
            "model": ErrorInfo,
            "description": "Service unavailable. Typically the server is down."
        },
    },
    tags=["Device status subscription"],
    summary="Retrieve a device status event subscription for a device",
    response_model_by_alias=True,
)
async def retrieve_subscription(
    subscriptionId: str = Path(
        None,
        description="Subscription identifier that was obtained from the "
        "create subscription operation"
    )
) -> SubscriptionInfo:
    """retrieve event subscription information for a given subscription."""
    return 


@router.get(
    "/subscriptions",
    responses={
        200: {
            "model": List[SubscriptionInfo],
            "description": "List of event subscription details"
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
        500: {
            "model": ErrorInfo,
            "description": "Server error"
        },
        503: {
            "model": ErrorInfo,
            "description": "Service unavailable. Typically the server is down."
        },
    },
    tags=["Device status subscription"],
    summary="Retrieve a list of device status event subscription",
    response_model_by_alias=True,
)
async def retrieve_subscription_list(
) -> List[SubscriptionInfo]:
    """Retrieve a list of device status event subscription(s)"""
    return