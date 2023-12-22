# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-19 12:13:53
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-22 22:24:52
# coding: utf-8

import config # noqa
from sqlalchemy.orm import Session
import logging
from typing import List  # noqa: F401
from fastapi import APIRouter, Header, Body, Path, Depends
from common.apis.device_location_schemas import (
    CreateSubscription,
    ErrorInfo,
    SubscriptionInfo,
)
import json
from fastapi import status
from fastapi.responses import Response
from common.helpers import device_location as DeviceLocationHelper
from common.message_broker import schemas as MessageBrokerSchemas
from common.database import connections_factory as DBFactory
from common.apis import device_location_schemas as DeviceLocationSchemas
from common.helpers import device_location as DeviceLocationHelpers
from helpers.responses_documentation.geofencing_api import (
    GeofencingResponses
)
from helpers import message_broker as PikaHelper
from common.database import crud
import copy

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

    # Send the new subscription to the events module.
    # This behaviour is due to the fact that a client may create a new
    # subscription when the simulation is already running
    subscription_parse_for_broker = MessageBrokerSchemas\
        .GeofencingSubscription(
            simulation_id=simulation_id,
            subscription_id=created_subscription.id,
            subscription_type=MessageBrokerSchemas
            .SubscriptionType.DEVICE_LOCATION_GEOFENCING,
            area=DeviceLocationHelpers.parse_area_dict_to_pydantic_area(
                json.loads(json.loads(created_subscription.area))
            ),
            geofencing_subscription_type=created_subscription
            .subscription_type,
            ue=created_subscription.ue,
            webhook=DeviceLocationSchemas.Webhook(
                notificationUrl=created_subscription.webhook_url,
                notificationAuthToken=created_subscription
                .webhook_auth_token
            ),
            expire_time=created_subscription.expire_time,
        )

    message_to_send_to_events_module = MessageBrokerSchemas.\
        GeofencingSubscriptionEvent(
            simulation_id=simulation_id,
            operation=MessageBrokerSchemas
            .GeofencingSubscriptionEventOperation.add,
            subscriptions=[subscription_parse_for_broker]
        )

    # Send message to the events module
    PikaHelper.send_events_messages(message_to_send_to_events_module)

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

    subscription_from_db_snapshot = copy.deepcopy(subscription_from_db)
    # Delete subscription
    crud.delete_location_subscription(
        db=db,
        subscription=subscription_from_db
    )

    # Send the new subscription to the events module.
    # This behaviour is due to the fact that a client may create a new
    # subscription when the simulation is already running
    subscription_parse_for_broker = MessageBrokerSchemas\
        .GeofencingSubscription(
            simulation_id=simulation_id,
            subscription_id=subscription_from_db_snapshot.id,
            subscription_type=MessageBrokerSchemas
            .SubscriptionType.DEVICE_LOCATION_GEOFENCING,
            area=DeviceLocationHelpers.parse_area_dict_to_pydantic_area(
                json.loads(json.loads(subscription_from_db_snapshot.area))
            ),
            geofencing_subscription_type=subscription_from_db_snapshot
            .subscription_type,
            ue=subscription_from_db_snapshot.ue,
            webhook=DeviceLocationSchemas.Webhook(
                notificationUrl=subscription_from_db_snapshot.webhook_url,
                notificationAuthToken=subscription_from_db_snapshot
                .webhook_auth_token
            ),
            expire_time=subscription_from_db_snapshot.expire_time,
        )

    message_to_send_to_events_module = MessageBrokerSchemas.\
        GeofencingSubscriptionEvent(
            simulation_id=simulation_id,
            operation=MessageBrokerSchemas
            .GeofencingSubscriptionEventOperation.delete,
            subscriptions=[subscription_parse_for_broker]
        )

    # Send message to the events module
    PikaHelper.send_events_messages(message_to_send_to_events_module)
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
