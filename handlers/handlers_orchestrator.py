# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-07 11:17:37
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-11 21:05:18
import sys
import json
import logging
import config # noqa
from device_location_handler import DeviceLocationHandler
from common.message_broker import connections_factory as PikaFactory
from common.simulation.simulation_types import SimulationType
from common.message_broker.topics import Topics
from common.database import connections_factory as DBFactory
from common.message_broker import schemas as SimulationSchemas


def main():
    # Start RabbitMQ Consumer Connection
    _, channel = PikaFactory.get_new_pika_connection_and_channel()

    db = DBFactory.new_db_session()

    def handlers_callback(ch, method, properties, body):
        simulation_data = SimulationSchemas\
            .SimulationData(**json.loads(body))

        logging.debug(f"[x] Received {simulation_data}")

        if simulation_data.simulation_type == SimulationType.DEVICE_LOCATION:
            DeviceLocationHandler.process_message(simulation_data, db)

    # Start consuming
    channel.basic_consume(
        queue=Topics.SIMULATION_DATA.value,
        on_message_callback=handlers_callback,
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
                f"Couldn't start the handlers orchestrator due to: {e}"
            )
            raise e
