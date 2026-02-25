import React, { useState } from "react";
import axios from "axios";
import { toast } from "sonner";

const BACKEND = process.env.REACT_APP_BACKEND_URL || "http://localhost:8002";

const SCENARIO_INFO = {
  "Normal Operation": {
    desc: "No attack, minimal noise. Verifies the system does not generate false alarms during healthy operation.",
    icon: "✓",
  },
  "Sensor Spoofing": {
    desc: "A hacker forces the speed sensor to report a value higher than reality. The system should detect the physics inconsistency (voltage/current vs. reported speed).",
    icon: "⚡",
  },
  "Packet Dropout": {
    desc: "Network packets carrying sensor data are dropped. The system should detect the dropout pattern and flag it as a cyber incident.",
    icon: "📡",
  },
  "Friction Buildup": {
    desc: "Physical wear causes friction to increase gradually. The motor slows down. Speed should drop measurably compared to healthy baseline.",
    icon: "⚙️",
  },
  "Bearing Fault": {
    desc: "A bearing fault introduces vibration. Speed readings should show increased variance/noise after fault onset.",
    icon: "🔩",
  },
};

export default function VerificationView() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleRun = async () => {
    setLoading(true);
    setResults(null);
    try {
      const { data } = await axios.post(`${BACKEND}/api/verify`);
      setResults(data);
      const { passed, failed } = data.summary;
      if (failed === 0) {
        toast.success(`All ${passed} scenarios passed`);
      } else {
        toast.warning(`${passed} passed · ${failed} failed`);
      }
    } catch (err) {
      toast.error(err.response?.data?.detail ?? "Backend error");
    } finally {
      setLoading(false);
    }
  };

  const summary = results?.summary;

  return (
    <div className="flex flex-col h-full">
      {/* Header bar */}
      <div className="shrink-0 border-b border-slate-800 bg-slate-900 px-6 py-4 flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold text-white">Verification Suite</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Runs 5 preset scenarios to validate AI detection + physics fault response
          </p>
        </div>
        <button onClick={handleRun} disabled={loading}
          className="bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500
                     text-white text-sm font-semibold px-5 py-2 rounded transition-colors">
          {loading ? "Running 5 scenarios…" : "▶ Run All Tests"}
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-6 py-5 space-y-5">

        {/* Summary bar */}
        {summary && (
          <div className="flex gap-3">
            <div className={`flex-1 rounded-lg border px-4 py-3 ${summary.failed === 0 ? "bg-green-950 border-green-800" : "bg-red-950 border-red-800"}`}>
              <p className="text-xs text-slate-400">Overall Result</p>
              <p className={`text-lg font-bold ${summary.failed === 0 ? "text-green-400" : "text-red-400"}`}>
                {summary.failed === 0 ? "ALL PASSED" : `${summary.failed} FAILED`}
              </p>
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-lg px-4 py-3 min-w-[100px]">
              <p className="text-xs text-slate-400">Passed</p>
              <p className="text-green-400 text-lg font-bold">{summary.passed}/{summary.total}</p>
            </div>
          </div>
        )}

        {/* Scenario cards */}
        {results ? (
          <div className="space-y-3">
            {results.scenarios.map((s) => {
              const info = SCENARIO_INFO[s.name] ?? {};
              const passed = s.passed;
              const isError = s.status === "ERROR";
              return (
                <div
                  key={s.name}
                  className={`border rounded-lg p-4 space-y-2
                    ${isError ? "border-yellow-700 bg-yellow-950/30"
                      : passed ? "border-green-800 bg-green-950/20"
                               : "border-red-800 bg-red-950/20"}`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{info.icon ?? "?"}</span>
                      <div>
                        <p className="text-sm font-semibold text-white">{s.name}</p>
                        <p className="text-xs text-slate-500">{info.desc}</p>
                      </div>
                    </div>
                    <span className={`shrink-0 text-xs font-bold px-2 py-0.5 rounded
                      ${isError ? "bg-yellow-800 text-yellow-200"
                        : passed ? "bg-green-800 text-green-100"
                                 : "bg-red-800 text-red-100"}`}>
                      {s.status}
                    </span>
                  </div>

                  {!isError && (
                    <div className="grid grid-cols-2 gap-3 pt-1">
                      <div className="bg-slate-900/60 rounded px-3 py-2">
                        <p className="text-xs text-slate-500">{s.metric_label}</p>
                        <p className={`text-sm font-semibold ${passed ? "text-green-400" : "text-red-400"}`}>
                          {s.metric_value}
                        </p>
                      </div>
                      <div className="bg-slate-900/60 rounded px-3 py-2">
                        <p className="text-xs text-slate-500">Threshold</p>
                        <p className="text-sm text-slate-300">{s.threshold}</p>
                      </div>
                    </div>
                  )}

                  {isError && (
                    <p className="text-xs text-yellow-400 font-mono">{s.error}</p>
                  )}
                </div>
              );
            })}
          </div>
        ) : !loading ? (
          /* Pre-run: show what each scenario does */
          <div className="space-y-3">
            <p className="text-xs text-slate-500">
              Click <strong>Run All Tests</strong> to execute all 5 scenarios automatically. Each uses a preset configuration and checks a specific pass/fail criterion.
            </p>
            {Object.entries(SCENARIO_INFO).map(([name, info]) => (
              <div key={name} className="bg-slate-900 border border-slate-800 rounded-lg p-4 flex gap-3">
                <span className="text-xl shrink-0">{info.icon}</span>
                <div>
                  <p className="text-sm font-semibold text-white">{name}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{info.desc}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center gap-3 text-slate-400 text-sm">
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" className="opacity-25" />
              <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" className="opacity-75" />
            </svg>
            Running 5 scenarios sequentially — this may take 30–60 seconds…
          </div>
        )}

        {/* Explainer */}
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-4 text-xs text-slate-400 space-y-1">
          <p className="text-white font-semibold text-sm mb-2">What This Tests</p>
          <p><span className="text-red-400 font-medium">Cyber scenarios</span> verify XGBoost detects attacks at &gt;80% rate after the attack begins.</p>
          <p><span className="text-orange-400 font-medium">Normal scenario</span> verifies the system has &lt;10% false-positive rate under clean conditions.</p>
          <p><span className="text-yellow-400 font-medium">Physical fault scenarios</span> verify the sensor physics respond correctly (friction slows the motor; bearing faults add vibration).</p>
        </div>
      </div>
    </div>
  );
}
