# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-14 11:14:04
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-27 14:46:34
from datetime import datetime
from fastapi.responses import JSONResponse
import config # noqa
from common.apis.sim_swap_schemas import ErrorInfo
from common.database import models


def compute_simulated_data_age(
    sim_swap_simulation_data: models.SimSwapSimulationData
):
    # Get the current time
    current_time = datetime.utcnow()

    # Compute the time difference
    time_difference = current_time - sim_swap_simulation_data.timestamp

    # Return the difference in seconds
    return time_difference.total_seconds()


def error_message_simulation_not_running():
    return JSONResponse(
            status_code=404,
            content=ErrorInfo(
                status=404,
                code="SIMULATION.NOT_RUNNING",
                message="The simulation is not running. Thus, you cannot " +
                "get its generated data"
            ).__dict__
        )


def error_message_unknown_phone_number():
    return JSONResponse(
            status_code=404,
            content=ErrorInfo(
                status=404,
                code="SIM_SWAP.UNKNOWN_PHONE_NUMBER",
                message="SIM Swap can't be checked because the phone "
                "number is unknown."
            ).__dict__
        )
