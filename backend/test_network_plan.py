from models.network_plan_schema import NetworkPlan


sample_plan = NetworkPlan(
    architecture="Hierarchical",
    topology="Extended Star",

    vlans=[
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
        }
    ],

    ip_networks=[
        {
            "network": "192.168.10.0",
            "subnet_mask": "255.255.255.0",
            "gateway": "192.168.10.1",
            "vlan_id": 10
        }
    ],

    devices=[
        {
            "device_type": "Core Switch",
            "quantity": 2,
            "purpose": "Core network connectivity"
        },
        {
            "device_type": "Access Switch",
            "quantity": 10,
            "purpose": "Connect end-user devices"
        }
    ],

    routing_protocol="OSPF",

    services=[
        "DHCP",
        "DNS",
        "Internet"
    ],

    security_features=[
        "VLAN Segmentation",
        "Firewall"
    ],

    wireless_required=True,
    internet_required=True,
    firewall_required=True,
    redundancy_required=True,

    recommendations=[
        "Use hierarchical network architecture",
        "Separate departments using VLANs",
        "Use OSPF for dynamic routing"
    ]
)


print("\n===== NETWORK PLAN =====\n")

print(sample_plan.model_dump_json(indent=4))