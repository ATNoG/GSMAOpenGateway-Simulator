# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-19 15:21:40
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2024-01-11 11:41:55

import requests
import requests.exceptions
import config # noqa
import logging
import common.apis.device_location_schemas as DeviceLocationSchemas
import common.apis.device_status_schemas as DeviceStatusSchemas

import constants as Constants
from datetime import datetime
from common.database import crud
from common.helpers import device_location as DeviceLocationHelpers


class Notifications:
    def __init__(self, db):
        self.db = db

    def send_and_record_location_notification(self, subscription):

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
            callback_payload = self.prepare_location_callback_payload(
                subscription,
                notification_from_db
            )

            # Tweak the callback payload
            callback_payload = callback_payload.model_dump()
            callback_payload["type"] = callback_payload["type"].value
            callback_payload["time"] = callback_payload["time"]\
                .strftime("%Y-%m-%dT%H:%M:%S.%fZ")

            response = requests.post(
                url=subscription.webhook.notification_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " +
                    subscription.webhook.notification_auth_token
                },
                json=callback_payload,
                timeout=15
            )
            # Raises an HTTPError for bad responses (4xx and 5xx)
            response.raise_for_status()
            logging.info(
                f"Notification to {subscription.webhook.notification_url} " +
                "was successful."
            )

            # Store results in DB
            self.store_location_notification_output_in_db(
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
            self.store_location_notification_output_in_db(
                notification_id=notification_from_db.id,
                error_message=str(exception)
            )
            return None

    def prepare_location_callback_payload(
        self, subscription, notification_from_db
    ):

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
            id=str(notification_from_db.id),
            source=Constants.GEONFENCING_NOTIFICATION_SOURCE,
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

    def store_location_notification_output_in_db(
        self, notification_id, error_message
    ):
        # if error message -> notification unsuccessful
        # if no error message -> notification successful
        crud.update_device_location_subscription_notification(
            db=self.db,
            notification_id=notification_id,
            sucess=error_message is None,
            error=error_message
        )

    def send_and_record_device_status_notification(self, subscription):

        logging.info(
            "Sending notification to " +
            f"{subscription.webhook.notification_url}. This notification " +
            "is realated with a " +
            f"{subscription.device_status_subscription_type.value} event."
        )

        # First, we have to register this new notification
        notification_from_db = crud\
            .create_device_status_subscription_notification(
                db=self.db,
                subscription_id=subscription.subscription_id,
            )

        try:
            callback_payload = self.prepare_device_status_callback_payload(
                subscription,
                notification_from_db
            )

            # Tweak the callback payload
            callback_payload = callback_payload.model_dump()
            callback_payload["type"] = callback_payload["type"].value
            callback_payload["time"] = callback_payload["time"]\
                .strftime("%Y-%m-%dT%H:%M:%S.%fZ")

            response = requests.post(
                url=subscription.webhook.notification_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " +
                    subscription.webhook.notification_auth_token
                },
                json=callback_payload,
                timeout=15
            )
            # Raises an HTTPError for bad responses (4xx and 5xx)
            response.raise_for_status()
            logging.info(
                f"Notification to {subscription.webhook.notification_url} " +
                "was successful."
            )

            # Store results in DB
            self.store_device_status_notification_output_in_db(
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
            self.store_device_status_notification_output_in_db(
                notification_id=notification_from_db.id,
                error_message=str(exception)
            )
            return None

    def prepare_device_status_callback_payload(
        self, subscription, notification_from_db
    ):
        # Get the device information
        simulation_device = crud.get_simulated_device_from_id(
            db=self.db,
            device_id=subscription.ue
        )

        cloud_event = DeviceStatusSchemas.CloudEvent(
            id=str(notification_from_db.id),
            source=Constants.DEVICE_STATUS_NOTIFICATION_SOURCE,
            type=subscription.device_status_subscription_type,
            specversion="1.0",
            datacontenttype="application/json",
            time=datetime.utcnow(),
            data={
                "device": {"phoneNumber": simulation_device.phone_number},
                "subscriptionId": subscription.subscription_id,
            }
        )

        if subscription.device_status_subscription_type == \
                DeviceStatusSchemas.SubscriptionEventType.ROAMING_STATUS:
            cloud_event.data["device"]["roaming"] = subscription\
                .current_roaming
            cloud_event.data["device"]["countryCode"] = subscription\
                .current_country_code
            cloud_event.data["device"]["countryName"] = subscription\
                .current_country_name
        elif subscription.device_status_subscription_type == \
                DeviceStatusSchemas.SubscriptionEventType\
                .ROAMING_CHANGE_COUNTRY:
            cloud_event.data["device"]["countryCode"] = subscription\
                .current_country_code

        return cloud_event

    def store_device_status_notification_output_in_db(
        self, notification_id, error_message
    ):
        # if error message -> notification unsuccessful
        # if no error message -> notification successful
        crud.update_device_status_subscription_notification(
            db=self.db,
            notification_id=notification_id,
            sucess=error_message is None,
            error=error_message
        )
