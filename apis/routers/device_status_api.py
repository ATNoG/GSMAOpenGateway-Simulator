# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2024-01-08 10:23:10
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2024-01-11 19:24:36
# coding: utf-8

from typing import List  # noqa: F401
from fastapi import APIRouter, Body, Path, Depends, Header, status
from sqlalchemy.orm import Session
import json
import config # noqa
import logging # noqa
from common.database import connections_factory as DBFactory
from common.database import crud
from common.helpers import device_status as DeviceStatusHelper
from common.apis.device_status_schemas import (
    ConnectivityStatusResponse,
    RequestConnectivityStatus,
    RoamingStatusResponse,
    RequestRoamingStatus,
    SubscriptionInfo,
    SubscriptionAsync,
    CreateSubscription
)
from helpers.responses_documentation.device_status_api import (
    DeviceStatusResponses
)
from fastapi.responses import Response

router = APIRouter()


@router.post(
    "/connectivity",
    responses=DeviceStatusResponses.POST_CONNECTIVITY,
    tags=["Device connectivity status"],
    summary="Get the current connectivity status information",
    response_model_by_alias=True,
    status_code=201
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
    responses=DeviceStatusResponses.POST_ROAMING,
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
    responses=DeviceStatusResponses.POST_SUBSCRIPTION,
    tags=["Device status subscription"],
    summary="Create a device status event subscription for a device",
    response_model_by_alias=True,
    status_code=201
)
async def create_device_status_subscription(
    simulation_id: int = Header(),
    create_subscription: CreateSubscription = Body(),
    db: Session = Depends(DBFactory.get_db_session)
):

    # Get the Simulated UE ID
    simulated_ue = crud.get_simulated_device_from_root_simulation(
        db=db,
        root_simulation_id=simulation_id,
        device=create_subscription.subscription_detail.device
    )

    # Store subscription in database
    created_subscription = crud.create_device_status_subscription(
        db=db,
        root_simulation_id=simulation_id,
        ue_id=simulated_ue.id,
        subscription=create_subscription
    )

    # Return
    subscription_info = SubscriptionInfo(
        webhook=create_subscription.webhook,
        subscription_detail=create_subscription.subscription_detail,
        subscription_expire_time=created_subscription.expire_time,
        subscription_id=created_subscription.id,
        starts_at=created_subscription.start_time,
        expires_at=created_subscription.expire_time
    )

    return Response(
        status_code=status.HTTP_201_CREATED,
        content=subscription_info.model_dump_json(),
        media_type="application/json"
    )


@router.delete(
    "/subscriptions/{subscription_id}",
    responses=DeviceStatusResponses.DELETE_SUBSCRIPTION,
    tags=["Device status subscription"],
    summary="Delete a device status event subscription for a device",
    response_model_by_alias=True,
    status_code=202
)
async def delete_subscription(
    simulation_id: int = Header(),
    subscription_id: str = Path(
        description="Subscription identifier that was obtained from the "
        "create event subscription operation"
    ),
    db: Session = Depends(DBFactory.get_db_session)
):

    # Get subscription from database
    subscription_from_db = crud\
        .get_device_status_subscription_for_root_simulation(
            db=db,
            subscription_id=subscription_id,
            root_simulation_id=simulation_id
        )

    # If subscription was not found return 404
    if not subscription_from_db:
        logging.error(
            f"Subscription with id {subscription_id} for Simulation" +
            f"{simulation_id} does not exist."
        )
        return DeviceStatusHelper.subscription_not_found()

    # Delete subscription
    crud.delete_device_status_subscription(
        db=db,
        subscription=subscription_from_db
    )

    subscription_delete_info = SubscriptionAsync(
        subscription_id=subscription_id
    )
    return Response(
        status_code=status.HTTP_202_ACCEPTED,
        content=subscription_delete_info.model_dump_json(),
        media_type="application/json"
    )


@router.get(
    "/subscriptions/{subscription_id}",
    responses=DeviceStatusResponses.GET_SUBSCRIPTION,
    tags=["Device status subscription"],
    summary="Retrieve a device status event subscription for a device",
    response_model_by_alias=True,
)
async def retrieve_subscription(
    simulation_id: int = Header(),
    subscription_id: str = Path(
        description="Subscription identifier that was obtained from the "
        "create subscription operation"
    ),
    db: Session = Depends(DBFactory.get_db_session)
) -> SubscriptionInfo:

    # Get subscription from database
    subscription_from_db = crud\
        .get_device_status_subscription_for_root_simulation(
            db=db,
            subscription_id=subscription_id,
            root_simulation_id=simulation_id
        )

    # If subscription was not found return 404
    if not subscription_from_db:
        logging.error(
            f"Subscription with id {subscription_id} for Simulation" +
            f"{simulation_id} does not exist."
        )
        return DeviceStatusHelper.subscription_not_found()

    return DeviceStatusHelper\
        .pydantic_subscription_info_from_db_subscription(
            db_subscription=subscription_from_db,
            simulated_device_from_db=crud.get_simulated_device_from_id(
                db=db,
                device_id=subscription_from_db.ue
            )
        )


@router.get(
    "/subscriptions",
    responses=DeviceStatusResponses.GET_SUBSCRIPTIONS,
    tags=["Device status subscription"],
    summary="Retrieve a list of device status event subscription",
    response_model_by_alias=True,
)
async def retrieve_subscription_list(
    simulation_id: int = Header(),
    db: Session = Depends(DBFactory.get_db_session)
) -> List[SubscriptionInfo]:

    # Parse the DB objects to pydantic ones, to cope with the standard
    return [
        DeviceStatusHelper
        .pydantic_subscription_info_from_db_subscription(
            db_subscription=subscription_from_db,
            simulated_device_from_db=crud.get_simulated_device_from_id(
                db=db,
                device_id=subscription_from_db.ue
            )
        )
        for subscription_from_db
        in crud
        .get_device_status_subscriptions_for_root_simulation(
            db=db,
            root_simulation_id=simulation_id
        )
    ]
