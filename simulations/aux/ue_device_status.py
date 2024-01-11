# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-06 22:13:23
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2024-01-10 17:51:11

import time
from datetime import datetime
import logging
import config # noqa
from common.simulation.simulation_types import SimulationType
from common.message_broker import schemas as SimulationSchemas
from common.message_broker.topics import Topics


class UEDeviceStatus():

    simulation_type = SimulationType.DEVICE_STATUS

    def __init__(
        self, simulation, ue, ue_instance, device_status_updates,
        message_queue_connection, message_queue_channel
    ):
        self.simulation = simulation
        self.ue = ue
        self.ue_instance = ue_instance
        self.device_status_updates = {
            status["on_timestamp"]: status
            for status
            in device_status_updates
        }

        self.simulation_duration = max(list(self.device_status_updates.keys()))
        self.message_queue_connection = message_queue_connection
        self.message_queue_channel = message_queue_channel
        self.stop_event = False

    def start_device_status_updates(self):
        logging.info(
            "Will start a Device Status simulation for UE Instance " +
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
            if total_sleep_time in self.device_status_updates:
                self.advertise_device_status(
                    self.device_status_updates[total_sleep_time]
                )

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
        logging.info(f"Stopping Device Status simulation for UE '{self.ue}'.")
        self.stop_event = True

    def advertise_device_status(self, status):

        # Build the payload
        simulation_data = SimulationSchemas.SimulationData(
            simulation_id=self.simulation.simulation_id,
            simulation_instance_id=self.simulation.simulation_instance_id,
            child_simulation_instance_id=self.simulation.child_simulation_id,
            simulation_type=self.simulation_type,
            data=SimulationSchemas.DeviceStatusSimulationData(
                ue=self.ue,
                ue_instance=self.ue_instance,
                connectivity_status=status["connectivity_status"],
                roaming=status.get("roaming"),
                country_code=status.get("country_code"),
                country_name=status.get("country_name"),
                timestamp=datetime.utcnow()
            )
        )

        # Output Payload for debugging
        logging.info(
            "New UE Device Status for UE Instance with id " +
            f"{self.ue_instance} (UE {self.ue} Simulation " +
            f"{self.simulation.simulation_id}, Simulation Instance " +
            f"{self.simulation.simulation_instance_id}, Child Simulation" +
            f" Instance {self.simulation.child_simulation_id}). " +
            "Current Device Status: (connectivity_status=" +
            f"{simulation_data.data.connectivity_status}, " +
            f"roaming={simulation_data.data.roaming}, " +
            f"country_code={simulation_data.data.country_code}, " +
            f"country_name={simulation_data.data.country_name}, " +
            f"timestamp={simulation_data.data.timestamp})"
        )

        # Send Payload
        self.message_queue_channel.basic_publish(
            exchange='',
            routing_key=Topics.SIMULATION_DATA.value,
            body=simulation_data.model_dump_json()
        )

        self.message_queue_channel.basic_publish(
            exchange='',
            routing_key=Topics.EVENTS.value,
            body=simulation_data.model_dump_json()
        )
