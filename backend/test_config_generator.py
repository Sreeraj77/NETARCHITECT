from config_generator.cisco_generator import (
    generate_all_configurations
)


test_plan = {
    "architecture": "Hierarchical",
    "topology": "Extended Star",
    "routing_protocol": "OSPF",

    "vlans": [
        {
            "vlan_id": 10,
            "name": "CSE",
            "purpose": "CSE Department",
            "estimated_users": 100
        },
        {
            "vlan_id": 20,
            "name": "ECE",
            "purpose": "ECE Department",
            "estimated_users": 100
        },
        {
            "vlan_id": 30,
            "name": "EEE",
            "purpose": "EEE Department",
            "estimated_users": 100
        },
        {
            "vlan_id": 40,
            "name": "ME",
            "purpose": "ME Department",
            "estimated_users": 100
        },
        {
            "vlan_id": 50,
            "name": "CE",
            "purpose": "CE Department",
            "estimated_users": 100
        }
    ],

    "ip_networks": [
        {
            "network": "10.10.0.0/24",
            "subnet_mask": "255.255.255.0",
            "gateway": "10.10.0.1",
            "vlan_id": 10
        },
        {
            "network": "10.20.0.0/24",
            "subnet_mask": "255.255.255.0",
            "gateway": "10.20.0.1",
            "vlan_id": 20
        },
        {
            "network": "10.30.0.0/24",
            "subnet_mask": "255.255.255.0",
            "gateway": "10.30.0.1",
            "vlan_id": 30
        },
        {
            "network": "10.40.0.0/24",
            "subnet_mask": "255.255.255.0",
            "gateway": "10.40.0.1",
            "vlan_id": 40
        },
        {
            "network": "10.50.0.0/24",
            "subnet_mask": "255.255.255.0",
            "gateway": "10.50.0.1",
            "vlan_id": 50
        }
    ],

    "devices": [
        {
            "device_type": "Core Switch",
            "quantity": 1
        },
        {
            "device_type": "Distribution Switch",
            "quantity": 2
        },
        {
            "device_type": "Access Switch",
            "quantity": 11
        },
        {
            "device_type": "Wireless Access Point",
            "quantity": 10
        },
        {
            "device_type": "Firewall",
            "quantity": 1
        },
        {
            "device_type": "Internet Router",
            "quantity": 1
        }
    ]
}


configurations = generate_all_configurations(
    test_plan
)


for device_name, config in configurations.items():

    print("\n")
    print("=" * 70)
    print(device_name)
    print("=" * 70)

    print(config)