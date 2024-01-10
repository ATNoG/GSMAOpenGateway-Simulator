# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-14 11:14:04
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2024-01-10 12:12:42
from fastapi.responses import JSONResponse
import config # noqa
import json
from common.apis.sim_swap_schemas import ErrorInfo
from common.database import models
from common.apis.device_status_schemas import (
    ConnectivityStatus,
    Webhook,
    SubscriptionDetail,
    SubscriptionInfo,
    Device,
    DeviceIpv4Addr
)


def error_message_simulation_not_running():
    return JSONResponse(
            status_code=412,
            content=ErrorInfo(
                status=412,
                code="SIMULATION.NOT_RUNNING",
                message="The simulation is not running. Thus, you cannot " +
                "get its generated data"
            ).__dict__
        )


def error_message_unknown_device():
    return JSONResponse(
            status_code=404,
            content=ErrorInfo(
                status=404,
                code="NOT_FOUND",
                message="The specified resource is not found."
            ).__dict__
        )


def get_connectivity_enum_from_value(value):
    for status in ConnectivityStatus:
        if status.value == value:
            return status


def subscription_not_found():
    return JSONResponse(
            status_code=404,
            content=ErrorInfo(
                status=404,
                code="NOT_FOUND",
                message="The specified resource is not found"
            ).__dict__
        )


def parse_simulation_ue_to_pydantic_device(
    simulation_ue: models.SimulationUE
) -> Device:
    ipv4_address = DeviceIpv4Addr()

    if simulation_ue.ipv4_address_public_address:
        ipv4_address.public_address = simulation_ue\
            .ipv4_address_public_address
    if simulation_ue.ipv4_address_private_address:
        ipv4_address.private_address = simulation_ue\
            .ipv4_address_private_address
    if simulation_ue.ipv4_address_public_port:
        ipv4_address.public_port = simulation_ue\
            .ipv4_address_public_port

    return Device(
        phone_number=simulation_ue.phone_number,
        network_access_identifier=simulation_ue.network_access_identifier,
        ipv4_address=ipv4_address,
        ipv6_address=simulation_ue.ipv6_address,
    )


def pydantic_subscription_info_from_db_subscription(
    db_subscription, simulated_device_from_db
):
    # Recreate the Webhook Object
    webook = Webhook(
        notificationUrl=db_subscription.webhook_url,
        notificationAuthToken=db_subscription.webhook_auth_token
    )

    device = parse_simulation_ue_to_pydantic_device(
        simulated_device_from_db
    )

    subscription_detail = SubscriptionDetail(
        device=device,
        type=db_subscription.subscription_type
    )

    return SubscriptionInfo(
        webhook=webook,
        subscription_detail=subscription_detail,
        subscription_expire_time=db_subscription.expire_time,
        subscription_id=db_subscription.id,
        starts_at=db_subscription.start_time,
        expires_at=db_subscription.expire_time
    )
