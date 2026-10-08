from config_generator.cisco_generator import (
    generate_all_configurations
)

from config_validator.validator import (
    validate_configurations
)


test_plan = {
    "routing_protocol": "OSPF",

    "firewall_required": True,

    "vlans": [
        {
            "vlan_id": 10,
            "name": "CSE"
        },
        {
            "vlan_id": 20,
            "name": "ECE"
        },
        {
            "vlan_id": 30,
            "name": "EEE"
        },
        {
            "vlan_id": 40,
            "name": "ME"
        },
        {
            "vlan_id": 50,
            "name": "CE"
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
            "device_type": "Firewall",
            "quantity": 1
        },
        {
            "device_type": "Internet Router",
            "quantity": 1
        }
    ]
}


# Generate configurations
configurations = generate_all_configurations(
    test_plan
)


# Validate configurations
result = validate_configurations(
    test_plan,
    configurations
)


print("\n")
print("=" * 60)
print("NETWORK CONFIGURATION VALIDATION")
print("=" * 60)

print("\nVALID:", result["valid"])

print("\nCHECKS:")

for check, status in result["checks"].items():

    symbol = "✓" if status == "PASS" else "✗"

    print(
        f"{symbol} {check}: {status}"
    )


print("\nERRORS:")

if result["errors"]:

    for error in result["errors"]:
        print(f"- {error}")

else:

    print("No errors found.")


print("\nSUMMARY:")
print(result["summary"])