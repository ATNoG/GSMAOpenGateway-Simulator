# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-06 22:13:23
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-27 10:31:29

import time
from datetime import datetime
import logging
import config # noqa
from common.simulation.simulation_types import SimulationType
from common.message_broker import schemas as SimulationSchemas
from common.message_broker.topics import Topics


class UESIMSwap():

    simulation_type = SimulationType.SIM_SWAP

    def __init__(
        self, simulation, ue, ue_instance, timestamps_for_swaps_seconds,
        message_queue_connection, message_queue_channel
    ):
        self.simulation = simulation
        self.ue = ue
        self.ue_instance = ue_instance
        self.timestamps_for_swaps_seconds = sorted([
            int(ts)
            for ts
            in timestamps_for_swaps_seconds
        ])
        self.simulation_duration = max(self.timestamps_for_swaps_seconds)
        self.message_queue_connection = message_queue_connection
        self.message_queue_channel = message_queue_channel
        self.stop_event = False

    def start_sim_swapping(self):
        logging.info(
            "Will start a SIM Swap simulation for UE Instance " +
            f"'{self.ue_instance}' (UE {self.ue}), for "
            f"{self.simulation_duration} seconds"
        )

        total_sleep_time = 0

        while (
            not self.stop_event
            and
            total_sleep_time <= self.simulation_duration
        ):
            # Check if SIM Swap should occur
            if total_sleep_time in self.timestamps_for_swaps_seconds:
                self.advertise_sim_swap()

            # Wait 1 second
            time.sleep(1)
            total_sleep_time += 1

        # Close producer connection
        self.message_queue_connection.close()

        # Signal that the UE has stopped
        # When all UEs are stopped, the simulation can be considered as
        # concluded
        self.simulation.signal_that_ue_has_stopped()

    def stop(self):
        logging.info(f"Stopping SIM Swwap simulation for UE '{self.ue}'.")
        self.stop_event = True

    def advertise_sim_swap(self):
        # Get current UTC time
        current_time = datetime.utcnow()

        # Format the time as a string
        formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%SZ')

        # Build the payload
        simulation_data = SimulationSchemas.SimulationData(
            simulation_id=self.simulation.simulation_id,
            simulation_instance_id=self.simulation.simulation_instance_id,
            child_simulation_instance_id=self.simulation.child_simulation_id,
            simulation_type=self.simulation_type,
            data=SimulationSchemas.SIMSwapSimulationData(
                ue=self.ue,
                ue_instance=self.ue_instance,
                new_msisdn="dummy_msisdn",
                timestamp=formatted_time
            )
        )

        # Output Payload for debugging
        logging.info(
            f"New UE SIM Swap for UE Instance with id {self.ue_instance} " +
            f"(UE {self.ue} Simulation " +
            f"{self.simulation.simulation_id}, Simulation Instance " +
            f"{self.simulation.simulation_instance_id}, Child Simulation" +
            f" Instance {self.simulation.child_simulation_id}) swapped SIM " +
            f"at {formatted_time}"
        )

        # Send Payload
        self.message_queue_channel.basic_publish(
            exchange='',
            routing_key=Topics.SIMULATION_DATA.value,
            body=simulation_data.model_dump_json()
        )
