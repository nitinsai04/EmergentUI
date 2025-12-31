import React, { useState } from "react";
import ControlPanel from "./ControlPanel";
import ResultsViewer from "./ResultsViewer";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";
import axios from "axios";

const BACKEND_URL =
  process.env.REACT_APP_BACKEND_URL || "http://localhost:8001";
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [params, setParams] = useState({
    Kt: 0.1,
    J: 10.0,
    b: 0.01,
    load_torque: 0.5,
    voltage: 12.0,
    dt: 0.05,
    duration: 20.0,
    noise_level: 0.05,

    fault_type: "None",
    fault_severity: 0.5,
    fault_start_time: 10.0,

    attack_type: "None",
    attack_magnitude: 2.0,
    attack_start_time: 15.0,
  });

  // ---------------- Run Simulation ----------------
  const handleRunSimulation = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/simulate`, params);
      setResults(response.data);
      toast.success("Simulation completed successfully");
    } catch (error) {
      console.error("Simulation failed:", error);
      toast.error("Simulation failed. Check backend connection.");
    } finally {
      setLoading(false);
    }
  };

  // ---------------- AI Report Generation ----------------
  const handleGenerateReport = () => {
    if (!results) return;

    // Get the final state predictions
    const lastStatus = results.ai_status_text[results.ai_status_text.length - 1];
    const finalRul = results.ai_predicted_rul[results.ai_predicted_rul.length - 1];

    const reportContent = `
DIGITAL TWIN AI DIAGNOSTIC REPORT
=================================
Generated: ${new Date().toLocaleString()}

SYSTEM SUMMARY:
---------------
Final Operational Status: ${lastStatus}
Predicted Remaining Useful Life (RUL): ${finalRul.toFixed(2)} seconds

INPUT PARAMETERS:
-----------------
- Motor Constant (Kt): ${params.Kt}
- Voltage: ${params.voltage}V
- Load Torque: ${params.load_torque}
- Simulation Duration: ${params.duration}s

ANOMALY CONFIGURATION:
----------------------
- Fault Type: ${params.fault_type}
- Attack Type: ${params.attack_type}
- Attack Start Time: ${params.attack_start_time}s

AI ANALYTICS FINDINGS:
----------------------
The XGBoost Classifier analyzed the sensor stream and flagged the system state as "${lastStatus}".
The LSTM Prognostic model calculated a health trajectory resulting in ${finalRul.toFixed(2)}s of functional life.

Status Warning: ${finalRul < 5 ? "CRITICAL - Maintenance Required Immediately" : "OPERATIONAL - No immediate action needed"}
=================================
END OF REPORT
    `;

    const blob = new Blob([reportContent], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `AI_Diagnostic_Report_${Date.now()}.txt`;
    a.click();
    toast.success("AI Summary Report Downloaded");
  };

  // ---------------- Export CSV / JSON ----------------
  const handleExport = (format) => {
    if (!results) return;

    const keys = Object.keys(results);

    // Build row-wise dataset (time-aligned)
    const rows = results.time.map((_, i) =>
      Object.fromEntries(
        keys.map((k) => [k, results[k][i]])
      )
    );

    if (format === "json") {
      const blob = new Blob(
        [JSON.stringify(rows, null, 2)],
        { type: "application/json" }
      );
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "simulation_data.json";
      a.click();
    } else {
      const csv =
        keys.join(",") +
        "\n" +
        rows.map((r) => keys.map((k) => r[k]).join(",")).join("\n");

      const blob = new Blob([csv], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "simulation_data.csv";
      a.click();
    }

    toast.success(`Exported as ${format.toUpperCase()}`);
  };

  return (
    <div className="flex h-screen w-full bg-background text-foreground overflow-hidden flex-col">
      {/* Header */}
      <div className="bg-card border-b border-border p-4 shadow-sm z-10">
        <h1 className="text-lg font-bold text-primary">
          Digital Twin Platform: DC Motor–Pump Asset
        </h1>
        <p className="text-sm text-muted-foreground mt-1 max-w-4xl">
          This interface visualizes a physics-based Digital Twin with virtual
          sensors, physical faults, and cyber-attacks for robustness evaluation
          and dataset generation.
        </p>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div className="w-[350px] flex-shrink-0 h-full border-r border-border">
          <ControlPanel
            params={params}
            setParams={setParams}
            onRun={handleRunSimulation}
            loading={loading}
          />
        </div>

        {/* Main Content */}
        <div className="flex-1 h-full overflow-hidden bg-background/50 relative">
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none"></div>

          <ResultsViewer
            results={results}
            params={params}
            onExport={handleExport}
            onGenerateReport={handleGenerateReport} // PASSING THE NEW FUNCTION
          />
        </div>
      </div>

      <Toaster />
    </div>
  );
};

export default Dashboard;