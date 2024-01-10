# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2024-01-08 10:23:10
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2024-01-10 11:19:06
# coding: utf-8

from typing import List  # noqa: F401
from fastapi import APIRouter, Body, Path, Depends, Header
from sqlalchemy.orm import Session
import json
import config # noqa
import logging # noqa
from common.database import connections_factory as DBFactory
from common.database import crud
from common.helpers import device_status as DeviceStatusHelper
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
    simulation_id: int = Header(),
    request_connectivity_status: RequestConnectivityStatus = Body(),
    db: Session = Depends(DBFactory.get_db_session)

) -> ConnectivityStatusResponse:

    # We can only retrieve connectivity status if the simulation is active
    if not crud.simulation_is_running(db=db, simulation_id=simulation_id):
        logging.info(
            "Impossible to retrieve locations for Simulation " +
            f"{simulation_id}. This Simulation is not running. It must be " +
            "started first."
        )
        return DeviceStatusHelper.error_message_simulation_not_running()

    simulation_instance = crud\
        .get_last_simulation_instance_from_root_simulation(
            db=db,
            root_simulation_id=simulation_id
        )

    # Get the Simulated UE ID
    simulated_ue_instance = crud\
        .get_simulated_device_instance_from_root_simulation(
            db=db,
            root_simulation_id=simulation_id,
            device=request_connectivity_status.device
        )

    if not simulated_ue_instance:
        return DeviceStatusHelper.error_message_unknown_device()

    device_status_simulation_data = crud.get_last_device_status_entry(
        db=db,
        simulation_instance=simulation_instance.id,
        ue_id=simulated_ue_instance.id
    )

    return ConnectivityStatusResponse(
        connectivity_status=DeviceStatusHelper
        .get_connectivity_enum_from_value(
            device_status_simulation_data.connectivity_status
        )
    )


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
    simulation_id: int = Header(),
    request_roaming_status: RequestRoamingStatus = Body(),
    db: Session = Depends(DBFactory.get_db_session)
) -> RoamingStatusResponse:

    # We can only retrieve connectivity status if the simulation is active
    if not crud.simulation_is_running(db=db, simulation_id=simulation_id):
        logging.info(
            "Impossible to retrieve locations for Simulation " +
            f"{simulation_id}. This Simulation is not running. It must be " +
            "started first."
        )
        return DeviceStatusHelper.error_message_simulation_not_running()

    simulation_instance = crud\
        .get_last_simulation_instance_from_root_simulation(
            db=db,
            root_simulation_id=simulation_id
        )

    # Get the Simulated UE ID
    simulated_ue_instance = crud\
        .get_simulated_device_instance_from_root_simulation(
            db=db,
            root_simulation_id=simulation_id,
            device=request_roaming_status.device
        )

    if not simulated_ue_instance:
        return DeviceStatusHelper.error_message_unknown_device()

    device_status_simulation_data = crud.get_last_device_status_entry(
        db=db,
        simulation_instance=simulation_instance.id,
        ue_id=simulated_ue_instance.id
    )

    return RoamingStatusResponse(
        roaming=device_status_simulation_data.roaming,
        country_code=device_status_simulation_data.country_code,
        country_name=json.loads(device_status_simulation_data.country_name)
    )


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
):  # -> SubscriptionInfo:
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
        description="Subscription identifier that was obtained from the "
        "create event subscription operation"
    ),
):  # -> SubscriptionAsync:
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
        description="Subscription identifier that was obtained from the "
        "create subscription operation"
    )
):  # -> SubscriptionInfo:
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
):  # -> List[SubscriptionInfo]:
    """Retrieve a list of device status event subscription(s)"""
    return