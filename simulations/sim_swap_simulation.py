# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-06 22:11:26
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-26 20:48:40
import threading
import config # noqa
from aux.ue_sim_swap import UESIMSwap
from base_simulation import Simulation
from common.simulation.simulation_types import SimulationType
from common.message_broker import connections_factory as PikaFactory
from common.database import crud


class SIMSwapSimulation(Simulation):

    ue_threads = []
    sim_swap_ues = []
    sim_swap_ues_count = None
    simulation_type = SimulationType.SIM_SWAP

    def __init__(
        self, db, simulation_id, simulation_instance_id, child_simulation_id,
        simulation_payload
    ):
        # Initialize super
        super().__init__(
            db, simulation_id, simulation_instance_id, child_simulation_id,
            simulation_payload
        )

    def signal_that_ue_has_stopped(self):
        self.sim_swap_ues_count -= 1
        if self.sim_swap_ues_count == 0:
            self.signal_that_simulation_ended()

    def start_simulation(self):

        # Start the simulation
        # The super start_simulation will handle everything that is common to
        # all types of simulations - e.g., updating the simulation's
        # start_timestamp
        super().start_simulation()

        for ue_instance in self.simulation_payload["devices"]:

            # Get Root UE
            ue = crud.get_simulated_device_id_from_simulated_device_instance(
                db=self.db,
                simulated_device_instance_id=ue_instance
            )

            connection, channel = PikaFactory\
                .get_new_pika_connection_and_channel()

            self.sim_swap_ues.append(
                UESIMSwap(
                    simulation=self,
                    ue=ue,
                    ue_instance=ue_instance,
                    timestamps_for_swaps_seconds=self.simulation_payload.get(
                        "timestamps_for_swaps_seconds"
                    ),
                    message_queue_connection=connection,
                    message_queue_channel=channel
                )
            )

        # Todo: Using threads is far from being the best approach to deal 
        # Todo: with this
        # Todo: This threading appraoch must be replaced by a more resilient 
        # Todo: one

        # Create threads
        self.ue_threads = [
            threading.Thread(target=ue.start_sim_swapping)
            for ue
            in self.sim_swap_ues
        ]
        self.sim_swap_ues_count = len(self.ue_threads)

        # Start the threads
        for thread in self.ue_threads:
            thread.start()

    def stop_simulation(self):
        # Stop all moving UEs
        for sim_swap_ue in self.sim_swap_ues:
            sim_swap_ue.stop()
        # Wait for all threads to finish
        for thread in self.ue_threads:
            thread.join()
        # Signal that the simulation has ended
        self.signal_that_simulation_ended()
