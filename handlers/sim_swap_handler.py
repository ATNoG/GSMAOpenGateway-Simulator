# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-06 22:11:26
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-27 10:33:48


from datetime import datetime
import config # noqa
from common.database import crud
import logging


class SIMSwapHandler():

    @staticmethod
    def process_message(simulation_data, db):
        try:
            logging.debug(f" [x] Received {simulation_data}")

            crud.create_sim_swap_simulation_data_entry(
                db=db,
                simulation_instance=simulation_data.simulation_instance_id,
                child_simulation_instance=simulation_data
                .child_simulation_instance_id,
                ue_id=simulation_data.data["ue_instance"],
                new_msisdn=simulation_data.data["new_msisdn"],
                timestamp=datetime.strptime(
                    simulation_data.data["timestamp"],
                    '%Y-%m-%dT%H:%M:%SZ'
                )
            )
        except Exception as e:
            logging.error(
                f"Error processing SIM Swap message. Reason: {e}"
            )
