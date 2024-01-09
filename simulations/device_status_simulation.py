# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-06 22:11:26
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2024-01-09 18:28:55
import threading
import config # noqa
from aux.ue_device_status import UEDeviceStatus
from base_simulation import Simulation
from common.simulation.simulation_types import SimulationType
from common.message_broker import connections_factory as PikaFactory
from common.database import crud


class DeviceStatusSimulation(Simulation):

    ue_threads = []
    device_status_ues = []
    device_status_ues_count = None
    simulation_type = SimulationType.DEVICE_STATUS

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
        self.device_status_ues_count -= 1
        if self.device_status_ues_count == 0:
            self.signal_that_simulation_ended()

    def start_simulation(self):
        self.device_status_ues = []
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

            self.device_status_ues.append(
                UEDeviceStatus(
                    simulation=self,
                    ue=ue,
                    ue_instance=ue_instance,
                    device_status_updates=self.simulation_payload[
                        "device_status_updates"
                    ],
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
            threading.Thread(target=ue.start_device_status_updates)
            for ue
            in self.device_status_ues
        ]
        self.device_status_ues_count = len(self.ue_threads)

        # Start the threads
        for thread in self.ue_threads:
            thread.start()

    def stop_simulation(self):
        # Stop all moving UEs
        for device_status_ue in self.device_status_ues:
            device_status_ue.stop()
        # Wait for all threads to finish
        for thread in self.ue_threads:
            thread.join()
        # Signal that the simulation has ended
        self.signal_that_simulation_ended()
