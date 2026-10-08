"""
Network Configuration Validator
NetArchitect AI

Validates generated Cisco configurations
against the generated NetworkPlan.
"""

import re
from typing import Dict, Any, List


# ============================================================
# VLAN VALIDATION
# ============================================================

def validate_vlans(
    plan: Dict[str, Any],
    configurations: Dict[str, str]
) -> Dict[str, Any]:

    vlans = plan.get("vlans", [])

    expected_vlans = {
        str(vlan["vlan_id"])
        for vlan in vlans
        if vlan.get("vlan_id") is not None
    }

    errors = []

    for device, config in configurations.items():

        # Only switches need VLAN validation
        if "Switch" not in device:
            continue

        for vlan_id in expected_vlans:

            pattern = rf"vlan\s+{re.escape(vlan_id)}\b"

            if not re.search(pattern, config):
                errors.append(
                    f"{device}: VLAN {vlan_id} is missing."
                )

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors
    }


# ============================================================
# IP ADDRESS VALIDATION
# ============================================================

def validate_ip_networks(
    plan: Dict[str, Any],
    configurations: Dict[str, str]
) -> Dict[str, Any]:

    ip_networks = plan.get(
        "ip_networks",
        []
    )

    errors = []

    core_config = configurations.get(
        "Core Switch",
        ""
    )

    for network in ip_networks:

        vlan_id = network.get("vlan_id")
        gateway = network.get("gateway")

        if vlan_id is None or not gateway:
            continue

        interface_pattern = (
            rf"interface vlan\s+{vlan_id}\b"
        )

        gateway_pattern = (
            rf"ip address\s+{re.escape(gateway)}\b"
        )

        if not re.search(
            interface_pattern,
            core_config,
            re.IGNORECASE
        ):
            errors.append(
                f"Core Switch: SVI for VLAN "
                f"{vlan_id} is missing."
            )

        elif not re.search(
            gateway_pattern,
            core_config,
            re.IGNORECASE
        ):
            errors.append(
                f"Core Switch: Gateway "
                f"{gateway} is missing."
            )

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors
    }


# ============================================================
# OSPF VALIDATION
# ============================================================

def validate_ospf(
    plan: Dict[str, Any],
    configurations: Dict[str, str]
) -> Dict[str, Any]:

    routing_protocol = plan.get(
        "routing_protocol",
        ""
    ).upper()

    errors = []

    if routing_protocol != "OSPF":
        return {
            "status": "PASS",
            "errors": []
        }

    ip_networks = plan.get(
        "ip_networks",
        []
    )

    # Check Core Switch
    core_config = configurations.get(
        "Core Switch",
        ""
    )

    # Check Internet Router
    router_config = configurations.get(
        "Internet Router",
        ""
    )

    for network in ip_networks:

        network_address = network.get(
            "network"
        )

        if not network_address:
            continue

        if network_address.endswith("/24"):

            network_address = (
                network_address.replace(
                    "/24",
                    ""
                )
            )

            expected_line = (
                f"network {network_address}"
            )

            if expected_line not in core_config:
                errors.append(
                    f"Core Switch: OSPF network "
                    f"{network_address} is missing."
                )

            if expected_line not in router_config:
                errors.append(
                    f"Internet Router: OSPF network "
                    f"{network_address} is missing."
                )

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors
    }


# ============================================================
# TRUNK VALIDATION
# ============================================================

def validate_trunks(
    plan: Dict[str, Any],
    configurations: Dict[str, str]
) -> Dict[str, Any]:

    vlans = plan.get(
        "vlans",
        []
    )

    expected_vlan_list = ",".join(
        str(vlan["vlan_id"])
        for vlan in vlans
        if vlan.get("vlan_id") is not None
    )

    errors = []

    for device, config in configurations.items():

        if "Switch" not in device:
            continue

        trunk_lines = re.findall(
            r"switchport trunk allowed vlan\s+([^\n]+)",
            config,
            re.IGNORECASE
        )

        for trunk_vlan_list in trunk_lines:

            actual = (
                trunk_vlan_list
                .strip()
            )

            if actual != expected_vlan_list:

                errors.append(
                    f"{device}: Trunk VLAN list "
                    f"'{actual}' does not match "
                    f"expected '{expected_vlan_list}'."
                )

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors
    }


# ============================================================
# ACCESS PORT VALIDATION
# ============================================================

def validate_access_ports(
    plan: Dict[str, Any],
    configurations: Dict[str, str]
) -> Dict[str, Any]:

    vlans = plan.get(
        "vlans",
        []
    )

    valid_vlan_ids = {
        str(vlan["vlan_id"])
        for vlan in vlans
        if vlan.get("vlan_id") is not None
    }

    errors = []

    for device, config in configurations.items():

        if "Access Switch" not in device:
            continue

        access_vlan_lines = re.findall(
            r"switchport access vlan\s+(\d+)",
            config,
            re.IGNORECASE
        )

        for vlan_id in access_vlan_lines:

            if vlan_id not in valid_vlan_ids:

                errors.append(
                    f"{device}: Access port "
                    f"references undefined VLAN "
                    f"{vlan_id}."
                )

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors
    }


# ============================================================
# DEVICE VALIDATION
# ============================================================

def validate_devices(
    plan: Dict[str, Any],
    configurations: Dict[str, str]
) -> Dict[str, Any]:

    errors = []

    expected_devices = []

    for device in plan.get(
        "devices",
        []
    ):

        device_type = device.get(
            "device_type",
            ""
        )

        quantity = device.get(
            "quantity",
            1
        )

        if "Core Switch" in device_type:

            expected_devices.append(
                "Core Switch"
            )

        elif "Distribution Switch" in device_type:

            for i in range(
                1,
                quantity + 1
            ):
                expected_devices.append(
                    f"Distribution Switch {i}"
                )

        elif "Access Switch" in device_type:

            for i in range(
                1,
                quantity + 1
            ):
                expected_devices.append(
                    f"Access Switch {i}"
                )

        elif "Router" in device_type:

            expected_devices.append(
                "Internet Router"
            )

        elif "Firewall" in device_type:

            expected_devices.append(
                "Firewall"
            )

    for device in expected_devices:

        if device not in configurations:

            errors.append(
                f"Missing configuration for "
                f"{device}."
            )

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors
    }


# ============================================================
# FIREWALL VALIDATION
# ============================================================

def validate_firewall(
    plan: Dict[str, Any],
    configurations: Dict[str, str]
) -> Dict[str, Any]:

    errors = []

    firewall_required = plan.get(
        "firewall_required",
        False
    )

    if not firewall_required:
        return {
            "status": "PASS",
            "errors": []
        }

    if "Firewall" not in configurations:

        errors.append(
            "Firewall is required but "
            "no firewall configuration "
            "was generated."
        )

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors
    }


# ============================================================
# MAIN VALIDATION FUNCTION
# ============================================================

def validate_configurations(
    plan: Dict[str, Any],
    configurations: Dict[str, str]
) -> Dict[str, Any]:

    vlan_result = validate_vlans(
        plan,
        configurations
    )

    ip_result = validate_ip_networks(
        plan,
        configurations
    )

    ospf_result = validate_ospf(
        plan,
        configurations
    )

    trunk_result = validate_trunks(
        plan,
        configurations
    )

    access_result = validate_access_ports(
        plan,
        configurations
    )

    device_result = validate_devices(
        plan,
        configurations
    )

    firewall_result = validate_firewall(
        plan,
        configurations
    )

    checks = {
        "vlan_consistency": vlan_result["status"],
        "ip_addressing": ip_result["status"],
        "ospf_configuration": ospf_result["status"],
        "trunk_configuration": trunk_result["status"],
        "access_ports": access_result["status"],
        "device_consistency": device_result["status"],
        "firewall_configuration": firewall_result["status"]
    }

    all_errors = (
        vlan_result["errors"]
        + ip_result["errors"]
        + ospf_result["errors"]
        + trunk_result["errors"]
        + access_result["errors"]
        + device_result["errors"]
        + firewall_result["errors"]
    )

    return {
        "valid": len(all_errors) == 0,
        "checks": checks,
        "errors": all_errors,
        "summary": (
            "Configuration validation passed."
            if len(all_errors) == 0
            else
            f"Configuration validation found "
            f"{len(all_errors)} issue(s)."
        )
    }