# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-07 11:17:37
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2024-01-11 11:56:19
import sys
import json
import logging
import config # noqa
from common.message_broker import connections_factory as PikaFactory
from common.message_broker.topics import Topics
from common.message_broker import schemas as MessageBrokerSchemas
from geofencing_subscriptions_manager import GeofencingSubscriptionsManager
from device_status_subscriptions_manager import (
    DeviceStatusSubscriptionsManager
)
from common.simulation.simulation_types import SimulationType


def main():
    # Start RabbitMQ Consumer Connection
    _, channel = PikaFactory.get_new_pika_connection_and_channel()

    # Subscriptions Managers
    geofencing_subscriptions_manager = GeofencingSubscriptionsManager()
    device_status_subscriptions_manager = DeviceStatusSubscriptionsManager()

    def events_callback(ch, method, properties, body):

        message = json.loads(body)
        logging.debug(f"[x] Received {message}")

        # If the received payload relates with simulation data
        if "scope" in message and message['scope'] == "SIMULATION_DATA":
            simulation_data = MessageBrokerSchemas\
                .SimulationData(**message)

            if simulation_data.simulation_type == SimulationType\
                    .DEVICE_LOCATION:
                geofencing_subscriptions_manager.handle_ue_location_message(
                    simulation_data
                )

            elif simulation_data.simulation_type == SimulationType\
                    .DEVICE_STATUS:
                device_status_subscriptions_manager.handle_ue_status_message(
                    simulation_data
                )

    # Start consuming
    channel.basic_consume(
        queue=Topics.EVENTS.value,
        on_message_callback=events_callback,
        auto_ack=True
    )

    logging.info('[*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info('Interrupted')
        try:
            sys.exit(0)
        except SystemExit as e:
            logging.error(
                f"Couldn't start the events orchestrator due to: {e}"
            )
            raise e
