import React from "react";
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
import { Download, Database } from "lucide-react";
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

const ResultsViewer = ({ results, params, onExport }) => {
  if (!results) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-muted-foreground p-8">
        <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
            <Database className="w-8 h-8 opacity-50" />
        </div>
        <h3 className="text-lg font-medium">No Simulation Data</h3>
        <p className="text-sm max-w-md text-center mt-2">
          Configure parameters in the left panel and click "Run Simulation" to generate digital twin data.
        </p>
      </div>
    );
  }

  // Prepare data for Recharts
  const chartData = results.time.map((t, i) => ({
    time: t,
    omega_true: results.omega_true[i],
    omega_sensor: results.omega_sensor[i],
    torque: results.torque[i],
    load: results.load[i],
    attack_type: results.attack_type?.[i],
    attack_active: results.attack_active?.[i],
    fault_type: results.fault_type?.[i],
    fault_active: results.fault_active?.[i],
  }));

  return (
    <div className="h-full overflow-y-auto custom-scrollbar p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
            <h2 className="text-2xl font-bold tracking-tight">Simulation Results</h2>
            <div className="flex gap-2 mt-2">
                <Badge variant="outline" className="text-xs">
                    Duration: {params.duration}s
                </Badge>
                {params.fault_type !== "None" && (
                    <Badge variant="destructive" className="bg-accent text-accent-foreground border-accent">
                        Fault: {params.fault_type}
                    </Badge>
                )}
                {params.attack_type !== "None" && (
                    <Badge variant="destructive">
                        Attack: {params.attack_type}
                    </Badge>
                )}
            </div>
        </div>
        <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => onExport('csv')}>
                <Download className="w-4 h-4 mr-2" />
                Export CSV
            </Button>
            <Button variant="outline" size="sm" onClick={() => onExport('json')}>
                <Download className="w-4 h-4 mr-2" />
                Export JSON
            </Button>
        </div>
      </div>

      {/* Main Velocity Chart */}
      <Card className="border-border shadow-sm">
        <CardHeader>
          <CardTitle className="text-base font-medium">Digital Twin Ground Truth vs Virtual Sensor Output</CardTitle>
        </CardHeader>
        <CardContent className="h-[350px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.5} />
              <XAxis 
                dataKey="time" 
                stroke="hsl(var(--muted-foreground))" 
                fontSize={12} 
                tickFormatter={(val) => val.toFixed(1)}
                label={{ value: 'Time (s)', position: 'insideBottomRight', offset: -5, fill: 'hsl(var(--muted-foreground))' }}
              />
              <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
              <Tooltip content={<CustomTooltip />} />
              <Legend verticalAlign="top" height={36}/>
              
              <Line 
                type="monotone" 
                dataKey="omega_true" 
                name="True State (Twin)" 
                stroke="hsl(var(--secondary))" 
                strokeWidth={2} 
                dot={false} 
                activeDot={{ r: 6 }}
              />
              <Line 
                type="monotone" 
                dataKey="omega_sensor" 
                name="Measured Value (Sensor)" 
                stroke="hsl(var(--primary))" 
                strokeWidth={2} 
                strokeDasharray="5 5" 
                dot={false} 
              />
              
              {/* Fault/Attack Markers */}
              {(params.fault_type !== "None") && (
                 <ReferenceLine x={params.fault_start_time} stroke="hsl(var(--accent))" label="Fault Start" strokeDasharray="3 3" />
              )}
              {(params.attack_type !== "None") && (
                 <ReferenceLine x={params.attack_start_time} stroke="hsl(var(--destructive))" label="Attack Start" strokeDasharray="3 3" />
              )}
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Torque & Load Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-border shadow-sm">
            <CardHeader>
            <CardTitle className="text-base font-medium">Motor Torque vs Load Torque (Twin Predicted Dynamics)</CardTitle>
            </CardHeader>
            <CardContent className="h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.5} />
                <XAxis dataKey="time" hide />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <Tooltip content={<CustomTooltip />} />
                <Legend verticalAlign="top" height={36}/>
                
                <Area 
                    type="monotone" 
                    dataKey="torque" 
                    name="Motor Torque" 
                    stroke="hsl(var(--chart-4))" 
                    fill="hsl(var(--chart-4))" 
                    fillOpacity={0.2}
                />
                <Area 
                    type="step" 
                    dataKey="load" 
                    name="Load Torque" 
                    stroke="hsl(var(--chart-5))" 
                    fill="hsl(var(--chart-5))" 
                    fillOpacity={0.2}
                />
                </AreaChart>
            </ResponsiveContainer>
            </CardContent>
        </Card>

        <Card className="border-border shadow-sm">
            <CardHeader>
            <CardTitle className="text-base font-medium">Sensor–Twin Residual (|Measured − True|)</CardTitle>
            </CardHeader>
            <CardContent className="h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.5} />
                <XAxis dataKey="time" hide />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <Tooltip content={<CustomTooltip />} />
                <Legend verticalAlign="top" height={36}/>
                
                <Line 
                    type="monotone" 
                    dataKey={(d) => d.omega_sensor !== null ? Math.abs(d.omega_sensor - d.omega_true) : 0} 
                    name="Residual Anomaly" 
                    stroke="hsl(var(--destructive))" 
                    strokeWidth={1.5} 
                    dot={false} 
                />
                </LineChart>
            </ResponsiveContainer>
            </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ResultsViewer;
