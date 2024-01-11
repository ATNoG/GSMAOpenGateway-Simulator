# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-06 22:11:26
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2024-01-10 11:03:09

import config # noqa
from common.database import crud
import logging
import json


class DeviceStatusHandler():

    @staticmethod
    def process_message(simulation_data, db):
        try:
            logging.debug(f" [x] Received {simulation_data}")

            # 1. Get last simulation data
            device_status_simulation_data = crud.get_last_device_status_entry(
                db=db,
                simulation_instance=simulation_data.simulation_instance_id,
                ue_id=simulation_data.data["ue_instance"]
            )

            # 2. Evaluate which fields should be updated
            connectivity_status = simulation_data.data["connectivity_status"] \
                if simulation_data.data["connectivity_status"] \
                else device_status_simulation_data.connectivity_status

            roaming = simulation_data.data["roaming"] \
                if simulation_data.data["roaming"] \
                else device_status_simulation_data.roaming

            country_code = simulation_data.data["country_code"] \
                if simulation_data.data["country_code"] \
                else device_status_simulation_data.country_code
            country_name = simulation_data.data["country_name"] \
                if simulation_data.data["country_name"] \
                else json.loads(device_status_simulation_data.country_name)

            # 3. Update simulation data
            crud.create_device_status_simulation_data_entry(
                db=db,
                simulation_instance=simulation_data.simulation_instance_id,
                child_simulation_instance=simulation_data
                .child_simulation_instance_id,
                ue_id=simulation_data.data["ue_instance"],
                connectivity_status=connectivity_status,
                roaming=roaming,
                country_code=country_code,
                country_name=country_name
            )
        except Exception as e:
            logging.error(
                f"Error processing Device Location message. Reason: {e}"
            )
