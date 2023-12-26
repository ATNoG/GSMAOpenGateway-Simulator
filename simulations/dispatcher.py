# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-06 22:09:54
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-26 20:42:15

import config # noqa
import logging
from device_location_simulation import DeviceLocationSimulation
from sim_swap_simulation import SIMSwapSimulation
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
        print("simulation_type -", simulation_type)
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

        elif simulation_type == SimulationType.SIM_SWAP:
            print("SIM_SWAP")
            simulation = SIMSwapSimulation(
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
                
        elif not simulation_type:
            # Improve this later
            raise ValueError("Invalid simulation type") # noqa
        else:
            raise ValueError("Invalid simulation type") # noqa        

    def start_simulation(
        self, simulation_instance_id, child_simulation_instance_id
    ):
        simulation_instance = self.simulations.get(simulation_instance_id)
        if not simulation_instance:
            logging.error(
                f"Simulation Instance {simulation_instance_id} was not " +
                "found. Therefore it cannot be started!"
            )
            return
        child_simulation_instance = simulation_instance.get(
            child_simulation_instance_id
            )
        if not simulation_instance:
            logging.error(
                f"Child Simulation Instance {child_simulation_instance_id} " +
                f"of Simulation Instance {simulation_instance_id} was not " +
                "found. Therefore it cannot be started!"
            )
            return
        child_simulation_instance.start_simulation()

    def stop_simulation(
        self, simulation_instance_id, child_simulation_instance_id
    ):
        simulation_instance = self.simulations.get(simulation_instance_id)
        if not simulation_instance:
            logging.info(
                f"Simulation Instance {simulation_instance_id} was not " +
                "found. Therefore it cannot be stopped."
            )
            return
        child_simulation_instance = simulation_instance.get(
            child_simulation_instance_id
            )
        if not child_simulation_instance:
            logging.info(
                f"Child Simulation Instance {child_simulation_instance_id} " +
                f"of Simulation Instance {simulation_instance_id} was not " +
                "found. Therefore it cannot be stopped."
            )
            return
        child_simulation_instance.stop_simulation()
