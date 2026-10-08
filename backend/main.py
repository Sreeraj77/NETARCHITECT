from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
from config_validator.validator import validate_configurations

from ai.intent_extractor import extract_intent
from ai.network_planner import generate_network_plan

from config_generator.cisco_generator import (
    generate_all_configurations
)


app = FastAPI(
    title="NetArchitect AI",
    description="AI-Assisted Intent-Based Network Design and Automation Platform",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class NetworkRequest(BaseModel):
    requirement: str


class ConfigRequest(BaseModel):
    plan: Dict[str, Any]


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "NetArchitect AI backend is running"
    }


# ============================================================
# NETWORK DESIGN
# ============================================================

@app.post("/api/network/design")
def design_network(request: NetworkRequest):

    intent = extract_intent(
        request.requirement
    )

    plan = generate_network_plan(
        intent
    )

    return {
        "intent": intent.model_dump(),
        "network_plan": plan.model_dump()
    }


# ============================================================
# CISCO CONFIGURATION GENERATION
# ============================================================

@app.post("/api/network/generate-config")
def generate_config(request: ConfigRequest):

    configurations = generate_all_configurations(
        request.plan
    )

    return {
        "message": "Cisco configurations generated successfully",
        "configurations": configurations
    }

@app.post("/api/network/validate-config")
def validate_config(request: ConfigRequest):
    configurations = generate_all_configurations(request.plan)

    validation_result = validate_configurations(
        request.plan,
        configurations
    )

    return {
        "message": "Configuration validation completed",
        "validation": validation_result
    }