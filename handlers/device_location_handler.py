# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-06 22:11:26
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-14 11:01:55


from datetime import datetime
import config # noqa
from common.database import crud
import logging


class DeviceLocationHandler():

    @staticmethod
    def process_message(simulation_data, db):
        logging.debug(f" [x] Received {simulation_data}")

        timestamp_str = simulation_data.data["timestamp"]
        timestamp_dt = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%SZ')

        crud.create_device_location_simulation_data_entry(
            db=db,
            simulation_instance=simulation_data.simulation_id,
            child_simulation_instance=simulation_data.child_simulation_id,
            ue_id=simulation_data.data["ue"],
            latitude=simulation_data.data["latitude"],
            longitude=simulation_data.data["longitude"],
            timestamp=timestamp_dt,
        )
