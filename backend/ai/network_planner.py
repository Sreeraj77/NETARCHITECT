from ollama import chat
from models.intent_schema import NetworkIntent
from models.network_plan_schema import NetworkPlan
from rules.network_rules import apply_network_rules
import json


MODEL_NAME = "llama3.2:3b"


NETWORK_PLANNING_PROMPT = """
You are an expert computer network architect.

Create a practical network design from the structured requirements below.

You ARE allowed to make reasonable engineering recommendations,
but you MUST NOT contradict the user's requirements.

==================================================
NETWORK REQUIREMENTS
==================================================

{intent_json}

==================================================
DESIGN RULES
==================================================

1. Choose an appropriate network architecture.

Possible choices:
- Hierarchical
- Three-tier
- Two-tier
- Flat

2. Choose an appropriate topology.

Possible choices:
- Star
- Extended Star
- Mesh
- Partial Mesh

3. If VLANs are required:
   - Create VLANs for the departments.
   - Use the actual department names when available.
   - If names are unavailable, use Department-1, Department-2, etc.
   - VLAN IDs should start from 10 and increase by 10.

4. The total estimated users across VLANs MUST NOT exceed
   the total number of users.

5. Create an IP network for every VLAN.

6. Use private IPv4 addressing.

7. Recommend appropriate network devices.

8. If wireless is required, include Wireless Access Points.

9. If Internet is required, include an Internet Router.

10. If a firewall is required, include a Firewall.

11. If redundancy is required, recommend redundant critical devices.

12. If the user explicitly specifies a routing protocol, use it.

13. If the user does not specify a routing protocol,
    recommend an appropriate routing protocol.

14. Preserve all explicitly requested network services.

15. Provide useful network-specific recommendations.

==================================================
OUTPUT
==================================================

Return ONLY one valid JSON object.

Do NOT use Markdown.
Do NOT use ```json.
Do NOT add explanations outside the JSON.

The JSON must contain:

{
    "architecture": "string",
    "topology": "string",

    "vlans": [
        {
            "vlan_id": integer,
            "name": "string",
            "purpose": "string",
            "estimated_users": integer or null
        }
    ],

    "ip_networks": [
        {
            "network": "string",
            "subnet_mask": "string",
            "gateway": "string",
            "vlan_id": integer or null
        }
    ],

    "devices": [
        {
            "device_type": "string",
            "quantity": integer,
            "purpose": "string"
        }
    ],

    "routing_protocol": "string or null",
    "services": [],
    "security_features": [],
    "wireless_required": boolean,
    "internet_required": boolean,
    "firewall_required": boolean,
    "redundancy_required": boolean,
    "recommendations": []
}

==================================================
STRUCTURED REQUIREMENTS
==================================================

{intent_json}
"""


def generate_network_plan(intent: NetworkIntent) -> NetworkPlan:

    # ==============================================
    # STEP 1: SEND INTENT TO LLM
    # ==============================================

    intent_json = intent.model_dump_json(indent=4)

    prompt = NETWORK_PLANNING_PROMPT.replace(
        "{intent_json}",
        intent_json
    )

    response = chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    response_text = response.message.content.strip()

    print("\n===== RAW NETWORK PLAN RESPONSE =====\n")
    print(response_text)
    print("\n===== END RAW NETWORK PLAN RESPONSE =====\n")

    # ==============================================
    # STEP 2: CLEAN LLM RESPONSE
    # ==============================================

    response_text = response_text.replace(
        "```json",
        ""
    )

    response_text = response_text.replace(
        "```",
        ""
    )

    response_text = response_text.strip()

    # ==============================================
    # STEP 3: EXTRACT JSON
    # ==============================================

    start = response_text.find("{")
    end = response_text.rfind("}")

    if start == -1 or end == -1:

        raise ValueError(
            "No valid JSON object found in network planner response."
        )

    json_text = response_text[start:end + 1]

    try:

        data = json.loads(json_text)

    except json.JSONDecodeError as e:

        print("\n===== INVALID NETWORK PLAN JSON =====\n")
        print(json_text)

        raise ValueError(
            f"Network planner returned invalid JSON: {e}"
        )

    # ==============================================
    # STEP 4: NORMALIZE NULL VALUES
    # ==============================================

    for key, value in data.items():

        if isinstance(value, str):

            if value.lower().strip() == "null":

                data[key] = None

        elif isinstance(value, list):

            data[key] = [
                item
                for item in value
                if not (
                    isinstance(item, str)
                    and item.lower().strip() == "null"
                )
            ]

    # ==============================================
    # STEP 5: MAKE SURE REQUIRED LISTS EXIST
    # ==============================================

    list_fields = [
        "vlans",
        "ip_networks",
        "devices",
        "services",
        "security_features",
        "recommendations"
    ]

    for field in list_fields:

        if data.get(field) is None:

            data[field] = []

        if not isinstance(data.get(field), list):

            data[field] = []

    # ==============================================
    # STEP 6: APPLY RULE ENGINE
    # ==============================================

    print("\n===== APPLYING NETWORK RULE ENGINE =====\n")

    plan = apply_network_rules(
        intent,
        data
    )

    print("Network rules applied successfully.")

    return plan