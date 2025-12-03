import { Outlet, useNavigate } from "react-router-dom";
import Sidebar from "./Sidebar";
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import TabAnimations from "./TabAnimations";
import { ConnectionStatus } from "./ConnectionStatus";
import { useEffect, useState } from "react";

const Layout = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const navigate = useNavigate();

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  return (
    <div className="min-h-screen w-full flex flex-col bg-gradient-to-br from-background via-primary/5 to-accent/10 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Floating Particles */}
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-2 h-2 bg-primary/30 rounded-full animate-float"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${5 + Math.random() * 10}s`,
            }}
          />
        ))}
        
        {/* Light Streaks */}
        <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-transparent via-primary/20 to-transparent opacity-50" />
        <div className="absolute top-0 right-0 w-1 h-full bg-gradient-to-b from-transparent via-accent/20 to-transparent opacity-50" />
        
        {/* Parallax Gradient Orbs */}
        <div
          className="absolute w-96 h-96 rounded-full bg-primary/10 blur-3xl animate-pulse-slow"
          style={{
            top: "20%",
            left: "10%",
            transform: `translate(${mousePosition.x * 0.001}px, ${mousePosition.y * 0.001}px)`,
            transition: "transform 0.5s ease-out",
          }}
        />
        <div
          className="absolute w-96 h-96 rounded-full bg-accent/20 blur-3xl animate-pulse-slow"
          style={{
            bottom: "10%",
            right: "10%",
            transform: `translate(${mousePosition.x * -0.005}px, ${mousePosition.y * -0.005}px)`,
            transition: "transform 0.3s ease-out",
            animationDelay: "1s",
          }}
        />
      </div>

      {/* Tab-specific animations */}
      <TabAnimations />
      
      {/* Header - Fixed */}
      <header className="fixed top-0 left-0 right-0 h-16 border-b border-border backdrop-blur-md bg-background/95 z-50">
        <div className="h-full px-6 flex items-center justify-between">
          <button
            onClick={() => navigate('/')}
            className="flex flex-col hover:opacity-80 transition-opacity cursor-pointer items-start"
          >
            <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              AI Studio
            </h1>
            <p className="text-xs text-muted-foreground">Text-to-Video Platform</p>
          </button>
        </div>
      </header>

      {/* Main Content Area - With top padding for fixed header */}
      <div className="flex-1 flex relative z-10 pt-16">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden ml-20">
          <main className="flex-1 overflow-auto relative">
            <Outlet />
          </main>
        </div>
      </div>

      {/* Connection Status Indicator - Fixed bottom right */}
      <ConnectionStatus />
    </div>
  );
};

export default Layout;
