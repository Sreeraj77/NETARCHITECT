from models.intent_schema import NetworkIntent

sample = NetworkIntent(
    organization_type="College",
    organization_name="XYZ College",
    number_of_users=500,
    number_of_departments=4,
    departments=[
        "Administration",
        "CSE",
        "ECE",
        "Mechanical"
    ],
    services=[
        "DHCP",
        "DNS",
        "Internet",
        "WiFi"
    ],
    vlan_required=True,
    wireless_required=True,
    internet_required=True,
    firewall_required=True,
    routing_protocol="OSPF"
)

print(sample.model_dump_json(indent=4))