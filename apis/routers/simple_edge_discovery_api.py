# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-19 12:13:53
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-30 20:50:02
# coding: utf-8

import config # noqa
from sqlalchemy.orm import Session
from enum import Enum
import logging
from typing import List  # noqa: F401
from fastapi import APIRouter, Header, Depends, Query
from common.apis.simple_edge_discovery_schemas import MecPlatform
from common.database import connections_factory as DBFactory
from common.helpers import simple_edge_discovery as SimpleEdgeDiscoveryHelpers
from common.database import crud
from apis.helpers.responses_documentation.simple_edge_discovery_api import (
    SimpleEdgeDiscoveryResponses
)

router = APIRouter()


class FilterEnum(str, Enum):
    closest = "closest"


@router.get(
    "/mec-platforms",
    responses=SimpleEdgeDiscoveryResponses.GET_MEC_PLATFORMS,
    tags=["Discovery"],
    summary="Returns the name of the MEC platform closest to user device "
    "identified in the request.",
    response_model_by_alias=True,
)
async def get_mecplatforms(
    simulation_id: int = Header(
        alias="simulation-id"
    ),
    filter: FilterEnum = Query(
        description="filter the MEC Platforms according to the parameter "
        "value. For this API the only supported value is `closest`"
    ),
    ip_address: str = Header(
        None,
        description="The public IP allocated to the device.",
        alias="IP-Address",
        example="84.125.93.10"
    ),
    network_access_identifier: str = Header(
        None,
        description="3GPP network access identifier for the subscription "
        "being used by the device",
        alias="Network-Access-Identifier",
        example="4d596ac1-7822-4927-a3c5-d72e1f922c94@domain.com"
    ),
    phone_number: str = Header(
        None,
        description="MSISDN in E.164 format (starting with country code) "
        "of the mobile subscription being used by the device. Optionally "
        "prefixed with &#39;+&#39;.", regex=r"^\+?\d{5,15}$",
        alias="Phone-Number",
        example="441234567890"
        ),
    db: Session = Depends(DBFactory.get_db_session)
) -> List[MecPlatform]:
    # We can only retrieve locations if the simulation is active
    if not crud.simulation_is_running(db=db, simulation_id=simulation_id):
        logging.error(
            "Impossible to retrieve Mec Platforms for Simulation " +
            f"{simulation_id}. This Simulation is not running. It must be " +
            "started first."
        )
        return SimpleEdgeDiscoveryHelpers\
            .error_message_simulation_not_running()

    # Evaluate if at least one of the device's filtering parameters was
    # provided by the user
    if (
        ip_address is None
        and network_access_identifier is None
        and phone_number is None
    ):
        logging.error(
            "Insufficient parameters: At least one of " +
            "Network-Access-Identifier, Phone-Number or IP-Address must " +
            "be specified, or, the API must be called by a client on a " +
            "netwok-attached device (hence passing the source IP in the " +
            "request header)"
        )
        return SimpleEdgeDiscoveryHelpers\
            .error_message_insufficient_parameters()

    # Get the simulated device requested by the client
    simulated_ue = crud\
        .get_simulated_device_based_on_several_parameters(
            db=db,
            root_simulation_id=simulation_id,
            ip_address=ip_address,
            network_access_identifier=network_access_identifier,
            phone_number=phone_number
        )

    # If no UE with the indicated phone number was found, inform the client
    if not simulated_ue:
        return SimpleEdgeDiscoveryHelpers\
            .error_message_device_not_found()

    logging.info(f"Simulated Device: {simulated_ue.__dict__}")

    # Get simulated device instance, so we can then query its location in
    # the simulation
    simulated_ue_instance = crud\
        .get_simulated_device_instance_from_root_simulation(
            db=db,
            root_simulation_id=simulation_id,
            device=simulated_ue
        )

    if not simulated_ue_instance:
        return SimpleEdgeDiscoveryHelpers\
            .error_message_simulation_is_starting()

    logging.info(
        f"Simulated Device Instance: {simulated_ue_instance.__dict__}"
    )

    simulated_ue_location_data = crud\
        .get_device_location_simulation_data(
            db=db,
            root_simulation_id=simulation_id,
            ue=simulated_ue_instance
        )

    if not simulated_ue_location_data:
        return SimpleEdgeDiscoveryHelpers\
            .error_message_simulation_is_starting()

    logging.info(
        f"Simulated Device Location: {simulated_ue_location_data.__dict__}"
    )

    # Get the Simulation Mec Platforms for the simulation
    mec_platforms = crud.get_mec_platforms_for_root_simulation(
        db=db,
        root_simulation_id=simulation_id
    )

    closest_mec_platform = SimpleEdgeDiscoveryHelpers\
        .get_closest_mec_platform(
            mec_platforms=mec_platforms,
            device_location_simulation_data=simulated_ue_location_data
        )

    return [
        MecPlatform(
            edge_cloud_provider=closest_mec_platform.edge_cloud_provider,
            edge_resource_name=closest_mec_platform.edge_resource_name,
        )
    ]
