# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-06 22:13:23
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-13 17:02:07

import time
from datetime import datetime
import logging
import config # noqa
from common.simulation.simulation_types import SimulationType
from common.message_broker import schemas as SimulationSchemas
from common.message_broker.topics import Topics


class UEMovement():

    sleep_step = None
    simulation_type = SimulationType.DEVICE_LOCATION

    def __init__(
        self, simulation, ue, itinerary, simulation_duration,
        message_queue_connection, message_queue_channel
    ):
        self.simulation = simulation
        self.ue = ue
        self.itinerary = itinerary
        self.simulation_duration = simulation_duration
        self.message_queue_connection = message_queue_connection
        self.message_queue_channel = message_queue_channel
        self.stop_event = False
        # Compute the sleep step time for conducting the movements
        self._set_sleep_time()

    def _set_sleep_time(self):
        self.sleep_step = self.simulation_duration / (len(self.itinerary) - 1)

    def move(self):
        logging.info(
            f"Will start a simulation for UE '{self.ue}', " +
            f"for {self.simulation_duration} seconds"
        )

        for _, coordinates in self.itinerary:
            # The self.stop_event variable is used to stop the simulation
            # during running time
            if self.stop_event:
                break
            # Sleep for a while before moving the UE again
            time.sleep(self.sleep_step)
            self.advertise_current_location(coordinates[::-1])

        # Close producer connection
        self.message_queue_connection.close()

        # Signal that the UE has stopped
        # When all UEs are stopped, the simulation can be considered as
        # concluded
        self.simulation.signal_that_ue_has_stopped()

    def stop(self):
        logging.info(f"Stopping simulation for UE '{self.ue}'.")
        self.stop_event = True

    def advertise_current_location(self, location):        
        # Get current UTC time
        current_time = datetime.utcnow()

        # Format the time as a string
        formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%SZ')

        # Build the payload
        simulation_data = SimulationSchemas.SimulationData(
            simulation_id=self.simulation.simulation_id,
            child_simulation_id=self.simulation.child_simulation_id,
            simulation_type=self.simulation_type,
            data=SimulationSchemas.DeviceLocationSimulationData(
                ue=self.ue,
                latitude=location[0],
                longitude=location[1],
                timestamp=formatted_time
            )
        )

        # Output Payload for debugging
        logging.info(
            f"New UE Position for UE with id {self.ue} (Simulation " +
            f"Instance {self.simulation.simulation_id}, Child Simulation " +
            f"Instance {self.simulation.child_simulation_id}) is at " +
            f"{location}."
        )

        # Send Payload
        self.message_queue_channel.basic_publish(
            exchange='',
            routing_key=Topics.SIMULATION_DATA.value,
            body=simulation_data.model_dump_json()
        )
