import React, { useState } from "react";
import ControlPanel from "./ControlPanel";
import ResultsViewer from "./ResultsViewer";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8001";
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

  const handleRunSimulation = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/simulate`, params);
      setResults(response.data);
      toast.success("Simulation completed successfully");
    } catch (error) {
      console.error("Simulation failed:", error);
      toast.error("Simulation failed. Check backend connection.");
      
      // Fallback Mock Data for Prototype if Backend is down
      // This ensures the UI is reviewable even if backend has issues
      const mockTime = Array.from({ length: 100 }, (_, i) => i * 0.2);
      setResults({
        time: mockTime,
        omega_true: mockTime.map(t => Math.sin(t) * 10 + 50),
        omega_sensor: mockTime.map(t => Math.sin(t) * 10 + 50 + (Math.random() - 0.5)),
        torque: mockTime.map(t => 5),
        load: mockTime.map(t => 2),
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExport = (format) => {
    if (!results) return;
    
    const data = results.time.map((t, i) => ({
        time: t,
        omega_true: results.omega_true[i],
        omega_sensor: results.omega_sensor[i],
        torque: results.torque[i],
        load: results.load[i]
    }));

    if (format === 'json') {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'simulation_data.json';
        a.click();
    } else {
        // CSV
        const headers = Object.keys(data[0]).join(',');
        const rows = data.map(row => Object.values(row).join(',')).join('\n');
        const csv = `${headers}\n${rows}`;
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'simulation_data.csv';
        a.click();
    }
    toast.success(`Exported as ${format.toUpperCase()}`);
  };

  return (
    <div className="flex h-screen w-full bg-background text-foreground overflow-hidden">
      {/* Sidebar */}
      <div className="w-[350px] flex-shrink-0 h-full">
        <ControlPanel 
            params={params} 
            setParams={setParams} 
            onRun={handleRunSimulation} 
            loading={loading} 
        />
      </div>

      {/* Main Content */}
      <div className="flex-1 h-full overflow-hidden bg-background/50 relative">
        {/* Grid Background Effect */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none"></div>
        
        <ResultsViewer 
            results={results} 
            params={params}
            onExport={handleExport}
        />
      </div>
      <Toaster />
    </div>
  );
};

export default Dashboard;
