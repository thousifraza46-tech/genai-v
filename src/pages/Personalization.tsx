import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Beaker } from "lucide-react";

const Personalization = () => {
  return (
    <div className="h-full p-8">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold mb-8 text-foreground">Editor Lab</h2>
        
        <Card className="p-6 shadow-medium border-border mb-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-20 h-20 rounded-full bg-gradient-primary flex items-center justify-center shadow-soft">
              <Beaker className="w-10 h-10 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-foreground">Experimental Features</h3>
              <p className="text-muted-foreground">Test and customize advanced options</p>
            </div>
          </div>
          
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <Label className="text-base font-medium">Auto-save projects</Label>
                <p className="text-sm text-muted-foreground">Automatically save your work</p>
              </div>
              <Switch defaultChecked />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <Label className="text-base font-medium">Smart suggestions</Label>
                <p className="text-sm text-muted-foreground">Get AI-powered recommendations</p>
              </div>
              <Switch defaultChecked />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <Label className="text-base font-medium">Email notifications</Label>
                <p className="text-sm text-muted-foreground">Receive updates via email</p>
              </div>
              <Switch />
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Personalization;
