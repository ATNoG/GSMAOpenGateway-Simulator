# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-19 12:13:53
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-23 20:47:58
# coding: utf-8

import config # noqa
from sqlalchemy.orm import Session
import logging
from typing import List  # noqa: F401
from fastapi import APIRouter, Header, Body, Path, Depends
from common.apis.device_location_schemas import (
    CreateSubscription,
    SubscriptionInfo,
)
from fastapi import status
from fastapi.responses import Response
from common.helpers import device_location as DeviceLocationHelper
from common.database import connections_factory as DBFactory
from helpers.responses_documentation.geofencing_api import (
    GeofencingResponses
)
from common.database import crud

router = APIRouter()


@router.post(
    "/subscriptions",
    responses=GeofencingResponses.POST_GEOFENCE_SUBSCRIPTION,
    tags=["Geofencing subscriptions"],
    summary="Create a geofencing subscription for a device",
    response_model_by_alias=True,
    status_code=201
)
async def create_subscription(
    simulation_id: int = Header(),
    create_subscription: CreateSubscription = Body(),
    db: Session = Depends(DBFactory.get_db_session)
):
    # Todo: If simulation was not created, you need to create it, in 
    # Todo: order to register the UES

    # Get the Simulated UE ID
    simulated_ue = crud.get_simulated_device_from_root_simulation(
        db=db,
        root_simulation_id=simulation_id,
        device=create_subscription.subscription_detail.device
    )

    # Store subscription in database
    created_subscription = crud.create_device_location_subscription(
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
    responses=GeofencingResponses.DELETE_GEOFENCE_SUBSCRIPTION,
    tags=["Geofencing subscriptions"],
    summary="Operation to delete a subscription",
    response_model_by_alias=True,
    status_code=204
)
async def delete_subscription(
    simulation_id: int = Header(),
    subscription_id: str = Path(description="subscription identifier"),
    db: Session = Depends(DBFactory.get_db_session)
):
    # Get subscription from database
    subscription_from_db = crud\
        .get_device_location_subscription_for_root_simulation(
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
        return DeviceLocationHelper.subscription_not_found()

    # Delete subscription
    crud.delete_location_subscription(
        db=db,
        subscription=subscription_from_db
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/subscriptions/{subscription_id}",
    responses=GeofencingResponses.GET_GEOFENCE_SUBSCRIPTION,
    tags=["Geofencing subscriptions"],
    summary="Operation to retrieve a subscription based on the provided ID",
    response_model_by_alias=True,
)
async def get_subscription(
    simulation_id: int = Header(),
    subscription_id: str = Path(
        description="Subscription identifier that was obtained from " +
        "the create event subscription operation"
    ),
    db: Session = Depends(DBFactory.get_db_session)
) -> SubscriptionInfo:

    # Get subscription from database
    subscription_from_db = crud\
        .get_device_location_subscription_for_root_simulation(
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
        return DeviceLocationHelper.subscription_not_found()

    return DeviceLocationHelper\
        .pydantic_subscription_info_from_db_subscription(
            db_subscription=subscription_from_db,
            simulated_device_from_db=crud.get_simulated_device_from_id(
                db=db,
                device_id=subscription_from_db.ue
            )
        )


@router.get(
    "/subscriptions",
    responses=GeofencingResponses.GET_GEOFENCE_SUBSCRIPTIONS,
    tags=["Geofencing subscriptions"],
    summary="Operation to retrieve a list of subscriptions.",
    response_model_by_alias=True,
)
async def get_subscription_list(
    simulation_id: int = Header(),
    db: Session = Depends(DBFactory.get_db_session)
) -> List[SubscriptionInfo]:

    # Parse the DB objects to pydantic ones, to cope with the standard
    return [
        DeviceLocationHelper
        .pydantic_subscription_info_from_db_subscription(
            db_subscription=subscription_from_db,
            simulated_device_from_db=crud.get_simulated_device_from_id(
                db=db,
                device_id=subscription_from_db.ue
            )
        )
        for subscription_from_db
        in crud
        .get_device_location_subscriptions_for_root_simulation(
            db=db,
            root_simulation_id=simulation_id
        )
    ]
