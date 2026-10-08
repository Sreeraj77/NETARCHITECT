import { useState } from "react";
import NetworkTopology from "./NetworkTopology";
import "./App.css";

function App() {
  const [requirement, setRequirement] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  // Configuration generation
  const [configurations, setConfigurations] = useState(null);
  const [configLoading, setConfigLoading] = useState(false);
  const [configError, setConfigError] = useState("");
  const [selectedDevice, setSelectedDevice] = useState("");

  // Configuration validation
  const [validationResult, setValidationResult] = useState(null);
  const [validationLoading, setValidationLoading] = useState(false);
  const [validationError, setValidationError] = useState("");

  // --------------------------------------------------
  // Generate Network Design
  // --------------------------------------------------

  const generateNetwork = async () => {
    if (!requirement.trim()) {
      setError("Please enter a network requirement.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setConfigurations(null);
    setValidationResult(null);
    setConfigError("");
    setValidationError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/network/design",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            requirement: requirement,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to generate network design.");
      }

      const data = await response.json();

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------
  // Generate Cisco Configurations
  // --------------------------------------------------

  const generateConfigurations = async () => {
    if (!result?.network_plan) {
      setConfigError("Generate a network design first.");
      return;
    }

    setConfigLoading(true);
    setConfigError("");
    setConfigurations(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/network/generate-config",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            plan: result.network_plan,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to generate configurations.");
      }

      const data = await response.json();

      setConfigurations(data.configurations);

      // Select first device automatically
      const deviceNames = Object.keys(data.configurations);

      if (deviceNames.length > 0) {
        setSelectedDevice(deviceNames[0]);
      }

      // Clear old validation result
      setValidationResult(null);
      setValidationError("");
    } catch (err) {
      setConfigError(err.message);
    } finally {
      setConfigLoading(false);
    }
  };

  // --------------------------------------------------
  // Validate Configurations
  // --------------------------------------------------

  const validateConfigurations = async () => {
    if (!result?.network_plan) {
      setValidationError("Generate a network design first.");
      return;
    }

    setValidationLoading(true);
    setValidationError("");
    setValidationResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/network/validate-config",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            plan: result.network_plan,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Configuration validation failed.");
      }

      const data = await response.json();

      setValidationResult(data.validation);
    } catch (err) {
      setValidationError(err.message);
    } finally {
      setValidationLoading(false);
    }
  };

  // --------------------------------------------------
  // Copy Configuration
  // --------------------------------------------------

  const copyConfiguration = async () => {
    if (!configurations || !selectedDevice) {
      return;
    }

    try {
      await navigator.clipboard.writeText(
        configurations[selectedDevice]
      );

      alert("Configuration copied to clipboard.");
    } catch (err) {
      alert("Failed to copy configuration.");
    }
  };

  // --------------------------------------------------
  // Download Configuration
  // --------------------------------------------------

  const downloadConfiguration = () => {
    if (!configurations || !selectedDevice) {
      return;
    }

    const configText = configurations[selectedDevice];

    const blob = new Blob([configText], {
      type: "text/plain",
    });

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;
    link.download = `${selectedDevice}.txt`;

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  };

  // --------------------------------------------------
  // Helper: Format Names
  // --------------------------------------------------

  const formatName = (name) => {
    return name
      .replace(/_/g, " ")
      .replace(/\b\w/g, (char) => char.toUpperCase());
  };

  return (
    <div className="app">

      {/* ==================================================
          HEADER
      ================================================== */}

      <header className="app-header">
        <div>
          <h1>NetArchitect AI</h1>

          <p>
            AI-Assisted Intent-Based Network Design and
            Automation Platform
          </p>
        </div>
      </header>

      <main className="app-container">

        {/* ==================================================
            NETWORK REQUIREMENT
        ================================================== */}

        <section className="requirement-section">

          <h2>Network Requirement</h2>

          <p className="section-description">
            Describe your organization's network requirements
            in natural language.
          </p>

          <textarea
            value={requirement}
            onChange={(e) => setRequirement(e.target.value)}
            placeholder="Example: Design a secure college network for 500 users across CSE, ECE, EEE, ME and CE departments with VLANs, WiFi, firewall, Internet access and OSPF routing."
            rows={6}
          />

          <button
            className="generate-button"
            onClick={generateNetwork}
            disabled={loading}
          >
            {loading
              ? "Generating Network Design..."
              : "Generate Network Design"}
          </button>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

        </section>

        {/* ==================================================
            NETWORK RESULT
        ================================================== */}

        {result && (
          <>

            {/* ==================================================
                INTENT
            ================================================== */}

            <section className="result-section">

              <h2>Extracted Network Intent</h2>

              <div className="info-grid">

                <div className="info-card">
                  <span>Organization</span>
                  <strong>
                    {result.intent?.organization_name ||
                      result.intent?.organization_type ||
                      "N/A"}
                  </strong>
                </div>

                <div className="info-card">
                  <span>Users</span>
                  <strong>
                    {result.intent?.number_of_users || "N/A"}
                  </strong>
                </div>

                <div className="info-card">
                  <span>Departments</span>
                  <strong>
                    {result.intent?.number_of_departments || "N/A"}
                  </strong>
                </div>

                <div className="info-card">
                  <span>Buildings</span>
                  <strong>
                    {result.intent?.number_of_buildings || "N/A"}
                  </strong>
                </div>

                <div className="info-card">
                  <span>Routing</span>
                  <strong>
                    {result.intent?.routing_protocol || "N/A"}
                  </strong>
                </div>

                <div className="info-card">
                  <span>Firewall</span>
                  <strong>
                    {result.intent?.firewall_required
                      ? "Required"
                      : "Not Required"}
                  </strong>
                </div>

              </div>

            </section>

            {/* ==================================================
                NETWORK TOPOLOGY
            ================================================== */}

            <section className="result-section">

              <h2>Network Topology</h2>

              <p className="section-description">
                Interactive visualization of the generated
                network architecture.
              </p>

              <div className="topology-container">
                <NetworkTopology
                  plan={result.network_plan}
                />
              </div>

            </section>

            {/* ==================================================
                NETWORK OVERVIEW
            ================================================== */}

            <section className="result-section">

              <h2>Network Overview</h2>

              <div className="overview-grid">

                <div className="overview-card">
                  <span>Architecture</span>
                  <strong>
                    {result.network_plan?.architecture ||
                      "N/A"}
                  </strong>
                </div>

                <div className="overview-card">
                  <span>Topology</span>
                  <strong>
                    {result.network_plan?.topology ||
                      "N/A"}
                  </strong>
                </div>

                <div className="overview-card">
                  <span>Routing Protocol</span>
                  <strong>
                    {result.network_plan?.routing_protocol ||
                      "N/A"}
                  </strong>
                </div>

                <div className="overview-card">
                  <span>VLANs</span>
                  <strong>
                    {result.network_plan?.vlans?.length || 0}
                  </strong>
                </div>

              </div>

            </section>

            {/* ==================================================
                VLAN CONFIGURATION
            ================================================== */}

            <section className="result-section">

              <h2>VLAN Configuration</h2>

              <div className="table-container">

                <table>

                  <thead>
                    <tr>
                      <th>VLAN ID</th>
                      <th>Name</th>
                      <th>Purpose</th>
                      <th>Users</th>
                    </tr>
                  </thead>

                  <tbody>

                    {result.network_plan?.vlans?.map(
                      (vlan) => (
                        <tr key={vlan.vlan_id}>
                          <td>{vlan.vlan_id}</td>
                          <td>{vlan.name}</td>
                          <td>{vlan.purpose}</td>
                          <td>{vlan.estimated_users}</td>
                        </tr>
                      )
                    )}

                  </tbody>

                </table>

              </div>

            </section>

            {/* ==================================================
                IP ADDRESSING
            ================================================== */}

            <section className="result-section">

              <h2>IP Addressing</h2>

              <div className="table-container">

                <table>

                  <thead>
                    <tr>
                      <th>VLAN</th>
                      <th>Network</th>
                      <th>Gateway</th>
                    </tr>
                  </thead>

                  <tbody>

                    {result.network_plan?.ip_networks?.map(
                      (network, index) => (
                        <tr key={index}>
                          <td>{network.vlan_id}</td>
                          <td>{network.network}</td>
                          <td>{network.gateway}</td>
                        </tr>
                      )
                    )}

                  </tbody>

                </table>

              </div>

            </section>

            {/* ==================================================
                DEVICE REQUIREMENTS
            ================================================== */}

            <section className="result-section">

              <h2>Device Requirements</h2>

              <div className="device-grid">

                {result.network_plan?.devices?.map(
                  (device, index) => (
                    <div
                      className="device-card"
                      key={index}
                    >
                      <h3>{device.device_type}</h3>

                      <div className="device-quantity">
                        {device.quantity}
                      </div>

                      <p>{device.purpose}</p>
                    </div>
                  )
                )}

              </div>

            </section>

            {/* ==================================================
                SERVICES & SECURITY
            ================================================== */}

            <section className="result-section">

              <div className="two-column">

                <div>

                  <h2>Services</h2>

                  <div className="tag-container">

                    {result.network_plan?.services?.map(
                      (service, index) => (
                        <span
                          className="tag"
                          key={index}
                        >
                          {service}
                        </span>
                      )
                    )}

                  </div>

                </div>

                <div>

                  <h2>Security Features</h2>

                  <div className="tag-container">

                    {result.network_plan?.security_features?.map(
                      (feature, index) => (
                        <span
                          className="tag security-tag"
                          key={index}
                        >
                          {feature}
                        </span>
                      )
                    )}

                  </div>

                </div>

              </div>

            </section>

            {/* ==================================================
                RECOMMENDATIONS
            ================================================== */}

            {result.network_plan?.recommendations?.length >
              0 && (
              <section className="result-section">

                <h2>Recommendations</h2>

                <ul className="recommendation-list">

                  {result.network_plan.recommendations.map(
                    (recommendation, index) => (
                      <li key={index}>
                        {recommendation}
                      </li>
                    )
                  )}

                </ul>

              </section>
            )}

            {/* ==================================================
                CISCO CONFIGURATION GENERATOR
            ================================================== */}

            <section className="result-section config-panel">

              <div className="config-header">

                <div>
                  <h2>Cisco Configuration Generator</h2>

                  <p className="section-description">
                    Generate Cisco-style configurations
                    based on the generated network plan.
                  </p>
                </div>

                <button
                  className="generate-button"
                  onClick={generateConfigurations}
                  disabled={configLoading}
                >
                  {configLoading
                    ? "Generating..."
                    : "Generate Configurations"}
                </button>

              </div>

              {configError && (
                <div className="error-message">
                  {configError}
                </div>
              )}

              {configurations && (
                <div className="configuration-content">

                  {/* Device Selector */}

                  <div className="device-selector">

                    <label htmlFor="device-select">
                      Select Device
                    </label>

                    <select
                      id="device-select"
                      value={selectedDevice}
                      onChange={(e) =>
                        setSelectedDevice(e.target.value)
                      }
                    >

                      {Object.keys(configurations).map(
                        (device) => (
                          <option
                            key={device}
                            value={device}
                          >
                            {formatName(device)}
                          </option>
                        )
                      )}

                    </select>

                  </div>

                  {/* Configuration Viewer */}

                  {selectedDevice &&
                    configurations[selectedDevice] && (
                      <div className="configuration-viewer">

                        <div className="config-viewer-header">

                          <h3>
                            {formatName(selectedDevice)}
                          </h3>

                          <div className="config-actions">

                            <button
                              onClick={copyConfiguration}
                            >
                              Copy
                            </button>

                            <button
                              onClick={
                                downloadConfiguration
                              }
                            >
                              Download
                            </button>

                          </div>

                        </div>

                        <pre className="config-code">
                          {configurations[selectedDevice]}
                        </pre>

                      </div>
                    )}

                </div>
              )}

            </section>

            {/* ==================================================
                CONFIGURATION VALIDATION
            ================================================== */}

            <section className="result-section validation-panel">

              <div className="validation-header">

                <div>
                  <h2>Configuration Validation</h2>

                  <p className="section-description">
                    Validate the generated network
                    configuration against the network plan.
                  </p>
                </div>

                <button
                  className="validate-button"
                  onClick={validateConfigurations}
                  disabled={validationLoading}
                >
                  {validationLoading
                    ? "Validating..."
                    : "Validate Configuration"}
                </button>

              </div>

              {validationError && (
                <div className="validation-error">
                  {validationError}
                </div>
              )}

              {validationResult && (
                <div className="validation-content">

                  {/* Overall Status */}

                  <div
                    className={`validation-status ${
                      validationResult.valid
                        ? "validation-success"
                        : "validation-failure"
                    }`}
                  >

                    <span className="validation-icon">
                      {validationResult.valid
                        ? "✓"
                        : "✗"}
                    </span>

                    <div>
                      <strong>
                        {validationResult.valid
                          ? "Configuration Valid"
                          : "Configuration Invalid"}
                      </strong>

                      <p>
                        {validationResult.summary}
                      </p>
                    </div>

                  </div>

                  {/* Validation Checks */}

                  <div className="validation-checks">

                    {Object.entries(
                      validationResult.checks || {}
                    ).map(([check, status]) => (

                      <div
                        className="validation-check"
                        key={check}
                      >

                        <span>
                          {formatName(check)}
                        </span>

                        <strong
                          className={
                            status === "PASS"
                              ? "pass"
                              : "fail"
                          }
                        >
                          {status}
                        </strong>

                      </div>

                    ))}

                  </div>

                  {/* Errors */}

                  {validationResult.errors?.length >
                    0 && (
                    <div className="validation-errors">

                      <h3>Validation Errors</h3>

                      {validationResult.errors.map(
                        (validationError, index) => (
                          <p key={index}>
                            • {validationError}
                          </p>
                        )
                      )}

                    </div>
                  )}

                </div>
              )}

            </section>

          </>
        )}

      </main>

    </div>
  );
}

export default App;