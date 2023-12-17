# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-06 22:16:14
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-12 22:49:48

TEST_SIMULATIONS = [ 
    {
        "UEs": {
            "UE1": {
                    "id": "UE1",
                    "phone_number": "123456789",
                    "network_access_identifier": "123456789@domain.com",
                    "ipv4_address": {
                        "public_address": "84.125.93.10",
                        "public_port": 59765
                    },
                    "ipv6_address": "2001:db8:85a3:8d3:1319:8a2e:370:7344"
                },
        },
        "device_location": {
            "simulations": [
                {
                    "UEs": [
                        "UE1"
                    ],
                    "duration": 20,
                    "stops": [
                        {
                            "label": "Reitoria UA",
                            "lat": 40.631649455486816,
                            "long": -8.657374926386364
                        },
                        {
                            "label": "Autocarro Bar",
                            "lat": 40.63442687018253,
                            "long": -8.657574824707662
                        },
                        {
                            "label": "Hospital Aveiro",
                            "lat": 40.635236027955024,
                            "long": -8.65590872154504
                        },
                        {
                            "label": "Cadeia Aveiro",
                            "lat": 40.6368880975912,
                            "long": -8.65708611819683
                        },
                        {
                            "label": "Fábrica da Ciencia Viva",
                            "lat": 40.63777642283235,
                            "long": -8.658646959356998
                        },
                        {
                            "label": "Rua da Pega",
                            "lat": 40.62952643772836,
                            "long": -8.65991719738882
                        },
                        {
                            "label": "STIC UA",
                            "lat": 40.62960224117823,
                            "long": -8.658517543642327
                        },
                        {
                            "label": "Aristides Hall",
                            "lat": 40.62991505139128,
                            "long": -8.65486302112794
                        },
                        {
                            "label": "Ponte Crasto",
                            "lat": 40.62852357440743, 
                            "long": -8.656242006868082
                        },
                        {
                            "label": "Residências UA",
                            "lat": 40.63121656259592, 
                            "long": -8.656323498254093
                        },
                        {
                            "label": "Reitoria UA",
                            "lat": 40.631649455486816,
                            "long": -8.657374926386364
                        }
                    ]         
                }
            ]
        }
    },
    {
        "UEs": {
                "UE1": {
                    "id": "UE1",
                    "phone_number": "123456789",
                    "network_access_identifier": "123456789@domain.com",
                    "ipv4_address": {
                        "public_address": "84.125.93.10",
                        "public_port": 59765
                    },
                    "ipv6_address": "2001:db8:85a3:8d3:1319:8a2e:370:7344"
                },
                "UE2": {
                    "id": "UE2",
                    "phone_number": "987654321",
                    "network_access_identifier": "987654321@domain.com",
                    "ipv4_address": {
                        "public_address": "10.93.125.84",
                        "public_port": 56795
                    },
                    "ipv6_address": "2001:db6:85a3:8d3:1319:8a2e:111:7344"
                },
                "UE3": {
                    "id": "UE3",
                    "phone_number": "987654320",
                    "network_access_identifier": "987654320@domain.com",
                    "ipv4_address": {
                        "public_address": "10.93.125.88",
                        "public_port": 27614
                    },
                    "ipv6_address": "2000:db6:85a3:8d3:1319:8a2e:111:7344"
                }
        },
        "device_location": {
            "simulations": [
                {
                    "UEs": [
                        "UE1"
                    ],
                    "duration": 20,
                    "stops": [
                        {
                            "label": "Reitoria UA",
                            "lat": 40.631649455486816,
                            "long": -8.657374926386364
                        },
                        {
                            "label": "Autocarro Bar",
                            "lat": 40.63442687018253,
                            "long": -8.657574824707662
                        },
                        {
                            "label": "Hospital Aveiro",
                            "lat": 40.635236027955024,
                            "long": -8.65590872154504
                        },
                        {
                            "label": "Cadeia Aveiro",
                            "lat": 40.6368880975912,
                            "long": -8.65708611819683
                        },
                        {
                            "label": "Fábrica da Ciencia Viva",
                            "lat": 40.63777642283235,
                            "long": -8.658646959356998
                        },
                        {
                            "label": "Rua da Pega",
                            "lat": 40.62952643772836,
                            "long": -8.65991719738882
                        },
                        {
                            "label": "STIC UA",
                            "lat": 40.62960224117823,
                            "long": -8.658517543642327
                        },
                        {
                            "label": "Aristides Hall",
                            "lat": 40.62991505139128,
                            "long": -8.65486302112794
                        },
                        {
                            "label": "Ponte Crasto",
                            "lat": 40.62852357440743, 
                            "long": -8.656242006868082
                        },
                        {
                            "label": "Residências UA",
                            "lat": 40.63121656259592, 
                            "long": -8.656323498254093
                        },
                        {
                            "label": "Reitoria UA",
                            "lat": 40.631649455486816,
                            "long": -8.657374926386364
                        }
                    ]     
                },
                {
                    "UEs": [
                        "UE2",
                        "UE3"
                    ],
                    "duration": 60,
                    "stops": [
                        {
                            "label": "Hospital Aveiro",
                            "lat": 40.635236027955024,
                            "long": -8.65590872154504
                        },
                        {
                            "label": "Cadeia Aveiro",
                            "lat": 40.6368880975912,
                            "long": -8.65708611819683
                        },
                        {
                            "label": "Fábrica da Ciencia Viva",
                            "lat": 40.63777642283235,
                            "long": -8.658646959356998
                        },
                        {
                            "label": "Rua da Pega",
                            "lat": 40.62952643772836,
                            "long": -8.65991719738882
                        },
                        {
                            "label": "STIC UA",
                            "lat": 40.62960224117823,
                            "long": -8.658517543642327
                        }
                    ]         
                }
            ]
        }
    }
]