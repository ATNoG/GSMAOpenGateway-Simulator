# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-19 19:04:36
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-23 17:38:24
import pytest
from unittest.mock import call
import config # noqa
from datetime import datetime, timedelta
from geofencing_subscriptions_manager import GeofencingSubscriptionsManager
from common.subscriptions.subscription_types import SubscriptionType
from common.simulation.simulation_types import SimulationType
from notifications import Notifications
from common.message_broker.schemas import (
    SimulationData,
    GeofencingSubscription,
    DeviceLocationSimulationData
)
import constants as Constants
from common.apis.device_location_schemas import (
    SubscriptionEventType,
    Circle,
    Webhook,
    Point,
    CloudEvent
)
from common.database import models
import json


def get_simulated_data():
    strftime_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    return [
        SimulationData(
            simulation_id=1,
            simulation_instance_id=1,
            child_simulation_instance_id=1,
            simulation_type=SimulationType.DEVICE_LOCATION,
            data=DeviceLocationSimulationData(
                ue=1,
                ue_instance=1,
                latitude=32.67809867905849,
                longitude=-17.622633942472735,
                timestamp=datetime.utcnow().strftime(strftime_format)
            ).__dict__
        ),
        SimulationData(
            simulation_id=1,
            simulation_instance_id=1,
            child_simulation_instance_id=1,
            simulation_type=SimulationType.DEVICE_LOCATION,
            data=DeviceLocationSimulationData(
                ue=1,
                ue_instance=1,
                latitude=32.77298854063671,
                longitude=-17.13037010791792,
                timestamp=datetime.utcnow().strftime(strftime_format)
            ).__dict__
        ),
        SimulationData(
            simulation_id=1,
            simulation_instance_id=1,
            child_simulation_instance_id=1,
            simulation_type=SimulationType.DEVICE_LOCATION,
            data=DeviceLocationSimulationData(
                ue=1,
                ue_instance=1,
                latitude=32.44551578131866,
                longitude=-17.259338468442383,
                timestamp=datetime.utcnow().strftime(strftime_format)
            ).__dict__
        ),
        SimulationData(
            simulation_id=1,
            simulation_instance_id=1,
            child_simulation_instance_id=1,
            simulation_type=SimulationType.DEVICE_LOCATION,
            data=DeviceLocationSimulationData(
                ue=1,
                ue_instance=1,
                latitude=32.69540592103866,
                longitude=-16.99218572668454,
                timestamp=datetime.utcnow().strftime(strftime_format)
            ).__dict__
        ),
        SimulationData(
            simulation_id=1,
            simulation_instance_id=1,
            child_simulation_instance_id=1,
            simulation_type=SimulationType.DEVICE_LOCATION,
            data=DeviceLocationSimulationData(
                ue=1,
                ue_instance=1,
                latitude=32.73397576083184,
                longitude=-16.824103575407136,
                timestamp=datetime.utcnow().strftime(strftime_format)
            ).__dict__
        ),
        SimulationData(
            simulation_id=1,
            simulation_instance_id=1,
            child_simulation_instance_id=1,
            simulation_type=SimulationType.DEVICE_LOCATION,
            data=DeviceLocationSimulationData(
                ue=1,
                ue_instance=1,
                latitude=32.316487028304884,
                longitude=-16.50248551307069,
                timestamp=datetime.utcnow().strftime(strftime_format)
            ).__dict__
        )
    ]


def test_if_area_related_events_are_being_triggered(mocker):
    area_entered_geofencing_subscription = GeofencingSubscription(
        subscription_id="1",
        subscription_type=SubscriptionType.DEVICE_LOCATION_GEOFENCING,
        simulation_id=1,
        area=Circle(
            center=Point(
                latitude=32.74513588903821,
                longitude=-17.0078912128889
            ),
            radius=22.84*1000
        ),
        geofencing_subscription_type=SubscriptionEventType.AREA_ENTERED,
        ue=1,
        webhook=Webhook(
            notification_url='https://webhook.site/44623dab-5634-46cc-a5ff-' +
            'd9f1828057e8',
            notification_auth_token='c8974e592c2fa383d4a3960714'
        ),
        expire_time=datetime.utcnow() + timedelta(minutes=2),
    )

    area_left_geofencing_subscription = GeofencingSubscription(
        subscription_id="2",
        subscription_type=SubscriptionType.DEVICE_LOCATION_GEOFENCING,
        simulation_id=1,
        area=Circle(
            center=Point(
                latitude=32.74513588903821,
                longitude=-17.0078912128889
            ),
            radius=22.84*1000
        ),
        geofencing_subscription_type=SubscriptionEventType.AREA_LEFT,
        ue=1,
        webhook=Webhook(
            notification_url='https://webhook.site/44623dab-5634-46cc-a5ff-' +
            'd9f1828057e8',
            notification_auth_token='c8974e592c2fa383d4a3960714'
        ),
        expire_time=datetime.utcnow() + timedelta(minutes=2),
    )

    simulated_data = get_simulated_data()

    # Expected behavior
    # UE Positions
    # 1 -> Outside Area (area-left)
    # 2 -> Inside Area (area-entered)
    # 3 -> Outside Area (area-left)
    # 4 -> Inside Area (area-entered)
    # 5 -> Inside Area
    # 6 -> Outside Area (area-left)

    # Expected notifications
    # 2 area-entered
    # 3 area-left
    # 5 in total

    # Set mocks
    notifications_mock = mocker.patch(
        target="notifications.Notifications.send_and_record_notification",
        return_value=True
    )

    # Create Geofencing Subscriptions Manager
    geo_subs_manager = GeofencingSubscriptionsManager()

    # Add two test subscriptions
    geo_subs_manager.add_subscription(area_entered_geofencing_subscription)
    geo_subs_manager.add_subscription(area_left_geofencing_subscription)

    # Simualte that UE device location simulation data is arriving
    for simulation_data in simulated_data:
        geo_subs_manager.handle_ue_location_message(
            simulation_data=simulation_data
        )

    # Assert that the noficiation method was called 5 times
    assert notifications_mock.call_count == 5

    # Assert the order of the different calls to that method
    expected_calls = [
        call(area_left_geofencing_subscription),
        call(area_entered_geofencing_subscription),
        call(area_left_geofencing_subscription),
        call(area_entered_geofencing_subscription),
        call(area_left_geofencing_subscription)
    ]
    notifications_mock.assert_has_calls(
        expected_calls, any_order=False
    )


@pytest.mark.parametrize(
    'subscription, expected_return',
    [
        (
            GeofencingSubscription(
                subscription_id="1",
                subscription_type=SubscriptionType.DEVICE_LOCATION_GEOFENCING,
                simulation_id=1,
                area=Circle(
                    center=Point(
                        latitude=32.74513588903821,
                        longitude=-17.0078912128889
                    ),
                    radius=22.84*1000
                ),
                geofencing_subscription_type=SubscriptionEventType
                .AREA_ENTERED,
                ue=1,
                webhook=Webhook(
                    notification_url='https://webhook.site/44623dab-5634-' +
                    '46cc-a5ff-d9f1828057e8',
                    notification_auth_token=''
                ),
                expire_time=datetime.utcnow(),
            ),
            CloudEvent(
                id="10",
                source=Constants.NOTIFICATION_SOURCE,
                type=SubscriptionEventType.AREA_ENTERED,
                specversion="1.0",
                datacontenttype="application/json",
                time=datetime.utcnow(),
                data={
                    "subscriptionId": "1",
                    "device": {
                        'phone_number': '987654321',
                        'network_access_identifier': '987654321@domain.com',
                        'ipv4_address': {
                            'public_address': '10.93.125.84',
                            'private_address': '10.10.10.84',
                            'public_port': 56795
                        },
                        'ipv6_address': '2001:db6:85a3:8d3:1319:8a2e:111:7344'
                    },
                    "area": {
                        'area_type': 'circle',
                        'center': {
                            'latitude': 32.74513588903821,
                            'longitude': -17.0078912128889
                        },
                        'radius': 22840.0
                    }
                }
            )
        ),
        (
            GeofencingSubscription(
                subscription_id="2",
                subscription_type=SubscriptionType.DEVICE_LOCATION_GEOFENCING,
                simulation_id=1,
                area=Circle(
                    center=Point(
                        latitude=32.74513588903821,
                        longitude=-17.0078912128889
                    ),
                    radius=22.84*1000
                ),
                geofencing_subscription_type=SubscriptionEventType
                .AREA_ENTERED,
                ue=1,
                webhook=Webhook(
                    notification_url='https://aklsjdklh.site/44623dab-5634-' +
                    '46cc-a5ff-d9f1828057e8',
                    notification_auth_token=''
                ),
                expire_time=datetime.utcnow(),
            ),
            None
        )
    ]
)
def test_if_area_related_events_notifications(
    subscription, expected_return, mocker
):
    # Prepare Mocks
    create_db_notification_mock = mocker.patch(
        target="common.database.crud." +
        "create_device_location_subscription_notification",
        return_value=models.DeviceLocationSubscriptionNotification(
            id="10",
            subscription_id=int(subscription.subscription_id)
        )
    )

    get_ue_from_db_mock = mocker.patch(
        target="common.database.crud." +
        "get_simulated_device_from_id",
        return_value=models.SimulationUE(
            id=subscription.ue,
            root_simulation=subscription.simulation_id,
            phone_number="987654321",
            network_access_identifier="987654321@domain.com",
            ipv4_address_public_address="10.93.125.84",
            ipv4_address_private_address="10.10.10.84",
            ipv4_address_public_port=56795,
            ipv6_address="2001:db6:85a3:8d3:1319:8a2e:111:7344"
        )
    )

    update_subscription_notification_mock = mocker.patch(
        target="common.database.crud." +
        "update_device_location_subscription_notification",
        return_value=models.DeviceLocationSubscriptionNotification(
            id="10",
            subscription_id=int(subscription.subscription_id),
            sucess=expected_return
        )
    )

    notifications = Notifications(None)
    ret = notifications.send_and_record_notification(subscription)

    # The times will be defined according to the object's time of creation
    # As such, one should avoid to compare these times on this test. Thus,
    # before comparing the expected response and the actual one, we set the
    # 'time' argument to None, on both.
    if expected_return:
        ret["time"] = None
        expected_return.time = None
        # Expected Return to json
        expected_return_json = expected_return.model_dump()
        expected_return_json["type"] = expected_return_json["type"].value
        expected_return_json = json.dumps(expected_return_json)
        # Actual Return to json
        ret_json = json.dumps(ret)
        assert ret_json == expected_return_json
    else:
        assert ret == expected_return

    assert create_db_notification_mock.call_count == 1
    assert get_ue_from_db_mock.call_count == 1
    assert update_subscription_notification_mock.call_count == 1
