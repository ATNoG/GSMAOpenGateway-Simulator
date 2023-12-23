# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-06 22:11:09
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-22 11:10:57
from datetime import datetime
import logging
import config # noqa
from common.database import crud


class Simulation:
    def __init__(
        self, db, simulation_id, simulation_instance_id, child_simulation_id,
        simulation_payload
    ):
        self.db = db
        self.simulation_id = simulation_id
        self.simulation_instance_id = simulation_instance_id
        self.child_simulation_id = child_simulation_id
        self.simulation_payload = simulation_payload

    def start_simulation(self):
        logging.info(
            f"Child Simulation Instance {self.child_simulation_id} of " +
            f"Simulation Instance {self.simulation_instance_id} " +
            f"(Simulation {self.simulation_id} is starting!"
        )
        # Update the stat timestamp of the current child simulation
        crud.update_child_simulation_start_timestamp(
            db=self.db,
            child_simulation_id=self.child_simulation_id,
            start_timestamp=datetime.utcnow()
        )

    def stop_simulation(self):
        # This method will be overwritten in child classes
        pass

    def signal_that_simulation_ended(self):
        logging.info(
            f"Child Simulation {self.child_simulation_id} of " +
            f"Simulation Instance {self.simulation_instance_id} " +
            f"(Simulation {self.simulation_id} has ended!"
        )
        crud.update_child_simulation_end_timestamp(
            db=self.db,
            child_simulation_id=self.child_simulation_id,
            end_timestamp=datetime.utcnow()
        )
