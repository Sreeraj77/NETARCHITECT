from typing import List, Optional
from pydantic import BaseModel, Field


class VLANPlan(BaseModel):
    vlan_id: int = Field(..., ge=1, le=4094)
    name: str
    purpose: str
    estimated_users: Optional[int] = Field(default=None, ge=1)


class IPNetworkPlan(BaseModel):
    network: str
    subnet_mask: str
    gateway: str
    vlan_id: Optional[int] = None


class DeviceRequirement(BaseModel):
    device_type: str
    quantity: int = Field(..., ge=1)
    purpose: str


class TopologyNode(BaseModel):
    node_id: str
    label: str
    device_type: str
    quantity: int = Field(default=1, ge=1)
    vlan_ids: List[int] = Field(default_factory=list)


class TopologyConnection(BaseModel):
    source: str
    target: str
    connection_type: str = "Ethernet"


class NetworkTopology(BaseModel):
    nodes: List[TopologyNode] = Field(default_factory=list)
    connections: List[TopologyConnection] = Field(default_factory=list)


class NetworkPlan(BaseModel):
    architecture: str
    topology: str

    vlans: List[VLANPlan] = Field(default_factory=list)

    ip_networks: List[IPNetworkPlan] = Field(default_factory=list)

    devices: List[DeviceRequirement] = Field(default_factory=list)

    routing_protocol: Optional[str] = None

    services: List[str] = Field(default_factory=list)

    security_features: List[str] = Field(default_factory=list)

    wireless_required: bool = False

    internet_required: bool = False

    firewall_required: bool = False

    redundancy_required: bool = False

    recommendations: List[str] = Field(default_factory=list)

    topology_data: NetworkTopology = Field(
        default_factory=NetworkTopology
    )