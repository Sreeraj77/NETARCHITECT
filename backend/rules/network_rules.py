from models.intent_schema import NetworkIntent
from models.network_plan_schema import NetworkPlan
import math


# ==============================================================
# USER DISTRIBUTION
# ==============================================================

def distribute_users(
    total_users: int | None,
    number_of_groups: int
) -> list[int | None]:

    if not total_users or number_of_groups <= 0:
        return [None] * number_of_groups

    base_users = total_users // number_of_groups
    remainder = total_users % number_of_groups

    distribution = []

    for i in range(number_of_groups):

        users = base_users

        if i < remainder:
            users += 1

        distribution.append(users)

    return distribution


# ==============================================================
# VLAN PLAN
# ==============================================================

def generate_vlan_plan(
    intent: NetworkIntent
) -> list[dict]:

    if not intent.vlan_required:
        return []

    # Use actual department names if available
    if intent.departments:

        departments = intent.departments

    # Otherwise create generic department names
    elif intent.number_of_departments:

        departments = [
            f"Department-{i + 1}"
            for i in range(intent.number_of_departments)
        ]

    else:

        departments = ["Users"]

    user_distribution = distribute_users(
        intent.number_of_users,
        len(departments)
    )

    vlans = []

    for index, department in enumerate(departments):

        vlan_id = 10 + (index * 10)

        vlans.append(
            {
                "vlan_id": vlan_id,
                "name": department,
                "purpose": f"{department} Department",
                "estimated_users": user_distribution[index]
            }
        )

    return vlans


# ==============================================================
# IP ADDRESS PLAN
# ==============================================================

def generate_ip_plan(
    vlans: list[dict]
) -> list[dict]:

    ip_networks = []

    for vlan in vlans:

        vlan_id = vlan["vlan_id"]

        network = f"10.{vlan_id}.0.0/24"

        subnet_mask = "255.255.255.0"

        gateway = f"10.{vlan_id}.0.1"

        ip_networks.append(
            {
                "network": network,
                "subnet_mask": subnet_mask,
                "gateway": gateway,
                "vlan_id": vlan_id
            }
        )

    return ip_networks


# ==============================================================
# ACCESS SWITCH CALCULATION
# ==============================================================

def calculate_access_switches(
    number_of_users: int | None
) -> int:

    if not number_of_users:
        return 1

    # Assume 48 usable ports per access switch
    return max(
        1,
        math.ceil(number_of_users / 48)
    )


# ==============================================================
# DEVICE PLAN
# ==============================================================

def generate_device_plan(
    intent: NetworkIntent,
    vlan_count: int
) -> list[dict]:

    devices = []

    # ----------------------------------------------
    # CORE SWITCH
    # ----------------------------------------------

    core_quantity = 2 if intent.redundancy_required else 1

    devices.append(
        {
            "device_type": "Core Switch",
            "quantity": core_quantity,
            "purpose": (
                "Provides redundant high-speed core connectivity"
                if intent.redundancy_required
                else "Provides high-speed core connectivity"
            )
        }
    )

    # ----------------------------------------------
    # DISTRIBUTION SWITCH
    # ----------------------------------------------

    if vlan_count > 2:

        distribution_quantity = (
            2 if intent.redundancy_required else 2
        )

        devices.append(
            {
                "device_type": "Distribution Switch",
                "quantity": distribution_quantity,
                "purpose": "Aggregates access-layer switches"
            }
        )

    # ----------------------------------------------
    # ACCESS SWITCH
    # ----------------------------------------------

    access_quantity = calculate_access_switches(
        intent.number_of_users
    )

    devices.append(
        {
            "device_type": "Access Switch",
            "quantity": access_quantity,
            "purpose": "Provides wired connectivity to end-user devices"
        }
    )

    # ----------------------------------------------
    # WIRELESS ACCESS POINT
    # ----------------------------------------------

    if intent.wireless_required:

        users = intent.number_of_users or 50

        ap_quantity = max(
            1,
            math.ceil(users / 50)
        )

        devices.append(
            {
                "device_type": "Wireless Access Point",
                "quantity": ap_quantity,
                "purpose": "Provides wireless network access"
            }
        )

    # ----------------------------------------------
    # FIREWALL
    # ----------------------------------------------

    if intent.firewall_required:

        firewall_quantity = (
            2 if intent.redundancy_required else 1
        )

        devices.append(
            {
                "device_type": "Firewall",
                "quantity": firewall_quantity,
                "purpose": "Provides perimeter security and traffic filtering"
            }
        )

    # ----------------------------------------------
    # INTERNET ROUTER
    # ----------------------------------------------

    if intent.internet_required:

        router_quantity = (
            2 if intent.redundancy_required else 1
        )

        devices.append(
            {
                "device_type": "Internet Router",
                "quantity": router_quantity,
                "purpose": "Provides connectivity to the Internet"
            }
        )

    return devices


# ==============================================================
# SERVICES
# ==============================================================

def generate_services(
    intent: NetworkIntent
) -> list[str]:

    services = []

    # Preserve explicitly requested services
    for service in intent.services:

        if service not in services:
            services.append(service)

    # Supporting services
    if "DHCP" not in services:
        services.append("DHCP")

    if "DNS" not in services:
        services.append("DNS")

    return services


# ==============================================================
# SECURITY FEATURES
# ==============================================================

def generate_security_features(
    intent: NetworkIntent
) -> list[str]:

    security_features = []

    if intent.vlan_required:

        security_features.append(
            "VLAN Segmentation"
        )

    if intent.firewall_required:

        security_features.append(
            "Firewall Traffic Filtering"
        )

    for feature in intent.security_features:

        if feature not in security_features:

            security_features.append(feature)

    return security_features


# ==============================================================
# ROUTING PROTOCOL
# ==============================================================

def select_routing_protocol(
    intent: NetworkIntent
) -> str:

    # Respect explicit user choice
    if intent.routing_protocol:

        return intent.routing_protocol.upper()

    # Multi-department networks benefit from
    # dynamic routing.
    if intent.number_of_departments:

        if intent.number_of_departments >= 3:
            return "OSPF"

    # Default
    return "OSPF"


# ==============================================================
# USER DISTRIBUTION VALIDATION
# ==============================================================

def validate_user_distribution(
    vlans: list[dict],
    total_users: int | None
) -> bool:

    if total_users is None:
        return True

    estimated_users = 0

    for vlan in vlans:

        users = vlan.get("estimated_users")

        if users:
            estimated_users += users

    return estimated_users <= total_users


# ==============================================================
# TOPOLOGY GENERATION
# ==============================================================

def generate_topology_data(
    intent: NetworkIntent,
    vlans: list[dict],
    devices: list[dict]
) -> dict:

    nodes = []
    connections = []

    def add_node(
        node_id,
        label,
        device_type,
        quantity=1,
        vlan_ids=None
    ):

        nodes.append(
            {
                "node_id": node_id,
                "label": label,
                "device_type": device_type,
                "quantity": quantity,
                "vlan_ids": vlan_ids or []
            }
        )

    # VLAN IDs
    vlan_ids = [
        vlan["vlan_id"]
        for vlan in vlans
    ]

    # ==========================================================
    # INTERNET
    # ==========================================================

    add_node(
        "internet",
        "Internet",
        "Internet"
    )

    # ==========================================================
    # ROUTER
    # ==========================================================

    router = next(
        (
            d for d in devices
            if "router" in d["device_type"].lower()
        ),
        None
    )

    router_id = None

    if router:

        router_id = "router-1"

        add_node(
            router_id,
            "Internet Router",
            "Internet Router",
            router["quantity"]
        )

        connections.append(
            {
                "source": "internet",
                "target": router_id,
                "connection_type": "WAN"
            }
        )

    # ==========================================================
    # FIREWALL
    # ==========================================================

    firewall = next(
        (
            d for d in devices
            if "firewall" in d["device_type"].lower()
        ),
        None
    )

    firewall_id = None

    if firewall:

        firewall_id = "firewall-1"

        add_node(
            firewall_id,
            "Firewall",
            "Firewall",
            firewall["quantity"]
        )

        connections.append(
            {
                "source": router_id or "internet",
                "target": firewall_id,
                "connection_type": "Ethernet"
            }
        )

    # ==========================================================
    # CORE SWITCH
    # ==========================================================

    core = next(
        (
            d for d in devices
            if "core switch" in d["device_type"].lower()
        ),
        None
    )

    core_id = None

    if core:

        core_id = "core-1"

        add_node(
            core_id,
            "Core Switch",
            "Core Switch",
            core["quantity"],
            vlan_ids
        )

        connections.append(
            {
                "source": firewall_id or router_id or "internet",
                "target": core_id,
                "connection_type": "Ethernet"
            }
        )

    # ==========================================================
    # DISTRIBUTION SWITCHES
    # ==========================================================

    distribution = next(
        (
            d for d in devices
            if "distribution switch"
            in d["device_type"].lower()
        ),
        None
    )

    distribution_ids = []

    if distribution and core_id:

        for i in range(distribution["quantity"]):

            distribution_id = f"distribution-{i + 1}"

            distribution_ids.append(
                distribution_id
            )

            add_node(
                distribution_id,
                f"Distribution Switch {i + 1}",
                "Distribution Switch",
                1,
                vlan_ids
            )

            connections.append(
                {
                    "source": core_id,
                    "target": distribution_id,
                    "connection_type": "Ethernet"
                }
            )

    # ==========================================================
    # ACCESS SWITCHES
    # ==========================================================

    access = next(
        (
            d for d in devices
            if "access switch"
            in d["device_type"].lower()
        ),
        None
    )

    access_ids = []

    if access:

        # Prefer Distribution layer.
        # If Distribution does not exist,
        # connect directly to Core.
        parent_ids = (
            distribution_ids
            if distribution_ids
            else (
                [core_id]
                if core_id
                else []
            )
        )

        for i in range(access["quantity"]):

            access_id = f"access-{i + 1}"

            access_ids.append(
                access_id
            )

            add_node(
                access_id,
                f"Access Switch {i + 1}",
                "Access Switch",
                1,
                vlan_ids
            )

            if parent_ids:

                parent = parent_ids[
                    i % len(parent_ids)
                ]

                connections.append(
                    {
                        "source": parent,
                        "target": access_id,
                        "connection_type": "Ethernet"
                    }
                )

    # ==========================================================
    # WIRELESS ACCESS POINTS
    # ==========================================================

    wireless = next(
        (
            d for d in devices
            if "wireless access point"
            in d["device_type"].lower()
        ),
        None
    )

    if wireless:

        # APs should connect to Access Switches.
        # If Access Switches do not exist,
        # fall back to Distribution, then Core.
        parent_ids = (
            access_ids
            if access_ids
            else (
                distribution_ids
                if distribution_ids
                else (
                    [core_id]
                    if core_id
                    else []
                )
            )
        )

        for i in range(wireless["quantity"]):

            ap_id = f"ap-{i + 1}"

            add_node(
                ap_id,
                f"WiFi AP {i + 1}",
                "Wireless Access Point",
                1,
                vlan_ids
            )

            if parent_ids:

                parent = parent_ids[
                    i % len(parent_ids)
                ]

                connections.append(
                    {
                        "source": parent,
                        "target": ap_id,
                        "connection_type": "Ethernet"
                    }
                )

    # ==========================================================
    # RETURN TOPOLOGY
    # ==========================================================

    return {
        "nodes": nodes,
        "connections": connections
    }


# ==============================================================
# APPLY NETWORK RULES
# ==============================================================

def apply_network_rules(
    intent: NetworkIntent,
    plan_data: dict
) -> NetworkPlan:

    # ==============================================
    # VLAN RULES
    # ==============================================

    vlans = generate_vlan_plan(intent)

    plan_data["vlans"] = vlans

    # ==============================================
    # IP ADDRESSING RULES
    # ==============================================

    plan_data["ip_networks"] = generate_ip_plan(
        vlans
    )

    # ==============================================
    # DEVICE RULES
    # ==============================================

    plan_data["devices"] = generate_device_plan(
        intent,
        len(vlans)
    )

    # ==============================================
    # TOPOLOGY
    # ==============================================

    plan_data["topology_data"] = generate_topology_data(
        intent,
        vlans,
        plan_data["devices"]
    )

    print(
        "DEVICES:",
        plan_data["devices"]
    )

    # ==============================================
    # SERVICES
    # ==============================================

    plan_data["services"] = generate_services(
        intent
    )

    # ==============================================
    # SECURITY
    # ==============================================

    plan_data["security_features"] = (
        generate_security_features(intent)
    )

    # ==============================================
    # ROUTING
    # ==============================================

    plan_data["routing_protocol"] = (
        select_routing_protocol(intent)
    )

    # ==============================================
    # REQUIREMENT FLAGS
    # ==============================================

    plan_data["wireless_required"] = (
        intent.wireless_required
    )

    plan_data["internet_required"] = (
        intent.internet_required
    )

    plan_data["firewall_required"] = (
        intent.firewall_required
    )

    plan_data["redundancy_required"] = (
        intent.redundancy_required
    )

    # ==============================================
    # USER DISTRIBUTION VALIDATION
    # ==============================================

    if not validate_user_distribution(
        vlans,
        intent.number_of_users
    ):

        raise ValueError(
            "VLAN user distribution exceeds total users."
        )

    # ==============================================
    # FINAL VALIDATION
    # ==============================================

    return NetworkPlan(**plan_data)