import React from "react";
import ReportSummary from "./ReportSummary";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  AreaChart,
  Area
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Download, Database, Activity, Clock, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-popover border border-border p-3 rounded-md shadow-xl text-xs">
        <p className="font-bold mb-1 text-foreground">{`Time: ${Number(label).toFixed(2)}s`}</p>
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center gap-2" style={{ color: entry.color }}>
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }}></span>
            <span>{entry.name}: {Number(entry.value).toFixed(3)}</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

// ADDED onGenerateReport to the props
const ResultsViewer = ({ results, params, onExport, onGenerateReport }) => {
  if (!results) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-muted-foreground p-8">
        <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
            <Database className="w-8 h-8 opacity-50" />
        </div>
        <h3 className="text-lg font-medium">No Simulation Data</h3>
        <p className="text-sm max-w-md text-center mt-2">
          Configure parameters in the left panel and click "Run Simulation".
        </p>
      </div>
    );
  }

  const chartData = results.time.map((t, i) => ({
    time: t,
    omega_true: results.omega_true[i],
    omega_sensor: results.omega_sensor[i],
    torque: results.torque[i],
    load: results.load[i],
    ai_status: results.ai_status_text?.[i] || "Normal",
    ai_label: results.ai_attack_label?.[i] || 0,
    ai_rul: results.ai_predicted_rul?.[i] || 0,
  }));

  const currentStatus = chartData[chartData.length - 1].ai_status;
  const isHealthy = chartData[chartData.length - 1].ai_label === 0;

  return (
    <div className="h-full overflow-y-auto custom-scrollbar p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
            <h2 className="text-2xl font-bold tracking-tight">Digital Twin Diagnostics</h2>
            <div className="flex gap-2 mt-2">
                <Badge variant="outline" className="text-xs">
                    Duration: {params.duration}s
                </Badge>
                <Badge className={isHealthy ? "bg-green-600" : "bg-red-600 animate-pulse"}>
                    <Activity className="w-3 h-3 mr-1" />
                    AI Detection: {currentStatus}
                </Badge>
            </div>
        </div>
        <div className="flex gap-2">
            {/* NEW: DOWNLOAD AI REPORT BUTTON */}
            <Button variant="default" size="sm" onClick={onGenerateReport}>
                <FileText className="w-4 h-4 mr-2" />
                Download AI Report
            </Button>

            <Button variant="outline" size="sm" onClick={() => onExport('csv')}>
                <Download className="w-4 h-4 mr-2" />
                Export CSV
            </Button>
        </div>
      </div>

      {/* Physics Chart */}
      <Card className="border-border shadow-sm">
        <CardHeader>
          <CardTitle className="text-base font-medium">Physics vs. Sensor State</CardTitle>
        </CardHeader>
        <CardContent className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.5} />
              <XAxis dataKey="time" tickFormatter={(val) => val.toFixed(1)} />
              <YAxis />
              <Tooltip content={<CustomTooltip />} />
              <Legend verticalAlign="top" />
              <Line type="monotone" dataKey="omega_true" name="Twin State" stroke="#3b82f6" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="omega_sensor" name="Sensor Input" stroke="#10b981" dot={false} strokeDasharray="5 5" />
              {(params.attack_type !== "None") && (
                 <ReferenceLine x={params.attack_start_time} stroke="red" label="Attack" />
              )}
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* RUL Chart */}
      <Card className="border-border shadow-sm border-l-4 border-l-orange-500">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-base font-medium flex items-center gap-2">
            <Clock className="w-4 h-4 text-orange-500" />
            Predictive Maintenance: Remaining Useful Life (RUL)
          </CardTitle>
        </CardHeader>
        <CardContent className="h-[200px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorRul" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f97316" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#f97316" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="time" hide />
              <YAxis label={{ value: 'Sec', angle: -90, position: 'insideLeft' }} />
              <Tooltip content={<CustomTooltip />} />
              <Area 
                type="monotone" 
                dataKey="ai_rul" 
                name="Predicted RUL" 
                stroke="#f97316" 
                fillOpacity={1} 
                fill="url(#colorRul)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Residual Chart */}
      <Card className="border-border shadow-sm">
          <CardHeader>
            <CardTitle className="text-base font-medium">Sensor Anomaly Residual</CardTitle>
          </CardHeader>
          <CardContent className="h-[180px]">
          <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="time" hide />
              <YAxis />
              <Tooltip content={<CustomTooltip />} />
              <Line 
                  type="monotone" 
                  dataKey={(d) => Math.abs(d.omega_sensor - d.omega_true)} 
                  name="Residual Error" 
                  stroke="#ef4444" 
                  dot={false} 
              />
              </LineChart>
          </ResponsiveContainer>
          </CardContent>
      </Card>

      {/* AI Summary Section */}
      <ReportSummary results={results} />
    </div>
  );
};

export default ResultsViewer;