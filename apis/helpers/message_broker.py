# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-13 14:26:29
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-15 21:08:03

import logging
import config # noqa
from common.message_broker import connections_factory as PikaFactory
from common.message_broker.topics import Topics


def send_simulation_messages(simulation_messages):
    connection, channel = PikaFactory.get_new_pika_connection_and_channel()

    for simulation_message in simulation_messages:
        # Create the simulation
        channel.basic_publish(
            exchange='',
            routing_key=Topics.SIMULATION.value,
            body=simulation_message.model_dump_json()
        )

        logging.info(
            f"Sent simulation {simulation_message.action.value} message " +
            " for Child Simulation Instance  with id " +
            f"{simulation_message.child_simulation_instance_id} " +
            "(Simulation Instance with id " +
            f"{simulation_message.simulation_instance_id})" +
            f"to {Topics.SIMULATION.value}"
        )
    connection.close()
