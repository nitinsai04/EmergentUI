import React, { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";

const ControlPanel = ({ params, setParams, onRun, loading }) => {
  
  // Local state: user edits here without affecting global UI
  const [localParams, setLocalParams] = useState(params);

  const handleLocalChange = (key, value) => {
    setLocalParams(prev => ({ ...prev, [key]: value }));
  };

  const submitParams = () => {
    setParams(localParams);  // Only now update global params
    onRun();                 // Trigger simulation
  };

  return (
    <div className="h-full flex flex-col bg-card border-r border-border overflow-y-auto">
      <div className="p-6 border-b border-border">
        <h2 className="text-xl font-bold text-primary">Digital Twin Controls</h2>
      </div>

      <div className="p-4 flex-1">
        <Tabs defaultValue="physics">
          <TabsList className="grid w-full grid-cols-3 mb-4">
            <TabsTrigger value="physics">Physics</TabsTrigger>
            <TabsTrigger value="faults">Faults</TabsTrigger>
            <TabsTrigger value="attacks">Attacks</TabsTrigger>
          </TabsList>

          {/* PHYSICS */}
          <TabsContent value="physics" className="space-y-4">
            <div>
              <Label>Voltage</Label>
              <Input
                type="number"
                step="0.1"
                value={localParams.voltage}
                onChange={(e) => handleLocalChange("voltage", parseFloat(e.target.value))}
              />
            </div>

            <div>
              <Label>Load Torque</Label>
              <Input
                type="number"
                step="0.1"
                value={localParams.load_torque}
                onChange={(e) => handleLocalChange("load_torque", parseFloat(e.target.value))}
              />
            </div>

            <Separator />

            <div>
              <Label>Inertia J</Label>
              <Input
                type="number"
                step="1"
                value={localParams.J}
                onChange={(e) => handleLocalChange("J", parseFloat(e.target.value))}
              />
            </div>

            <div>
              <Label>Friction b</Label>
              <Input
                type="number"
                step="0.001"
                value={localParams.b}
                onChange={(e) => handleLocalChange("b", parseFloat(e.target.value))}
              />
            </div>

            <div>
              <Label>Kt</Label>
              <Input
                type="number"
                step="0.01"
                value={localParams.Kt}
                onChange={(e) => handleLocalChange("Kt", parseFloat(e.target.value))}
              />
            </div>

            <div>
              <Label>Duration</Label>
              <Input
                type="number"
                step="1"
                value={localParams.duration}
                onChange={(e) => handleLocalChange("duration", parseFloat(e.target.value))}
              />
            </div>
          </TabsContent>

          {/* FAULTS */}
          <TabsContent value="faults" className="space-y-4">
            <Label>Fault Type</Label>
            <Select
              value={localParams.fault_type}
              onValueChange={(v) => handleLocalChange("fault_type", v)}
            >
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="None">None</SelectItem>
                <SelectItem value="Bearing Friction">Bearing Friction</SelectItem>
                <SelectItem value="Torque Drop">Torque Drop</SelectItem>
                <SelectItem value="Sudden Load Spike">Sudden Load Spike</SelectItem>
              </SelectContent>
            </Select>

            {localParams.fault_type !== "None" && (
              <>
                <div>
                  <Label>Severity</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={localParams.fault_severity}
                    onChange={(e) =>
                      handleLocalChange("fault_severity", parseFloat(e.target.value))
                    }
                  />
                </div>
                <div>
                  <Label>Start Time</Label>
                  <Input
                    type="number"
                    step="0.5"
                    value={localParams.fault_start_time}
                    onChange={(e) =>
                      handleLocalChange("fault_start_time", parseFloat(e.target.value))
                    }
                  />
                </div>
              </>
            )}
          </TabsContent>

          {/* ATTACKS */}
          <TabsContent value="attacks" className="space-y-4">
            <Label>Attack Type</Label>
            <Select
              value={localParams.attack_type}
              onValueChange={(v) => handleLocalChange("attack_type", v)}
            >
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="None">None</SelectItem>
                <SelectItem value="Sensor Spoofing">Sensor Spoofing</SelectItem>
                <SelectItem value="Freezing Sensor">Freezing Sensor</SelectItem>
                <SelectItem value="Packet Dropout">Packet Dropout</SelectItem>
              </SelectContent>
            </Select>

            {localParams.attack_type !== "None" && (
              <>
                <div>
                  <Label>Magnitude</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={localParams.attack_magnitude}
                    onChange={(e) =>
                      handleLocalChange(
                        "attack_magnitude",
                        parseFloat(e.target.value)
                      )
                    }
                  />
                </div>

                <div>
                  <Label>Start Time</Label>
                  <Input
                    type="number"
                    step="0.5"
                    value={localParams.attack_start_time}
                    onChange={(e) =>
                      handleLocalChange(
                        "attack_start_time",
                        parseFloat(e.target.value)
                      )
                    }
                  />
                </div>
              </>
            )}
          </TabsContent>
        </Tabs>
      </div>

      {/* RUN BUTTON */}
      <div className="p-6 border-t border-border">
        <Button className="w-full" onClick={submitParams} disabled={loading}>
          {loading ? "Simulating..." : "Run Simulation"}
        </Button>
      </div>
    </div>
  );
};

export default ControlPanel;
