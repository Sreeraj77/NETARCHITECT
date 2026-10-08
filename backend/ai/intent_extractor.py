from ollama import chat
from models.intent_schema import NetworkIntent
from ai.prompt import INTENT_EXTRACTION_PROMPT
import json
import re


MODEL_NAME = "llama3.2:3b"


def extract_intent(user_input: str) -> NetworkIntent:

    prompt = INTENT_EXTRACTION_PROMPT.replace(
        "{user_input}",
        user_input
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

    print("\n===== RAW LLM RESPONSE =====\n")
    print(response_text)
    print("\n===== END RAW RESPONSE =====\n")

    # ==================================================
    # CLEAN LLM RESPONSE
    # ==================================================

    # Remove Markdown code fences
    response_text = response_text.replace("```json", "")
    response_text = response_text.replace("```", "")
    response_text = response_text.strip()

    # Find JSON object
    start = response_text.find("{")
    end = response_text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "No valid JSON object found in LLM response."
        )

    json_text = response_text[start:end + 1]

    try:
        data = json.loads(json_text)

    except json.JSONDecodeError as e:

        print("\n===== INVALID JSON =====\n")
        print(json_text)

        raise ValueError(
            f"LLM returned invalid JSON: {e}"
        )

    # ==================================================
    # NORMALIZE LLM OUTPUT
    # ==================================================

    # Convert "null" strings to None
    for key, value in data.items():

        if isinstance(value, str) and value.lower() == "null":

            data[key] = None

        elif isinstance(value, list):

            cleaned_list = []

            for item in value:

                if (
                    isinstance(item, str)
                    and item.lower() == "null"
                ):
                    continue

                cleaned_list.append(item)

            data[key] = cleaned_list

    # ==================================================
    # NORMALIZE UNKNOWN NUMERIC VALUES
    # ==================================================

    if data.get("number_of_buildings") == 0:
        data["number_of_buildings"] = None

    if data.get("number_of_floors") == 0:
        data["number_of_floors"] = None

    # ==================================================
    # DETERMINISTIC REQUIREMENT CHECKING
    # ==================================================

    # Always use original user input for explicit requirements.
    text = user_input.lower()
    print("\n===== ORIGINAL USER INPUT =====")
    print(user_input)
    print("===============================\n")

    # --------------------------------------------------
    # VLAN
    # --------------------------------------------------

    vlan_keywords = [
        "vlan",
        "vlans",
        "virtual lan",
        "virtual lans"
    ]

    if any(
        keyword in text
        for keyword in vlan_keywords
    ):
        data["vlan_required"] = True

    # --------------------------------------------------
    # WIFI
    # --------------------------------------------------

    wifi_keywords = [
        "wifi",
        "wi-fi",
        "wireless"
    ]

    if any(
        keyword in text
        for keyword in wifi_keywords
    ):
        data["wireless_required"] = True

    # --------------------------------------------------
    # INTERNET
    # --------------------------------------------------

    internet_keywords = [
        "internet",
        "internet access",
        "internet connectivity"
    ]

    if any(
        keyword in text
        for keyword in internet_keywords
    ):
        data["internet_required"] = True

    # --------------------------------------------------
    # FIREWALL
    # --------------------------------------------------

    firewall_keywords = [
        "firewall"
    ]

    if any(
        keyword in text
        for keyword in firewall_keywords
    ):
        data["firewall_required"] = True

    # --------------------------------------------------
    # REDUNDANCY
    # --------------------------------------------------

    redundancy_keywords = [
        "redundancy",
        "redundant",
        "high availability",
        "high-availability",
        "failover",
        "backup router",
        "backup firewall",
        "backup switch",
        "dual router",
        "dual firewall",
        "dual core"
    ]

    if any(
        keyword in text
        for keyword in redundancy_keywords
    ):
        data["redundancy_required"] = True
    else:
        # Do not allow the LLM to invent redundancy.
        data["redundancy_required"] = False

    # --------------------------------------------------
    # ROUTING PROTOCOL
    # --------------------------------------------------

    routing_protocols = [
        "ospf",
        "rip",
        "eigrp",
        "bgp",
        "static routing",
        "static"
    ]

    detected_protocol = None

    for protocol in routing_protocols:

        if re.search(
            r"\b" + re.escape(protocol) + r"\b",
            text
        ):

            detected_protocol = protocol.upper()
            break

    data["routing_protocol"] = detected_protocol

    # --------------------------------------------------
    # DEPARTMENT EXTRACTION
    # --------------------------------------------------

    # Deterministically preserve department names explicitly
    # mentioned by the user.
    #
    # Regex word boundaries prevent short names such as
    # "CE" from matching inside unrelated words.

    department_patterns = {
        "CSE": [
            "computer science and engineering",
            "computer science",
            "cse"
        ],

        "ECE": [
            "electronics and communication engineering",
            "electronics and communication",
            "electronics",
            "ece"
        ],

        "EEE": [
            "electrical and electronics engineering",
            "electrical and electronics",
            "electrical",
            "eee"
        ],

        "ME": [
            "mechanical engineering",
            "mechanical",
            "me"
        ],

        "CE": [
            "civil engineering",
            "civil",
            "ce"
        ]
    }

    detected_departments = []

    # Store department + position so that the final list
    # follows the order in which departments appear
    # in the user's sentence.

    department_positions = []

    for department, patterns in department_patterns.items():

        earliest_position = None

        for pattern in patterns:

            match = re.search(
                r"\b" + re.escape(pattern) + r"\b",
                text
            )

            if match:

                position = match.start()

                if (
                    earliest_position is None
                    or position < earliest_position
                ):
                    earliest_position = position

        if earliest_position is not None:

            department_positions.append(
                (
                    earliest_position,
                    department
                )
            )

    # Sort according to appearance in user input
    department_positions.sort(
        key=lambda item: item[0]
    )

    for _, department in department_positions:

        if department not in detected_departments:

            detected_departments.append(
                department
            )

    # If departments were explicitly mentioned,
    # override unreliable LLM department output.
    if detected_departments:

        data["departments"] = detected_departments

        data["number_of_departments"] = (
            len(detected_departments)
        )

    # --------------------------------------------------
    # REMOVE HALLUCINATED SECURITY FEATURES
    # --------------------------------------------------

    # Only keep security features if explicitly mentioned.

    security_feature_keywords = [
        "acl",
        "access control",
        "port security",
        "encryption",
        "ids",
        "ips",
        "vpn"
    ]

    detected_security_features = []

    for feature in security_feature_keywords:

        if re.search(
            r"\b" + re.escape(feature) + r"\b",
            text
        ):

            detected_security_features.append(
                feature
            )

    data["security_features"] = (
        detected_security_features
    )

    # --------------------------------------------------
    # SERVERS
    # --------------------------------------------------

    server_keywords = [
        "dns server",
        "web server",
        "dhcp server",
        "mail server",
        "email server",
        "database server",
        "file server",
        "ftp server",
        "application server"
    ]

    detected_servers = []

    for server in server_keywords:

        if server in text:

            detected_servers.append(
                server.title()
            )

    data["servers"] = detected_servers

    # --------------------------------------------------
    # SPECIAL REQUIREMENTS
    # --------------------------------------------------

    # Do not allow the LLM to invent these.
    data["special_requirements"] = []

    # --------------------------------------------------
    # LIST FIELD SAFETY
    # --------------------------------------------------

    list_fields = [
        "departments",
        "services",
        "security_features",
        "servers",
        "special_requirements"
    ]

    for field in list_fields:

        if data.get(field) is None:

            data[field] = []

        if not isinstance(
            data.get(field),
            list
        ):

            data[field] = []

    # ==================================================
    # BOOLEAN FIELD SAFETY
    # ==================================================

    boolean_fields = [
        "vlan_required",
        "wireless_required",
        "internet_required",
        "firewall_required",
        "redundancy_required"
    ]

    for field in boolean_fields:

        if data.get(field) is None:

            data[field] = False

    # ==================================================
    # PYDANTIC VALIDATION
    # ==================================================

    # IMPORTANT:
    # This happens AFTER all deterministic corrections.
    intent = NetworkIntent(**data)

    return intent