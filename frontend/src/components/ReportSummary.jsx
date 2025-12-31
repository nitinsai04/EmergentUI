import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle, CheckCircle2, ShieldAlert, Zap } from "lucide-react";

const ReportSummary = ({ results }) => {
  if (!results || !results.ai_attack_label) return null;

  const labels = results.ai_attack_label;
  const rul = results.ai_predicted_rul;
  const lastRul = rul[rul.length - 1];
  
  // Analysis Logic
  const uniqueLabels = [...new Set(labels)];
  const attackDetected = uniqueLabels.some(l => l > 1);
  const faultDetected = uniqueLabels.includes(1);
  
  // Calculate RUL drop percentage
  const initialRul = rul[0];
  const rulDrop = ((initialRul - lastRul) / initialRul) * 100;

  const getStatusConfig = () => {
    if (attackDetected) return { color: "text-red-500", icon: <ShieldAlert />, title: "Security Breach Detected" };
    if (faultDetected) return { color: "text-yellow-500", icon: <Zap />, title: "Mechanical Degradation Noted" };
    return { color: "text-green-500", icon: <CheckCircle2 />, title: "System Nominal" };
  };

  const config = getStatusConfig();

  return (
    <Card className="border-2 border-border mt-6">
      <CardHeader className="border-b bg-muted/30">
        <CardTitle className={`flex items-center gap-2 ${config.color}`}>
          {config.icon}
          AI Final Analysis Report
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-6 space-y-4 text-sm leading-relaxed">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-card border">
            <h4 className="font-bold mb-2 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-primary" />
              Event Timeline
            </h4>
            <ul className="list-disc pl-5 space-y-1">
              <li>Simulation lasted {results.time[results.time.length-1].toFixed(1)} seconds.</li>
              {attackDetected && <li>AI identified malicious sensor patterns (Attack Class {Math.max(...labels)}).</li>}
              {faultDetected && <li>AI detected physical torque deviations consistent with a mechanical fault.</li>}
              {!attackDetected && !faultDetected && <li>No anomalies were detected by the XGBoost classifier.</li>}
            </ul>
          </div>

          <div className="p-4 rounded-lg bg-card border">
            <h4 className="font-bold mb-2 flex items-center gap-2">
              <Activity className="w-4 h-4 text-orange-500" />
              Prognostics (LSTM)
            </h4>
            <ul className="list-disc pl-5 space-y-1">
              <li>Final RUL: {lastRul.toFixed(2)} seconds.</li>
              <li>System health dropped by {rulDrop.toFixed(1)}% during this run.</li>
              {lastRul < 1 ? (
                <li className="text-destructive font-bold">Urgent: Failure imminent. Immediate maintenance required.</li>
              ) : (
                <li className="text-green-600">Health levels remain within safety thresholds.</li>
              )}
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ReportSummary;