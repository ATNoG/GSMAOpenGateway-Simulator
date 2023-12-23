# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-19 15:21:40
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-23 16:36:52

import requests
import requests.exceptions
import config # noqa
import logging
import common.apis.device_location_schemas as DeviceLocationSchemas
import constants as Constants
from datetime import datetime
from common.database import crud
from common.helpers import device_location as DeviceLocationHelpers


class Notifications:
    def __init__(self, db):
        self.db = db

    def send_and_record_notification(self, subscription):

        logging.info(
            "Sending notification to " +
            f"{subscription.webhook.notification_url}. This notification " +
            "is realated with a " +
            f"{subscription.geofencing_subscription_type.value} event."
        )
        # First, we have to register this new notification
        notification_from_db = crud\
            .create_device_location_subscription_notification(
                db=self.db,
                subscription_id=subscription.subscription_id,
            )

        try:
            callback_payload = self.prepare_callback_payload(
                subscription,
                notification_from_db
            )

            response = requests.post(
                url=subscription.webhook.notification_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " +
                    subscription.webhook.notification_auth_token
                },
                data=callback_payload.model_dump(),
                timeout=15
            )
            # Raises an HTTPError for bad responses (4xx and 5xx)
            response.raise_for_status()
            logging.info(
                f"Notification to {subscription.webhook.notification_url} " +
                "was successful."
            )

            # Store results in DB
            self.store_notification_output_in_db(
                notification_id=notification_from_db.id,
                error_message=None
            )

            return callback_payload

        except Exception as exception:
            logging.error(
                    "Error on sending notification to " +
                    subscription.webhook.notification_url +
                    f". Reason: {exception}."
                )
            # Store results in DB
            self.store_notification_output_in_db(
                notification_id=notification_from_db.id,
                error_message=str(exception)
            )
            return None

    def prepare_callback_payload(self, subscription, notification_from_db):

        # Get the device information
        simulation_device = crud.get_simulated_device_from_id(
            db=self.db,
            device_id=subscription.ue
        )

        pydantic_device = DeviceLocationHelpers\
            .parse_simulation_ue_to_pydantic_device(
                simulation_device
            )

        return DeviceLocationSchemas.CloudEvent(
            id=notification_from_db.id,
            source=Constants.NOTIFICATION_SOURCE,
            type=subscription.geofencing_subscription_type,
            specversion="1.0",
            datacontenttype="application/json",
            time=datetime.utcnow(),
            data={
                "subscriptionId": subscription.subscription_id,
                "device": pydantic_device.model_dump(),
                "area": subscription.area.model_dump(),
            }
        )

    def store_notification_output_in_db(self, notification_id, error_message):
        # if error message -> notification unsuccessful
        # if no error message -> notification successful
        crud.update_device_location_subscription_notification(
            db=self.db,
            notification_id=notification_id,
            sucess=error_message is None,
            error=error_message
        )
