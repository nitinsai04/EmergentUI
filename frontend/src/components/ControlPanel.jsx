import React, { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { Play, AlertTriangle, ShieldAlert, Activity } from "lucide-react";

const ControlPanel = ({ params, setParams, onRun, loading }) => {
  const handleChange = (key, value) => {
    setParams((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="h-full flex flex-col bg-card border-r border-border overflow-y-auto custom-scrollbar">
      <div className="p-6 border-b border-border">
        <h2 className="text-xl font-bold flex items-center gap-2 text-primary">
          <Activity className="w-5 h-5" />
          Simulation Control
        </h2>
        <p className="text-sm text-muted-foreground mt-1">
          Configure digital twin parameters
        </p>
      </div>

      <div className="flex-1 p-4">
        <Tabs defaultValue="physics" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-4">
            <TabsTrigger value="physics">Physics</TabsTrigger>
            <TabsTrigger value="faults">Faults</TabsTrigger>
            <TabsTrigger value="attacks">Cyber</TabsTrigger>
          </TabsList>

          {/* PHYSICS TAB */}
          <TabsContent value="physics" className="space-y-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Voltage (V)</Label>
                <div className="flex items-center gap-4">
                  <Slider
                    value={[params.voltage]}
                    min={0}
                    max={24}
                    step={0.1}
                    onValueChange={(val) => handleChange("voltage", val[0])}
                    className="flex-1"
                  />
                  <Input
                    type="number"
                    value={params.voltage}
                    onChange={(e) => handleChange("voltage", parseFloat(e.target.value))}
                    className="w-20 h-8"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Load Torque (Nm)</Label>
                <div className="flex items-center gap-4">
                  <Slider
                    value={[params.load_torque]}
                    min={0}
                    max={5}
                    step={0.1}
                    onValueChange={(val) => handleChange("load_torque", val[0])}
                    className="flex-1"
                  />
                  <Input
                    type="number"
                    value={params.load_torque}
                    onChange={(e) => handleChange("load_torque", parseFloat(e.target.value))}
                    className="w-20 h-8"
                  />
                </div>
              </div>

              <Separator />

              <div className="space-y-2">
                <Label>Inertia (J)</Label>
                <Slider
                  value={[params.J]}
                  min={1}
                  max={50}
                  step={1}
                  onValueChange={(val) => handleChange("J", val[0])}
                />
                <div className="text-xs text-muted-foreground text-right">{params.J} kg·m²</div>
              </div>

              <div className="space-y-2">
                <Label>Friction (b)</Label>
                <Slider
                  value={[params.b]}
                  min={0.001}
                  max={0.1}
                  step={0.001}
                  onValueChange={(val) => handleChange("b", val[0])}
                />
                <div className="text-xs text-muted-foreground text-right">{params.b} Nms</div>
              </div>
              
              <div className="space-y-2">
                <Label>Torque Constant (Kt)</Label>
                <Slider
                  value={[params.Kt]}
                  min={0.01}
                  max={1.0}
                  step={0.01}
                  onValueChange={(val) => handleChange("Kt", val[0])}
                />
                <div className="text-xs text-muted-foreground text-right">{params.Kt} Nm/A</div>
              </div>

               <Separator />

               <div className="space-y-2">
                <Label>Simulation Duration (s)</Label>
                <Slider
                  value={[params.duration]}
                  min={1}
                  max={60}
                  step={1}
                  onValueChange={(val) => handleChange("duration", val[0])}
                />
                <div className="text-xs text-muted-foreground text-right">{params.duration} s</div>
              </div>
            </div>
          </TabsContent>

          {/* FAULTS TAB */}
          <TabsContent value="faults" className="space-y-6">
            <Card className="border-accent/20 bg-accent/5">
                <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium flex items-center gap-2 text-accent">
                        <AlertTriangle className="w-4 h-4" />
                        Fault Injection
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="space-y-2">
                        <Label>Fault Type</Label>
                        <Select 
                            value={params.fault_type} 
                            onValueChange={(val) => handleChange("fault_type", val)}
                        >
                            <SelectTrigger>
                                <SelectValue placeholder="Select Fault" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="None">None (Healthy)</SelectItem>
                                <SelectItem value="Bearing Friction">Bearing Friction Increase</SelectItem>
                                <SelectItem value="Torque Drop">Torque Drop (Coil Short)</SelectItem>
                                <SelectItem value="Sudden Load Spike">Sudden Load Spike</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    {params.fault_type !== "None" && (
                        <>
                            <div className="space-y-2">
                                <Label>Severity (0-1)</Label>
                                <Slider
                                    value={[params.fault_severity]}
                                    min={0}
                                    max={1}
                                    step={0.05}
                                    onValueChange={(val) => handleChange("fault_severity", val[0])}
                                />
                                <div className="text-xs text-muted-foreground text-right">{params.fault_severity}</div>
                            </div>
                            <div className="space-y-2">
                                <Label>Start Time (s)</Label>
                                <Slider
                                    value={[params.fault_start_time]}
                                    min={0}
                                    max={params.duration}
                                    step={0.5}
                                    onValueChange={(val) => handleChange("fault_start_time", val[0])}
                                />
                                <div className="text-xs text-muted-foreground text-right">{params.fault_start_time} s</div>
                            </div>
                        </>
                    )}
                </CardContent>
            </Card>
          </TabsContent>

          {/* ATTACKS TAB */}
          <TabsContent value="attacks" className="space-y-6">
             <Card className="border-destructive/20 bg-destructive/5">
                <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium flex items-center gap-2 text-destructive">
                        <ShieldAlert className="w-4 h-4" />
                        Cyber Attack
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="space-y-2">
                        <Label>Attack Type</Label>
                        <Select 
                            value={params.attack_type} 
                            onValueChange={(val) => handleChange("attack_type", val)}
                        >
                            <SelectTrigger>
                                <SelectValue placeholder="Select Attack" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="None">None (Secure)</SelectItem>
                                <SelectItem value="Sensor Spoofing">Sensor Spoofing (Offset)</SelectItem>
                                <SelectItem value="Freezing Sensor">Freezing Sensor (Replay)</SelectItem>
                                <SelectItem value="Packet Dropout">Packet Dropout (DoS)</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    {params.attack_type !== "None" && (
                        <>
                            <div className="space-y-2">
                                <Label>Magnitude / Probability</Label>
                                <Slider
                                    value={[params.attack_magnitude]}
                                    min={0}
                                    max={5} // Arbitrary scale depending on attack
                                    step={0.1}
                                    onValueChange={(val) => handleChange("attack_magnitude", val[0])}
                                />
                                <div className="text-xs text-muted-foreground text-right">{params.attack_magnitude}</div>
                            </div>
                            <div className="space-y-2">
                                <Label>Start Time (s)</Label>
                                <Slider
                                    value={[params.attack_start_time]}
                                    min={0}
                                    max={params.duration}
                                    step={0.5}
                                    onValueChange={(val) => handleChange("attack_start_time", val[0])}
                                />
                                <div className="text-xs text-muted-foreground text-right">{params.attack_start_time} s</div>
                            </div>
                        </>
                    )}
                </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      <div className="p-6 border-t border-border bg-card">
        <Button 
            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/20" 
            size="lg"
            onClick={onRun}
            disabled={loading}
        >
          {loading ? "Simulating..." : (
            <>
                <Play className="w-4 h-4 mr-2 fill-current" />
                Run Simulation
            </>
          )}
        </Button>
      </div>
    </div>
  );
};

export default ControlPanel;
