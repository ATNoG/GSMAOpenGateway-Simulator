# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-07 11:17:37
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-22 11:47:23
import json
import sys
import logging
import config # noqa
from dispatcher import SimulationDispatcher
from common.message_broker import connections_factory as PikaFactory
from common.message_broker.topics import Topics
from common.message_broker import schemas as SimulationSchemas
from common.simulation.simulation_operations import SimulationOperation


def main():
    # Start RabbitMQ Consumer Connection
    _, consumer_channel = PikaFactory.get_new_pika_connection_and_channel()

    # Start the dispatcher
    simulation_dispatcher = SimulationDispatcher()

    def my_callback(ch, method, properties, body):
        simulation = SimulationSchemas\
            .SimulationAction(**json.loads(body))

        logging.debug(f" [x] Received {simulation}")

        if simulation.action == SimulationOperation.START:
            logging.info(
                f"Simulation {simulation.child_simulation_instance_id} " +
                "will start."
            )

            simulation_dispatcher.create_simulation(
                simulation_id=simulation.simulation_id,
                simulation_instance_id=simulation.simulation_instance_id,
                child_simulation_instance_id=simulation
                .child_simulation_instance_id,
                simulation_type=simulation.simulation_type,
                simulation_payload=simulation.simulation_config,
            )

            simulation_dispatcher.start_simulation(
                simulation_instance_id=simulation.simulation_instance_id,
                child_simulation_instance_id=simulation
                .child_simulation_instance_id,
            )

        elif simulation.action == SimulationOperation.STOP:
            logging.info(
                f"Simulation Instance {simulation.simulation_instance_id} " +
                "will stop."
            )

            simulation_dispatcher.stop_simulation(
                simulation_instance_id=simulation.simulation_instance_id,
                child_simulation_instance_id=simulation
                .child_simulation_instance_id,
            )

    # Start consuming
    consumer_channel.basic_consume(
        queue=Topics.SIMULATION.value,
        on_message_callback=my_callback,
        auto_ack=True
    )

    logging.info(' [*] Waiting for messages. To exit press CTRL+C')
    consumer_channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info('Interrupted')
        try:
            sys.exit(0)
        except SystemExit as e:
            logging.error('SystemExit')
            raise e
