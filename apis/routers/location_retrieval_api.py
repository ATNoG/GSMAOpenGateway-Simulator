# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-12 10:54:41
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-23 10:39:09
# coding: utf-8

import config # noqa
from fastapi import APIRouter, Body, Header, Depends
from sqlalchemy.orm import Session
import logging
from common.apis.device_location_schemas import RetrievalLocationRequest
from common.helpers import device_location as DeviceLocationHelper
from apis.helpers.responses_documentation.location_retrieval_api import (
    LocationRetrievalResponses
)
from common.database import connections_factory as DBFactory
from common.database import crud

router = APIRouter()


@router.post(
    "/retrieve",
    responses=LocationRetrievalResponses.POST_RETRIEVE,
    tags=["Location retrieval"],
    summary="Execute location retrieval for a user equipment",
    response_model_by_alias=True,
)
async def retrieve_location(
    simulation_id: int = Header(),
    retrieval_location_request: RetrievalLocationRequest = Body(),
    db: Session = Depends(DBFactory.get_db_session)
):

    # We can only retrieve locations if the simulation is active
    if not crud.simulation_is_running(db=db, simulation_id=simulation_id):
        logging.info(
            "Impossible to retrieve locations for Simulation " +
            f"{simulation_id}. This Simulation is not running. It must be " +
            "started first."
        )
        return DeviceLocationHelper.error_message_simulation_not_running()

    # Get the Simulated UE ID
    simulated_ue = crud.get_simulated_device_instance_from_root_simulation(
        db=db,
        root_simulation_id=simulation_id,
        device=retrieval_location_request.device
    )

    device_location_data = crud.get_device_location_simulation_data(
        db=db,
        root_simulation_id=simulation_id,
        ue=simulated_ue
    )

    # Get the simulated data age (seconds)
    simulated_data_age = DeviceLocationHelper.compute_simulated_data_age(
        device_location_data=device_location_data
    )

    # Get the max allowed age (seconds) requested by the user and compare it
    # with the simulated data age
    if simulated_data_age > retrieval_location_request.max_age:
        return DeviceLocationHelper.error_message_max_age_exceeded()

    return DeviceLocationHelper.create_location_message(
        device_location_data
    )
