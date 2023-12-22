# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-06 22:09:54
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-22 11:20:08

import config # noqa
from device_location_simulation import DeviceLocationSimulation
from common.simulation.simulation_types import SimulationType
from common.database import connections_factory as DBFactory


class SimulationDispatcher:

    def __init__(self):
        self.simulations = {}
        self.db = DBFactory.new_db_session()

    def create_simulation(
        self, simulation_id, simulation_instance_id,
        child_simulation_instance_id, simulation_type, simulation_payload
    ):

        if simulation_type == SimulationType.DEVICE_LOCATION:
            # Create Simulation
            simulation = DeviceLocationSimulation(
                db=self.db,
                simulation_id=simulation_id,
                simulation_instance_id=simulation_instance_id,
                child_simulation_id=child_simulation_instance_id,
                simulation_payload=simulation_payload
            )

            if simulation_instance_id not in self.simulations:
                self.simulations[simulation_instance_id] = {
                    child_simulation_instance_id: simulation
                }
            else:
                self.simulations[
                    simulation_instance_id
                ][child_simulation_instance_id] = simulation

            print("self.simulations")
            print(self.simulations)

        elif not simulation_type:
            # Improve this later
            raise ValueError("Invalid simulation type") # noqa
        else:
            raise ValueError("Invalid simulation type") # noqa        

    def start_simulation(
        self, simulation_instance_id, child_simulation_instance_id
    ):
        self.simulations[simulation_instance_id][child_simulation_instance_id]\
            .start_simulation()

    def stop_simulation(
        self, simulation_instance_id, child_simulation_instance_id
    ):
        print("self.simulations")
        print(self.simulations)
        self.simulations[simulation_instance_id][child_simulation_instance_id]\
            .stop_simulation()
