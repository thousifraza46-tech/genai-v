import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Sparkles, Wand2, Video, ArrowRight, Play } from "lucide-react";
import { useEffect, useState } from "react";
import { FlipWords } from "@/components/ui/flip-words";
import backgroundImage from "@/assets/chat-background.jpg";

const HomePage = () => {
  const navigate = useNavigate();
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  const features = [
    {
      icon: Sparkles,
      title: "One Prompt â†’ Full Video Pipeline",
      description: "Generate complete videos from a single text prompt",
    },
    {
      icon: Wand2,
      title: "Built-in AI Assistant",
      description: "Intelligent script writing and creative guidance",
    },
    {
      icon: Video,
      title: "Custom Animation Tools",
      description: "Professional animations and effects at your fingertips",
    },
  ];

  return (
    <div className="min-h-screen w-full relative overflow-hidden bg-gradient-to-br from-background via-primary/5 to-accent/10">
      {/* Background Image with 60% opacity */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-60 pointer-events-none"
        style={{ backgroundImage: `url(${backgroundImage})` }}
      />
      
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Parallax Gradient Orbs */}
        <div
          className="absolute w-96 h-96 rounded-full bg-primary/20 blur-3xl animate-pulse-slow"
          style={{
            top: "10%",
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
            transform: `translate(${mousePosition.x * -0.001}px, ${mousePosition.y * -0.001}px)`,
            transition: "transform 0.5s ease-out",
            animationDelay: "1s",
          }}
        />
      </div>

      {/* Main Content */}
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Hero Section */}
        <div className="flex-1 flex items-start px-6 py-20 mt-20 relative">
          {/* 3D Floating Blob on Right Side */}
          <div className="hero-3d-blob">
          </div>
          <div className="hero-3d-blob-2"></div>
          
          <div className="ml-12 space-y-8 animate-fade-in">
            {/* Headline */}
            <div className="space-y-4">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight leading-tight">
                <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent animate-gradient bg-300%">
                  GenAI Text to Video
                </span>
                <br />
                <span className="text-foreground">Generation</span>
              </h1>
              
              <p className="text-lg md:text-xl text-muted-foreground max-w-2xl leading-relaxed">
                AI-powered script writing, voice narration, image generation, and final video creation — all in one place.
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row items-start gap-4">
              <button
                onClick={() => navigate("/app")}
                className="uiverse-button"
              >
                Get Started
              </button>
            </div>

            {/* Flip Words Section */}
            <div className="mt-8 text-center">
              <div className="text-2xl md:text-3xl font-semibold text-muted-foreground">
                <FlipWords
                  words={["Scripts", "Videos", "Animations", "Content", "Stories"]}
                  className="text-primary font-bold"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Feature Highlights */}
        <div className="pb-32 px-8 mt-32 relative">
          {/* 3D Floating Blob in Feature Section */}
          <div className="hero-3d-blob-3"></div>
          
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-28 justify-items-center">
              {features.map((feature, index) => {
                const Icon = feature.icon;
                return (
                  <div key={index} className="glass-container">
                    <div className="glass-box">
                      <div className="glass-icon-wrapper">
                        <Icon className="glass-icon" />
                      </div>
                      <div className="glass-content">
                        <strong className="glass-title">{feature.title}</strong>
                        <p className="glass-description">{feature.description}</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="py-8 border-t border-border/50 backdrop-blur-sm">
          <div className="max-w-6xl mx-auto px-6">
            <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-muted-foreground">
              <a href="#" className="hover:text-primary transition-colors">
                About
              </a>
              <span className="w-1 h-1 rounded-full bg-muted-foreground/30" />
              <a href="#" className="hover:text-primary transition-colors">
                Contact
              </a>
              <span className="w-1 h-1 rounded-full bg-muted-foreground/30" />
              <a href="#" className="hover:text-primary transition-colors">
                Terms
              </a>
              <span className="w-1 h-1 rounded-full bg-muted-foreground/30" />
              <a href="#" className="hover:text-primary transition-colors">
                Privacy
              </a>
            </div>
          </div>
        </footer>
      </div>

      <style>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0) translateX(0);
          }
          25% {
            transform: translateY(-20px) translateX(10px);
          }
          50% {
            transform: translateY(-10px) translateX(-10px);
          }
          75% {
            transform: translateY(-30px) translateX(5px);
          }
        }

        @keyframes pulse-slow {
          0%, 100% {
            opacity: 0.3;
            transform: scale(1);
          }
          50% {
            opacity: 0.5;
            transform: scale(1.1);
          }
        }

        @keyframes gradient {
          0% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
          100% {
            background-position: 0% 50%;
          }
        }

        @keyframes floatBlob {
          0% { 
            transform: translateY(0px) scale(1); 
            border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
          }
          25% {
            border-radius: 58% 42% 75% 25% / 76% 46% 54% 24%;
          }
          50% {
            border-radius: 50% 50% 33% 67% / 55% 27% 73% 45%;
          }
          75% {
            border-radius: 33% 67% 58% 42% / 63% 68% 32% 37%;
          }
          100% { 
            transform: translateY(-45px) scale(1.08); 
            border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
          }
        }

        @keyframes floatBlob2 {
          0% { 
            transform: translateY(0px) rotate(0deg) scale(1); 
            border-radius: 45% 55% 60% 40% / 55% 45% 55% 45%;
          }
          33% {
            border-radius: 70% 30% 50% 50% / 40% 60% 40% 60%;
          }
          66% {
            border-radius: 40% 60% 40% 60% / 50% 30% 70% 50%;
          }
          100% { 
            transform: translateY(-35px) rotate(15deg) scale(1.05); 
            border-radius: 45% 55% 60% 40% / 55% 45% 55% 45%;
          }
        }

        @keyframes floatBlob3 {
          0% { 
            transform: translateX(0px) translateY(0px) scale(1); 
            border-radius: 60% 40% 50% 50% / 45% 60% 40% 55%;
          }
          25% {
            border-radius: 50% 50% 60% 40% / 60% 50% 50% 40%;
          }
          50% {
            border-radius: 40% 60% 50% 50% / 50% 40% 60% 50%;
          }
          75% {
            border-radius: 55% 45% 45% 55% / 50% 55% 45% 50%;
          }
          100% { 
            transform: translateX(30px) translateY(-40px) scale(1.06); 
            border-radius: 60% 40% 50% 50% / 45% 60% 40% 55%;
          }
        }

        .animate-float {
          animation: float linear infinite;
        }

        .animate-pulse-slow {
          animation: pulse-slow 8s ease-in-out infinite;
        }

        .animate-gradient {
          animation: gradient 3s ease infinite;
        }

        .hero-3d-blob {
          position: absolute;
          right: 60px;
          top: 80px;
          width: 420px;
          height: 420px;
          background: radial-gradient(circle at 30% 30%, #9cb8ff, #6a73ff, #b06bff);
          border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
          filter: blur(2px) saturate(160%);
          opacity: 0.95;
          animation: floatBlob 30s ease-in-out infinite alternate;
          z-index: -1;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .hero-3d-blob-2 {
          position: absolute;
          left: 120px;
          bottom: 150px;
          width: 280px;
          height: 280px;
          background: radial-gradient(circle at 60% 40%, #ff9a9e, #fad0c4, #ffecd2);
          border-radius: 45% 55% 60% 40% / 55% 45% 55% 45%;
          filter: blur(2px) saturate(150%);
          opacity: 0.85;
          animation: floatBlob2 35s ease-in-out infinite alternate;
          z-index: -1;
        }

        .hero-3d-blob-3 {
          position: absolute;
          right: 100px;
          top: 50%;
          width: 350px;
          height: 350px;
          background: radial-gradient(circle at 40% 50%, #a8edea, #fed6e3, #d4fc79);
          border-radius: 60% 40% 50% 50% / 45% 60% 40% 55%;
          filter: blur(2px) saturate(140%);
          opacity: 0.8;
          animation: floatBlob3 40s ease-in-out infinite alternate;
          z-index: -1;
        }

        .bg-300\\% {
          background-size: 300% 300%;
        }

        /* Uiverse Button Styles */
        .uiverse-button {
          padding: 15px 25px;
          border: unset;
          border-radius: 15px;
          color: #212121;
          z-index: 1;
          background: #e8e8e8;
          position: relative;
          font-weight: 1000;
          font-size: 17px;
          -webkit-box-shadow: 4px 8px 19px -3px rgba(0,0,0,0.27);
          box-shadow: 4px 8px 19px -3px rgba(0,0,0,0.27);
          transition: all 250ms;
          overflow: hidden;
          cursor: pointer;
        }

        .uiverse-button::before {
          content: "";
          position: absolute;
          top: 0;
          left: 0;
          height: 100%;
          width: 0;
          border-radius: 15px;
          background-color: #212121;
          z-index: -1;
          -webkit-box-shadow: 4px 8px 19px -3px rgba(0,0,0,0.27);
          box-shadow: 4px 8px 19px -3px rgba(0,0,0,0.27);
          transition: all 250ms;
        }

        .uiverse-button:hover {
          color: #e8e8e8;
        }

        .uiverse-button:hover::before {
          width: 100%;
        }

        /* Glass Effect Feature Cards */
        .glass-container {
          color: white;
          position: relative;
          font-family: sans-serif;
        }

        .glass-container::before,
        .glass-container::after {
          content: "";
          background-color: #fab5704c;
          position: absolute;
        }

        .glass-container::before {
          border-radius: 50%;
          width: 6rem;
          height: 6rem;
          top: 30%;
          right: 7%;
        }

        .glass-container::after {
          content: "";
          position: absolute;
          height: 3rem;
          top: 8%;
          right: 5%;
          border: 1px solid;
        }

        .glass-container .glass-box {
          width: 18rem;
          height: 20rem;
          padding: 1.5rem;
          background-color: rgba(255, 255, 255, 0.25);
          border: 2px solid rgba(255, 255, 255, 0.6);
          -webkit-backdrop-filter: blur(15px);
          backdrop-filter: blur(15px);
          border-radius: 0.7rem;
          transition: all ease 0.3s;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        }

        .glass-icon-wrapper {
          display: flex;
          justify-content: center;
          align-items: center;
          margin-bottom: 1.5rem;
        }

        .glass-icon {
          width: 4rem;
          height: 4rem;
          color: #fab570;
          filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
        }

        .glass-content {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .glass-container .glass-box .glass-title {
          display: block;
          font-size: 1.3rem;
          font-weight: 600;
          letter-spacing: 0.05em;
          margin-bottom: 0.5rem;
          color: white;
          text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        .glass-container .glass-box .glass-description {
          margin: 0;
          font-size: 0.95rem;
          font-weight: 300;
          letter-spacing: 0.05em;
          line-height: 1.6;
          color: rgba(255, 255, 255, 0.95);
          text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        }

        .glass-container .glass-box:hover {
          box-shadow: 0px 0px 30px 3px #ffbb763f;
          border: 2px solid rgba(255, 255, 255, 0.8);
          background-color: rgba(255, 255, 255, 0.3);
        }
      `}</style>
    </div>
  );
};

export default HomePage;
