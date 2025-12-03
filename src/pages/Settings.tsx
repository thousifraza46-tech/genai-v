import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Settings as SettingsIcon } from "lucide-react";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";

const Settings = () => {
  const [language, setLanguage] = useState("en");
  const [theme, setTheme] = useState("light");
  const { toast } = useToast();

  const handleLanguageChange = (value: string) => {
    setLanguage(value);
    const languageNames: { [key: string]: string } = {
      en: "English",
      es: "Spanish",
      fr: "French",
      de: "German"
    };
    toast({
      title: "Language Updated",
      description: `Language changed to ${languageNames[value]}`,
    });
  };

  const handleThemeChange = (value: string) => {
    setTheme(value);
    
    // Apply theme to document
    if (value === "dark") {
      document.documentElement.classList.add("dark");
    } else if (value === "light") {
      document.documentElement.classList.remove("dark");
    } else {
      // Auto mode - detect system preference
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      if (prefersDark) {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
    }
    
    const themeNames: { [key: string]: string } = {
      light: "Light",
      dark: "Dark",
      auto: "Auto (System)"
    };
    toast({
      title: "Theme Updated",
      description: `Theme changed to ${themeNames[value]}`,
    });
  };

  return (
    <div className="h-full p-8">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold mb-8 text-foreground">Settings</h2>
        
        <Card className="p-6 shadow-medium border-border">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-xl bg-gradient-primary flex items-center justify-center shadow-soft">
              <SettingsIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-foreground">General Settings</h3>
              <p className="text-muted-foreground">Manage your preferences</p>
            </div>
          </div>
          
          <div className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="language">Language</Label>
              <Select value={language} onValueChange={handleLanguageChange}>
                <SelectTrigger id="language" className="border-border">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="es">Spanish</SelectItem>
                  <SelectItem value="fr">French</SelectItem>
                  <SelectItem value="de">German</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="theme">Theme</Label>
              <Select value={theme} onValueChange={handleThemeChange}>
                <SelectTrigger id="theme" className="border-border">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="light">Light</SelectItem>
                  <SelectItem value="dark">Dark</SelectItem>
                  <SelectItem value="auto">Auto</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Settings;
