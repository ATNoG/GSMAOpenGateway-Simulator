# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-27 11:15:07
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-30 17:45:32
# coding: utf-8
from sqlalchemy.orm import Session
from fastapi import APIRouter, Body, Header, Depends
import config # noqa
import logging
from common.apis.sim_swap_schemas import (
    CheckSimSwapInfo,
    CreateCheckSimSwap,
    SimSwapInfo,
    CreateSimSwapDate
)
from common.database import connections_factory as DBFactory
from common.database import crud
from common.helpers import sim_swap as SimSwapHelper
from helpers.responses_documentation.sim_swap_api import (
    SIMSwapResponses,
)

router = APIRouter()


@router.post(
    "/check",
    responses=SIMSwapResponses.CHECK,
    tags=["Check SIM swap"],
    response_model_by_alias=True,
)
async def check_sim_swap(
    simulation_id: int = Header(),
    create_check_sim_swap: CreateCheckSimSwap = Body(
        description="Create a check SIM swap request for a MSISDN identifier. "
    ),
    db: Session = Depends(DBFactory.get_db_session)
):
    # We can only retrieve locations if the simulation is active
    if not crud.simulation_is_running(db=db, simulation_id=simulation_id):
        logging.error(
            "Impossible to retrieve SIM swaps for Simulation " +
            f"{simulation_id}. This Simulation is not running. It must be " +
            "started first."
        )
        return SimSwapHelper.error_message_simulation_not_running()

    # Get the Simulated UE Instance
    simulated_ue_instance = crud\
        .get_simulated_device_instance_from_root_simulation_via_phone_number(
            db=db,
            root_simulation_id=simulation_id,
            device_phone_number=create_check_sim_swap.phone_number
        )

    # If no UE with the indicated phone number was found, inform the client
    if not simulated_ue_instance:
        return SimSwapHelper.error_message_unknown_phone_number()

    # Obtain the simulated data regarding that Simulated UE
    sim_swap_simulation_data = crud.get_sim_swap_simulation_data(
        db=db,
        root_simulation_id=simulation_id,
        ue_id=simulated_ue_instance.id
    )

    # If no simulated data was returned, than, the SIM was not swapped
    if not sim_swap_simulation_data:
        return CheckSimSwapInfo(
            swapped=False
        )

    # If we have simulated data, we have to check if it obeys to the maxAge
    # parameter
    # Get the simulated data age (seconds)
    simulated_data_age = SimSwapHelper.compute_simulated_data_age(
        sim_swap_simulation_data=sim_swap_simulation_data
    )

    # Get the max allowed age (seconds) requested by the user and compare it
    # with the simulated data age
    if simulated_data_age > create_check_sim_swap.max_age:
        return CheckSimSwapInfo(
            swapped=False
        )

    # If we got here, we can assume that:
    # - The requested device exists
    # - There is simulation data ( = the SIM was swapped)
    # - The simulation data obeys to the maximum maxAge constraint
    # Thus, we can affirm that the SIM was swapped

    return CheckSimSwapInfo(
        swapped=True
    )


@router.post(
    "/retrieve-date",
    responses=SIMSwapResponses.RETRIEVE_DATE,
    tags=["Retrieve SIM swap date"],
    response_model_by_alias=True,
)
async def retrieve_sim_swap_date(
    simulation_id: int = Header(),
    create_sim_swap_date: CreateSimSwapDate = Body(
        None,
        description="Create a SIM swap date request for a MSISDN identifier. "
    ),
    db: Session = Depends(DBFactory.get_db_session)
):
    # We can only retrieve locations if the simulation is active
    if not crud.simulation_is_running(db=db, simulation_id=simulation_id):
        logging.info(
            "Impossible to retrieve SIM swaps for Simulation " +
            f"{simulation_id}. This Simulation is not running. It must be " +
            "started first."
        )
        return SimSwapHelper.error_message_simulation_not_running()

    # Get the Simulated UE Instance
    simulated_ue_instance = crud\
        .get_simulated_device_instance_from_root_simulation_via_phone_number(
            db=db,
            root_simulation_id=simulation_id,
            device_phone_number=create_sim_swap_date.phone_number
        )

    # If no UE with the indicated phone number was found, inform the client
    if not simulated_ue_instance:
        return SimSwapHelper.error_message_unknown_phone_number()

    # Obtain the simulated data regarding that Simulated UE
    sim_swap_simulation_data = crud.get_sim_swap_simulation_data(
        db=db,
        root_simulation_id=simulation_id,
        ue_id=simulated_ue_instance.id
    )

    # If no simulated data was returned, than, the SIM was not swapped
    if not sim_swap_simulation_data:
        return SimSwapInfo()

    # If we got here, we can assume that:
    # - The requested device exists
    # - There is simulation data ( = the SIM was swapped)
    # Thus, we can return the datetime of the last swap

    return SimSwapInfo(
        latest_sim_change=sim_swap_simulation_data.timestamp
    )
