import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import { Bot } from "lucide-react";

const TopBar = () => {
  return (
    <header className="h-16 border-b border-border bg-card/50 backdrop-blur-sm flex items-center justify-end px-6 shadow-soft">
      <Avatar className="w-10 h-10 border-2 border-primary/20 shadow-soft cursor-pointer hover:border-primary transition-smooth">
        <AvatarImage src="https://api.dicebear.com/7.x/avataaars/svg?seed=User" />
        <AvatarFallback className="bg-gradient-primary text-white">U</AvatarFallback>
      </Avatar>
    </header>
  );
};

export default TopBar;
