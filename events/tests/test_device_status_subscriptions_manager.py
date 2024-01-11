# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-19 19:04:36
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2024-01-11 11:47:16
import pytest
import config # noqa
from datetime import datetime, timedelta
from common.subscriptions.subscription_types import SubscriptionType
from common.simulation.simulation_types import SimulationType
from notifications import Notifications
import json
from common.message_broker.schemas import (
    SimulationData,
    DeviceStatusSimulationData
)
import constants as Constants
from common.database import models
from common.subscriptions.schemas import DeviceStatusSubscription
from device_status_subscriptions_manager import \
    DeviceStatusSubscriptionsManager
from common.apis.device_status_schemas import (
    SubscriptionEventType,
    Webhook,
    CloudEvent
)


def get_simulated_data():
    return [
        SimulationData(
            simulation_id=1,
            simulation_instance_id=1,
            child_simulation_instance_id=1,
            simulation_type=SimulationType.DEVICE_STATUS,
            data=DeviceStatusSimulationData(
                ue=10,
                ue_instance=1120,
                connectivity_status="NOT_CONNECTED",
                roaming=None,
                country_code=None,
                country_name=None,
                timestamp=datetime.utcnow()
            ).__dict__
        ),
        SimulationData(
            simulation_id=1,
            simulation_instance_id=1,
            child_simulation_instance_id=1,
            simulation_type=SimulationType.DEVICE_STATUS,
            data=DeviceStatusSimulationData(
                ue=10,
                ue_instance=1120,
                connectivity_status="CONNECTED_SMS",
                roaming=None,
                country_code=None,
                country_name=None,
                timestamp=datetime.utcnow()
            ).__dict__
        ),
        SimulationData(
            simulation_id=1,
            simulation_instance_id=1,
            child_simulation_instance_id=1,
            simulation_type=SimulationType.DEVICE_STATUS,
            data=DeviceStatusSimulationData(
                ue=10,
                ue_instance=1120,
                connectivity_status="CONNECTED_DATA",
                roaming=None,
                country_code=None,
                country_name=None,
                timestamp=datetime.utcnow()
            ).__dict__
        ),
        SimulationData(
            simulation_id=1,
            simulation_instance_id=1,
            child_simulation_instance_id=1,
            simulation_type=SimulationType.DEVICE_STATUS,
            data=DeviceStatusSimulationData(
                ue=10,
                ue_instance=1120,
                connectivity_status="NOT_CONNECTED",
                roaming=None,
                country_code=None,
                country_name=None,
                timestamp=datetime.utcnow()
            ).__dict__
        ),
        SimulationData(
            simulation_id=1,
            simulation_instance_id=1,
            child_simulation_instance_id=1,
            simulation_type=SimulationType.DEVICE_STATUS,
            data=DeviceStatusSimulationData(
                ue=10,
                ue_instance=1120,
                connectivity_status="NOT_CONNECTED",
                roaming=True,
                country_code=None,
                country_name=None,
                timestamp=datetime.utcnow()
            ).__dict__
        ),
        SimulationData(
            simulation_id=1,
            simulation_instance_id=1,
            child_simulation_instance_id=1,
            simulation_type=SimulationType.DEVICE_STATUS,
            data=DeviceStatusSimulationData(
                ue=10,
                ue_instance=1120,
                connectivity_status="NOT_CONNECTED",
                roaming=False,
                country_code=None,
                country_name=None,
                timestamp=datetime.utcnow()
            ).__dict__
        ),
        SimulationData(
            simulation_id=1,
            simulation_instance_id=1,
            child_simulation_instance_id=1,
            simulation_type=SimulationType.DEVICE_STATUS,
            data=DeviceStatusSimulationData(
                ue=10,
                ue_instance=1120,
                connectivity_status="NOT_CONNECTED",
                roaming=None,
                country_code=351,
                country_name=None,
                timestamp=datetime.utcnow()
            ).__dict__
        ),
        SimulationData(
            simulation_id=1,
            simulation_instance_id=1,
            child_simulation_instance_id=1,
            simulation_type=SimulationType.DEVICE_STATUS,
            data=DeviceStatusSimulationData(
                ue=10,
                ue_instance=1120,
                connectivity_status="NOT_CONNECTED",
                roaming=None,
                country_code=34,
                country_name=None,
                timestamp=datetime.utcnow()
            ).__dict__
        )
    ]


@pytest.mark.parametrize(
    'subscriptions, expected_call_count',
    [
        (
            [
                DeviceStatusSubscription(
                    simulation_id=1,
                    subscription_id="a",
                    subscription_type=SubscriptionType.DEVICE_STATUS,
                    device_status_subscription_type=SubscriptionEventType
                    .CONNECTIVITY_DATA,
                    ue=10,
                    webhook=Webhook(
                        notification_url='https://webhook.site/44623dab-' +
                        '5634-46cc-a5ff-d9f1828057e8',
                        notification_auth_token=''
                    ),
                    expire_time=datetime.utcnow() + timedelta(minutes=10),
                    current_connectivity_status="NOT_CONNECTED",
                    current_country_code=351,
                    current_roaming=False,
                    current_country_name=[]
                ),
                DeviceStatusSubscription(
                    simulation_id=1,
                    subscription_id="b",
                    subscription_type=SubscriptionType.DEVICE_STATUS,
                    device_status_subscription_type=SubscriptionEventType
                    .CONNECTIVITY_DISCONNECTED,
                    ue=10,
                    webhook=Webhook(
                        notification_url='https://webhook.site/44623dab-' +
                        '5634-46cc-a5ff-d9f1828057e8',
                        notification_auth_token=''
                    ),
                    expire_time=datetime.utcnow() + timedelta(minutes=10),
                    current_connectivity_status="NOT_CONNECTED",
                    current_country_code=351,
                    current_roaming=False,
                    current_country_name=[]
                ),
                DeviceStatusSubscription(
                    simulation_id=1,
                    subscription_id="b",
                    subscription_type=SubscriptionType.DEVICE_STATUS,
                    device_status_subscription_type=SubscriptionEventType
                    .CONNECTIVITY_SMS,
                    ue=10,
                    webhook=Webhook(
                        notification_url='https://webhook.site/44623dab-' +
                        '5634-46cc-a5ff-d9f1828057e8',
                        notification_auth_token=''
                    ),
                    expire_time=datetime.utcnow() + timedelta(minutes=10),
                    current_connectivity_status="NOT_CONNECTED",
                    current_country_code=351,
                    current_roaming=False,
                    current_country_name=[]
                )
            ],
            3
        ),
        (
            [
                DeviceStatusSubscription(
                    simulation_id=1,
                    subscription_id="a",
                    subscription_type=SubscriptionType.DEVICE_STATUS,
                    device_status_subscription_type=SubscriptionEventType
                    .CONNECTIVITY_DATA,
                    ue=10,
                    webhook=Webhook(
                        notification_url='https://webhook.site/44623dab-' +
                        '5634-46cc-a5ff-d9f1828057e8',
                        notification_auth_token=''
                    ),
                    expire_time=datetime.utcnow() + timedelta(minutes=10),
                    current_connectivity_status="NOT_CONNECTED",
                    current_country_code=351,
                    current_roaming=False,
                    current_country_name=[]
                )
            ],
            1
        ),
        (
            [
                DeviceStatusSubscription(
                    simulation_id=1,
                    subscription_id="a",
                    subscription_type=SubscriptionType.DEVICE_STATUS,
                    device_status_subscription_type=SubscriptionEventType
                    .ROAMING_ON,
                    ue=10,
                    webhook=Webhook(
                        notification_url='https://webhook.site/44623dab-' +
                        '5634-46cc-a5ff-d9f1828057e8',
                        notification_auth_token=''
                    ),
                    expire_time=datetime.utcnow() + timedelta(minutes=10),
                    current_connectivity_status="NOT_CONNECTED",
                    current_country_code=351,
                    current_roaming=False,
                    current_country_name=[]
                ),
                DeviceStatusSubscription(
                    simulation_id=1,
                    subscription_id="a",
                    subscription_type=SubscriptionType.DEVICE_STATUS,
                    device_status_subscription_type=SubscriptionEventType
                    .ROAMING_OFF,
                    ue=10,
                    webhook=Webhook(
                        notification_url='https://webhook.site/44623dab-' +
                        '5634-46cc-a5ff-d9f1828057e8',
                        notification_auth_token=''
                    ),
                    expire_time=datetime.utcnow() + timedelta(minutes=10),
                    current_connectivity_status="NOT_CONNECTED",
                    current_country_code=351,
                    current_roaming=False,
                    current_country_name=[]
                )
            ],
            2
        ),
        (
            [
                DeviceStatusSubscription(
                    simulation_id=1,
                    subscription_id="a",
                    subscription_type=SubscriptionType.DEVICE_STATUS,
                    device_status_subscription_type=SubscriptionEventType
                    .ROAMING_ON,
                    ue=10,
                    webhook=Webhook(
                        notification_url='https://webhook.site/44623dab-' +
                        '5634-46cc-a5ff-d9f1828057e8',
                        notification_auth_token=''
                    ),
                    expire_time=datetime.utcnow() + timedelta(minutes=10),
                    current_connectivity_status="NOT_CONNECTED",
                    current_country_code=351,
                    current_roaming=False,
                    current_country_name=[]
                ),
                DeviceStatusSubscription(
                    simulation_id=1,
                    subscription_id="a",
                    subscription_type=SubscriptionType.DEVICE_STATUS,
                    device_status_subscription_type=SubscriptionEventType
                    .ROAMING_OFF,
                    ue=10,
                    webhook=Webhook(
                        notification_url='https://webhook.site/44623dab-' +
                        '5634-46cc-a5ff-d9f1828057e8',
                        notification_auth_token=''
                    ),
                    expire_time=datetime.utcnow() + timedelta(minutes=10),
                    current_connectivity_status="NOT_CONNECTED",
                    current_country_code=351,
                    current_roaming=False,
                    current_country_name=[]
                ),
                DeviceStatusSubscription(
                    simulation_id=1,
                    subscription_id="a",
                    subscription_type=SubscriptionType.DEVICE_STATUS,
                    device_status_subscription_type=SubscriptionEventType
                    .ROAMING_OFF,
                    ue=10,
                    webhook=Webhook(
                        notification_url='https://webhook.site/44623dab-' +
                        '5634-46cc-a5ff-d9f1828057e8',
                        notification_auth_token=''
                    ),
                    expire_time=datetime.utcnow() + timedelta(minutes=10),
                    current_connectivity_status="NOT_CONNECTED",
                    current_country_code=351,
                    current_roaming=False,
                    current_country_name=[]
                )
            ],
            3
        ),
        (
            [
                DeviceStatusSubscription(
                    simulation_id=1,
                    subscription_id="a",
                    subscription_type=SubscriptionType.DEVICE_STATUS,
                    device_status_subscription_type=SubscriptionEventType
                    .ROAMING_STATUS,
                    ue=10,
                    webhook=Webhook(
                        notification_url='https://webhook.site/44623dab-' +
                        '5634-46cc-a5ff-d9f1828057e8',
                        notification_auth_token=''
                    ),
                    expire_time=datetime.utcnow() + timedelta(minutes=10),
                    current_connectivity_status="NOT_CONNECTED",
                    current_country_code=351,
                    current_roaming=False,
                    current_country_name=[]
                )
            ],
            2
        ),
        (
            [
                DeviceStatusSubscription(
                    simulation_id=1,
                    subscription_id="a",
                    subscription_type=SubscriptionType.DEVICE_STATUS,
                    device_status_subscription_type=SubscriptionEventType
                    .ROAMING_CHANGE_COUNTRY,
                    ue=10,
                    webhook=Webhook(
                        notification_url='https://webhook.site/44623dab-' +
                        '5634-46cc-a5ff-d9f1828057e8',
                        notification_auth_token=''
                    ),
                    expire_time=datetime.utcnow() + timedelta(minutes=10),
                    current_connectivity_status="NOT_CONNECTED",
                    current_country_code=000,
                    current_roaming=False,
                    current_country_name=[]
                )
            ],
            2
        )
    ]
)
def test_notification_method_is_being_called(
    subscriptions, expected_call_count, mocker
):
    # Prepare Mocks
    get_subscriptions_mock = mocker.patch(
        target="device_status_subscriptions_manager." +
        "DeviceStatusSubscriptionsManager.get_subscriptions",
        return_value=subscriptions
    )

    notifications_mock = mocker.patch(
        target="notifications.Notifications.send_and_record_device_status_" +
        "notification",
        return_value=True
    )

    # Create DeviceStatusSubscriptionsManager and get simulation data
    device_status_subs_manager = DeviceStatusSubscriptionsManager()
    simulated_data = get_simulated_data()

    # Simualte that UE device status simulation data is arriving
    for simulation_data in simulated_data:
        device_status_subs_manager.handle_ue_status_message(
            simulation_data=simulation_data
        )

    # Assert that the noficiation method was called X time
    assert notifications_mock.call_count == expected_call_count
    # Assert that the get subscriptions method was called once per simulation
    # data
    assert get_subscriptions_mock.call_count == len(simulated_data)


@pytest.mark.parametrize(
    'subscription, expected_return',
    [
        (
            DeviceStatusSubscription(
                subscription_id="1",
                subscription_type=SubscriptionType.DEVICE_STATUS,
                simulation_id=1,
                device_status_subscription_type=SubscriptionEventType
                .ROAMING_STATUS,
                ue=1,
                webhook=Webhook(
                    notification_url='https://webhook.site/44623dab-5634-' +
                    '46cc-a5ff-d9f1828057e8',
                    notification_auth_token=''
                ),
                expire_time=datetime.utcnow() + timedelta(minutes=10),
                current_connectivity_status="NOT_CONNECTED",
                current_country_code=34,
                current_roaming=True,
                current_country_name=['ES']
            ),
            CloudEvent(
                id="10",
                source=Constants.DEVICE_STATUS_NOTIFICATION_SOURCE,
                type=SubscriptionEventType.ROAMING_STATUS,
                specversion="1.0",
                datacontenttype="application/json",
                time=datetime.utcnow(),
                data={
                    "device": {
                        'phoneNumber': '987654321',
                        'roaming': True,
                        'countryCode': 34,
                        'countryName': ['ES']
                    },
                    "subscriptionId": "1"
                }
            )
        ),
        (
            DeviceStatusSubscription(
                subscription_id="1",
                subscription_type=SubscriptionType.DEVICE_STATUS,
                simulation_id=1,
                device_status_subscription_type=SubscriptionEventType
                .ROAMING_ON,
                ue=1,
                webhook=Webhook(
                    notification_url='https://webhook.site/44623dab-5634-' +
                    '46cc-a5ff-d9f1828057e8',
                    notification_auth_token=''
                ),
                expire_time=datetime.utcnow() + timedelta(minutes=10),
                current_connectivity_status="NOT_CONNECTED",
                current_country_code=34,
                current_roaming=True,
                current_country_name=['ES']
            ),
            CloudEvent(
                id="10",
                source=Constants.DEVICE_STATUS_NOTIFICATION_SOURCE,
                type=SubscriptionEventType.ROAMING_ON,
                specversion="1.0",
                datacontenttype="application/json",
                time=datetime.utcnow(),
                data={
                    "device": {
                        'phoneNumber': '987654321',
                    },
                    "subscriptionId": "1"
                }
            )
        ),
        (
            DeviceStatusSubscription(
                subscription_id="1",
                subscription_type=SubscriptionType.DEVICE_STATUS,
                simulation_id=1,
                device_status_subscription_type=SubscriptionEventType
                .CONNECTIVITY_DATA,
                ue=1,
                webhook=Webhook(
                    notification_url='https://webhook.site/44623dab-5634-' +
                    '46cc-a5ff-d9f1828057e8',
                    notification_auth_token=''
                ),
                expire_time=datetime.utcnow() + timedelta(minutes=10),
                current_connectivity_status="CONNECTED_DATA",
                current_country_code=34,
                current_roaming=True,
                current_country_name=['ES']
            ),
            CloudEvent(
                id="10",
                source=Constants.DEVICE_STATUS_NOTIFICATION_SOURCE,
                type=SubscriptionEventType.CONNECTIVITY_DATA,
                specversion="1.0",
                datacontenttype="application/json",
                time=datetime.utcnow(),
                data={
                    "device": {
                        'phoneNumber': '987654321',
                    },
                    "subscriptionId": "1"
                }
            )
        ),
        (
            DeviceStatusSubscription(
                subscription_id="1",
                subscription_type=SubscriptionType.DEVICE_STATUS,
                simulation_id=1,
                device_status_subscription_type=SubscriptionEventType
                .ROAMING_CHANGE_COUNTRY,
                ue=1,
                webhook=Webhook(
                    notification_url='https://webhook.site/44623dab-5634-' +
                    '46cc-a5ff-d9f1828057e8',
                    notification_auth_token=''
                ),
                expire_time=datetime.utcnow() + timedelta(minutes=10),
                current_connectivity_status="NOT_CONNECTED",
                current_country_code=34,
                current_roaming=True,
                current_country_name=['ES']
            ),
            CloudEvent(
                id="10",
                source=Constants.DEVICE_STATUS_NOTIFICATION_SOURCE,
                type=SubscriptionEventType.ROAMING_CHANGE_COUNTRY,
                specversion="1.0",
                datacontenttype="application/json",
                time=datetime.utcnow(),
                data={
                    "device": {
                        'phoneNumber': '987654321',
                        'countryCode': 34,
                    },
                    "subscriptionId": "1"
                }
            )
        ),
    ]
)
def test_notifications_payload(
    subscription, expected_return, mocker
):
    # Prepare Mocks
    create_db_notification_mock = mocker.patch(
        target="common.database.crud." +
        "create_device_status_subscription_notification",
        return_value=models.DeviceStatusSubscriptionNotification(
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
        "update_device_status_subscription_notification",
        return_value=models.DeviceStatusSubscriptionNotification(
            id="10",
            subscription_id=int(subscription.subscription_id),
            sucess=expected_return
        )
    )

    notifications = Notifications(None)
    ret = notifications.send_and_record_device_status_notification(
        subscription
    )

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
