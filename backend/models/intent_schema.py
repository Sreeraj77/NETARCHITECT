from typing import List, Optional
from pydantic import BaseModel, Field


class NetworkIntent(BaseModel):
    """
    Standard schema for network design requirements extracted from
    a user's natural language prompt.
    """

    # Organization Details
    organization_type: str = Field(
        ...,
        description="Type of organization (College, Hospital, Office, School, etc.)"
    )

    organization_name: Optional[str] = Field(
        default=None,
        description="Name of the organization if mentioned."
    )

    # Infrastructure
    number_of_users: Optional[int] = Field(
        default=None,
        ge=1,
        description="Estimated number of users."
    )

    number_of_departments: Optional[int] = Field(
        default=None,
        ge=1
    )

    departments: List[str] = Field(
        default_factory=list
    )

    number_of_buildings: Optional[int] = Field(default=None, ge=1)

    number_of_floors: Optional[int] = Field(default=None, ge=1)

    # Network Services
    services: List[str] = Field(
        default_factory=list,
        description="DHCP, DNS, Internet, Email, Web Server, CCTV, WiFi, VPN..."
    )

    # Network Features
    vlan_required: bool = False

    wireless_required: bool = False

    internet_required: bool = False

    firewall_required: bool = False

    redundancy_required: bool = False

    # Routing
    routing_protocol: Optional[str] = Field(
        default=None,
        description="OSPF, RIP, EIGRP, Static"
    )

    # Security
    security_features: List[str] = Field(
        default_factory=list
    )

    # Servers
    servers: List[str] = Field(
        default_factory=list
    )

    # Additional Requirements
    special_requirements: List[str] = Field(
        default_factory=list
    )

    class Config:
        json_schema_extra = {
            "example": {
                "organization_type": "College",
                "organization_name": "ABC Engineering College",
                "number_of_users": 600,
                "number_of_departments": 5,
                "departments": [
                    "Administration",
                    "CSE",
                    "ECE",
                    "EEE",
                    "Mechanical"
                ],
                "number_of_buildings": 2,
                "number_of_floors": 4,
                "services": [
                    "DHCP",
                    "DNS",
                    "Internet",
                    "WiFi",
                    "VoIP",
                    "CCTV"
                ],
                "vlan_required": True,
                "wireless_required": True,
                "internet_required": True,
                "firewall_required": True,
                "redundancy_required": False,
                "routing_protocol": "OSPF",
                "security_features": [
                    "ACL",
                    "Firewall"
                ],
                "servers": [
                    "Web Server",
                    "DNS Server",
                    "DHCP Server"
                ],
                "special_requirements": [
                    "Guest WiFi",
                    "Remote VPN"
                ]
            }
        }