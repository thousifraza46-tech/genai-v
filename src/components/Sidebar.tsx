import { MessageSquare, Video, Sparkles, History, Home, Settings, Scissors, Wand2 } from "lucide-react";
import { NavLink } from "./NavLink";

const Sidebar = () => {
  const navItems = [
    { icon: MessageSquare, label: "AI Chat", path: "/app", animation: "animate-bounce-subtle" },
    { icon: Video, label: "Generate Video", path: "/generate-video", animation: "animate-pulse-subtle" },
    { icon: Scissors, label: "Editor Lab", path: "/editor-lab", animation: "animate-wiggle" },
    { icon: Wand2, label: "Image to Video", path: "/animation", animation: "animate-spin-slow" },
    { icon: History, label: "History", path: "/history", animation: "animate-swing" },
    { icon: Settings, label: "Settings", path: "/settings", animation: "animate-rotate-slow" },
  ];

  return (
    <aside className="fixed left-0 top-16 bottom-0 w-20 bg-card/80 backdrop-blur-sm border-r border-border flex flex-col items-center py-6 gap-2 z-40">
      {navItems.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          className="w-16 h-16 rounded-xl flex flex-col items-center justify-center gap-1 text-muted-foreground hover:text-primary hover:bg-secondary/50 transition-smooth group"
          activeClassName="bg-primary/10 text-primary shadow-soft"
        >
          <item.icon className={`w-5 h-5 group-hover:scale-110 transition-smooth group-hover:${item.animation}`} />
          <span className="text-[10px] font-medium text-center leading-tight">{item.label}</span>
        </NavLink>
      ))}
    </aside>
  );
};

export default Sidebar;
