# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-26 13:17:25
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-26 17:53:06
from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timedelta
import config # noqa
import logging
from common.message_broker import constants as Constants
from common.database import connections_factory as DBFactory
from common.database import crud


# Create the Celery App
app = Celery(
    'cleanup_miss_stopped_simulations',
    broker=f'amqp://{Constants.PIKA_CONNECTION_HOST}:'
    f'{Constants.PIKA_CONNECTION_PORT}'
    )


@app.task
def cleanup_miss_stopped_child_simulation():
    # Create DB connection
    db = DBFactory.new_db_session()

    all_child_simulation_instances_running = crud\
        .get_all_child_simulation_instances_running(db)

    ALL_SIMULATION_OK = True
    for child_sim_inst in all_child_simulation_instances_running:

        maximum_end_timestamp = (
            child_sim_inst.start_timestamp +
            timedelta(seconds=int(child_sim_inst.duration_seconds) + 30)
        )

        # Check is simulation should have been listed has stopped but wasn't
        # (due to a mistake)
        if (datetime.utcnow() > maximum_end_timestamp):
            logging.info(
                f"Child Simulation Instance {child_sim_inst.id}  (Simulation "
                f"Instance {child_sim_inst.simulation_instance}) should " +
                "have been stopped by now. However, due to a mistake it " +
                "wasn't. To cleanup this situation, the simulation instance " +
                "will be marked as completed."
            )
            ALL_SIMULATION_OK = False

            crud.update_child_simulation_end_timestamp(
                db=db,
                child_simulation_id=child_sim_inst.id,
                end_timestamp=datetime.utcnow()
            )

    if ALL_SIMULATION_OK:
        logging.info("All Child Simulations have been correctly stopped.")

    # Close connection with DB
    db.close()


# Define a periodic task to run every minute
app.conf.beat_schedule = {
    'run-x-every-minute': {
        'task': 'cleanup_miss_stopped_simulations'
        '.cleanup_miss_stopped_child_simulation',
        'schedule': crontab(minute='*'),
    },
}

app.conf.timezone = 'UTC'
