import { useLocation } from "react-router-dom";
import chatBackground from "@/assets/chat-background.jpg";
import videoBackground from "@/assets/video-background.jpg";
import animationBackground from "@/assets/animation-background.jpg";
import backgroundPattern from "@/assets/background-pattern.jpg";
import videoWaveBackground from "@/assets/video-background.jpg";
import aiWaveBackground from "@/assets/chat-background-copy.jpg";
import videoPatternBackground from "@/assets/background-pattern-copy.jpg";

const TabAnimations = () => {
  const location = useLocation();
  const currentPath = location.pathname;

  // Don't show animations on home page
  if (currentPath === '/') return null;

  if (currentPath === '/ai-assistance') {
    return (
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        {/* Background Image Layer - Light, Visible, Animated */}
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ 
            backgroundImage: `url(${aiWaveBackground})`,
            opacity: 0.5,
            filter: 'brightness(1.25) contrast(1.05) saturate(1.15)',
            zIndex: 1,
            animation: 'gentleZoom 30s ease-in-out infinite alternate, waveFloat 45s ease-in-out infinite'
          }}
        />
        {/* Swirling neural waves - big aura pulses */}
        {[...Array(4)].map((_, i) => (
          <div
            key={`aura-${i}`}
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full blur-3xl z-10"
            style={{
              width: `${200 + i * 150}px`,
              height: `${200 + i * 150}px`,
              background: `radial-gradient(circle, ${
                i % 2 === 0 ? 'rgba(59, 130, 246, 0.2)' : 'rgba(147, 51, 234, 0.2)'
              }, transparent 70%)`,
              animation: `neuralPulse ${4 + i * 2}s ease-in-out infinite`,
              animationDelay: `${i * 0.8}s`,
            }}
          />
        ))}

        {/* Soft electric arcs */}
        {[...Array(12)].map((_, i) => {
          const angle = (i * 360) / 12;
          return (
            <div
              key={`arc-${i}`}
              className="absolute top-1/2 left-1/2 origin-left"
              style={{
                width: '300px',
                height: '2px',
                transform: `rotate(${angle}deg)`,
                background: 'linear-gradient(to right, rgba(96, 165, 250, 0.4), transparent)',
                animation: `electricArc ${3 + (i % 3)}s ease-in-out infinite`,
                animationDelay: `${i * 0.2}s`,
                filter: 'blur(2px)',
              }}
            />
          );
        })}

        {/* Floating transparent energy rings */}
        {[...Array(6)].map((_, i) => (
          <div
            key={`ring-${i}`}
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 border-2 rounded-full"
            style={{
              width: `${150 + i * 100}px`,
              height: `${150 + i * 100}px`,
              borderColor: i % 2 === 0 ? 'rgba(59, 130, 246, 0.15)' : 'rgba(147, 51, 234, 0.15)',
              animation: `energyRing ${8 + i * 2}s linear infinite`,
              animationDelay: `${i * 1}s`,
            }}
          />
        ))}



        {/* Animation keyframes for AI Assistance */}
        <style>{`
          @keyframes gentleZoom {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
          }
          @keyframes waveFloat {
            0%, 100% { background-position: center center; }
            25% { background-position: 53% 47%; }
            50% { background-position: 47% 53%; }
            75% { background-position: 53% 53%; }
          }
          @keyframes neuralPulse {
            0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.3; }
            50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.6; }
          }
          @keyframes electricArc {
            0%, 100% { opacity: 0.2; width: 300px; }
            50% { opacity: 0.6; width: 350px; }
          }
          @keyframes energyRing {
            0% { transform: translate(-50%, -50%) scale(0.9) rotate(0deg); opacity: 0.3; }
            50% { transform: translate(-50%, -50%) scale(1.1) rotate(180deg); opacity: 0.2; }
            100% { transform: translate(-50%, -50%) scale(0.9) rotate(360deg); opacity: 0.3; }
          }
          @keyframes neuralOrbit {
            0% { transform: rotate(0deg) translateX(var(--radius, 180px)); }
            100% { transform: rotate(360deg) translateX(var(--radius, 180px)); }
          }
        `}</style>
      </div>
    );
  }

  // 2. Generate Video - "Hyperdrive Light Tunnel"
  if (currentPath === '/generate-video') {
    return (
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        {/* Background Wave Layer - Light Animated Aesthetic */}
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ 
            backgroundImage: `url(${videoWaveBackground})`,
            opacity: 0.15,
            filter: 'brightness(1.3) contrast(1.05) saturate(1.1)',
            animation: 'videoWaveFlow 35s ease-in-out infinite alternate, videoZoom 40s ease-in-out infinite',
            zIndex: 1
          }}
        />
        {/* Fast moving diagonal light streaks */}
        {[...Array(30)].map((_, i) => {
          const delay = i * 0.15;
          const duration = 2 + (i % 3) * 0.5;
          return (
            <div
              key={`streak-${i}`}
              className="absolute w-2 h-64 blur-sm"
              style={{
                left: `${(i * 3.5) % 100}%`,
                top: '-10%',
                background: `linear-gradient(to bottom, transparent, ${
                  i % 4 === 0 ? 'rgba(34, 197, 94, 0.4)' :
                  i % 4 === 1 ? 'rgba(16, 185, 129, 0.4)' :
                  i % 4 === 2 ? 'rgba(52, 211, 153, 0.4)' :
                  'rgba(110, 231, 183, 0.4)'
                }, transparent)`,
                transform: 'rotate(-20deg)',
                animation: `hyperStreakDown ${duration}s linear infinite`,
                animationDelay: `${delay}s`,
              }}
            />
          );
        })}

        {/* Faint warped tunnel effect */}
        {[...Array(8)].map((_, i) => (
          <div
            key={`tunnel-${i}`}
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 border border-green-400/10 rounded-full"
            style={{
              width: `${100 + i * 120}px`,
              height: `${80 + i * 96}px`,
              animation: `tunnelExpand ${3 + i * 0.3}s ease-out infinite`,
              animationDelay: `${i * 0.3}s`,
            }}
          />
        ))}

        {/* Glowing scan-line pulses */}
        {[...Array(5)].map((_, i) => (
          <div
            key={`scanline-${i}`}
            className="absolute w-full h-1 blur-md"
            style={{
              background: 'linear-gradient(to right, transparent, rgba(34, 197, 94, 0.6), transparent)',
              animation: `scanPulse ${4 + i}s linear infinite`,
              animationDelay: `${i * 0.8}s`,
            }}
          />
        ))}



        <style>{`
          @keyframes videoWaveFlow {
            0%, 100% { background-position: center center; }
            25% { background-position: 55% 45%; }
            50% { background-position: 45% 55%; }
            75% { background-position: 55% 55%; }
          }
          @keyframes videoZoom {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.08); }
          }
          @keyframes hyperStreakDown {
            0% { transform: translateY(0) rotate(-20deg); opacity: 0; }
            10% { opacity: 0.6; }
            90% { opacity: 0.6; }
            100% { transform: translateY(120vh) rotate(-20deg); opacity: 0; }
          }
          @keyframes tunnelExpand {
            0% { transform: translate(-50%, -50%) scale(0.5); opacity: 0.15; }
            100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
          }
          @keyframes scanPulse {
            0% { top: -10%; opacity: 0; }
            50% { opacity: 0.8; }
            100% { top: 110%; opacity: 0; }
          }
          @keyframes hyperMotion {
            0% { transform: translate(0, 0); opacity: 0; }
            10% { opacity: 0.8; }
            90% { opacity: 0.8; }
            100% { transform: translate(-50px, 80vh); opacity: 0; }
          }
        `}</style>
      </div>
    );
  }

  // 3. Animation - "Hologram Ripple Matrix"
  if (currentPath === '/animation') {
    return (
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        {/* Background Image Layer */}
        <div 
          className="absolute inset-0 opacity-30 bg-cover bg-center"
          style={{ 
            backgroundImage: `url(${animationBackground})`
          }}
        />
        {/* 3D holographic ripple waves */}
        {[...Array(6)].map((_, i) => (
          <div
            key={`ripple-${i}`}
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 border-2 rounded-full"
            style={{
              width: `${150 + i * 120}px`,
              height: `${100 + i * 80}px`,
              borderColor: `rgba(168, 85, 247, ${0.3 - i * 0.04})`,
              animation: `hologramRipple ${4 + i * 0.8}s ease-out infinite`,
              animationDelay: `${i * 0.5}s`,
              transform: `translate(-50%, -50%) perspective(800px) rotateX(${20 + i * 5}deg)`,
            }}
          />
        ))}

        {/* Transparent grid distortion */}
        {[...Array(8)].map((_, i) => (
          <div
            key={`h-grid-${i}`}
            className="absolute w-full h-px bg-gradient-to-r from-transparent via-purple-400/15 to-transparent"
            style={{
              top: `${12 + i * 11}%`,
              animation: `gridWave ${5 + i * 0.5}s ease-in-out infinite`,
              animationDelay: `${i * 0.3}s`,
            }}
          />
        ))}
        {[...Array(8)].map((_, i) => (
          <div
            key={`v-grid-${i}`}
            className="absolute h-full w-px bg-gradient-to-b from-transparent via-purple-400/15 to-transparent"
            style={{
              left: `${12 + i * 11}%`,
              animation: `gridWave ${5 + i * 0.5}s ease-in-out infinite`,
              animationDelay: `${i * 0.3 + 0.5}s`,
            }}
          />
        ))}

        {/* Floating polygons */}
        {[...Array(12)].map((_, i) => {
          const size = 40 + (i % 4) * 20;
          return (
            <div
              key={`poly-${i}`}
              className="absolute border border-purple-400/25"
              style={{
                width: `${size}px`,
                height: `${size}px`,
                left: `${10 + (i * 8) % 80}%`,
                top: `${15 + (i * 7) % 70}%`,
                clipPath: i % 3 === 0 ? 'polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)' :
                         i % 3 === 1 ? 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)' :
                         'polygon(50% 0%, 90% 20%, 100% 60%, 75% 100%, 25% 100%, 0% 60%, 10% 20%)',
                animation: `polyFloat ${8 + i * 2}s ease-in-out infinite`,
                animationDelay: `${i * 0.6}s`,
              }}
            />
          );
        })}



        <style>{`
          @keyframes hologramRipple {
            0% { transform: translate(-50%, -50%) perspective(800px) rotateX(20deg) scale(0.5); opacity: 0.4; }
            100% { transform: translate(-50%, -50%) perspective(800px) rotateX(35deg) scale(1.5); opacity: 0; }
          }
          @keyframes gridWave {
            0%, 100% { transform: scaleX(1) translateY(0); opacity: 0.15; }
            50% { transform: scaleX(1.05) translateY(5px); opacity: 0.3; }
          }
          @keyframes polyFloat {
            0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.25; }
            50% { transform: translateY(-30px) rotate(180deg); opacity: 0.4; }
          }
          @keyframes shimmer {
            0%, 100% { opacity: 0.2; transform: scale(1); }
            50% { opacity: 0.6; transform: scale(1.3); }
          }
        `}</style>
      </div>
    );
  }

  // 4. History - "Digital Time Drift"
  if (currentPath === '/history') {
    return (
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        {/* Background Image Layer */}
        <div 
          className="absolute inset-0 opacity-25 bg-cover bg-center"
          style={{ 
            backgroundImage: `url(${backgroundPattern})`,
            mixBlendMode: 'overlay'
          }}
        />
        {/* Slow-moving timeline beams */}
        {[...Array(6)].map((_, i) => (
          <div
            key={`timeline-${i}`}
            className="absolute h-full w-1 blur-sm"
            style={{
              left: `${15 + i * 14}%`,
              background: 'linear-gradient(to bottom, transparent, rgba(251, 146, 60, 0.2), rgba(251, 146, 60, 0.3), rgba(251, 146, 60, 0.2), transparent)',
              animation: `timelineDrift ${12 + i * 3}s ease-in-out infinite`,
              animationDelay: `${i * 1.5}s`,
            }}
          />
        ))}

        {/* Big translucent numbers */}
        {[...Array(8)].map((_, i) => {
          const numbers = ['2024', '2023', '2022', '2021', '2020', '2019', '2018', '2017'];
          return (
            <div
              key={`number-${i}`}
              className="absolute text-8xl font-bold blur-sm select-none"
              style={{
                left: `${(i * 13) % 85}%`,
                top: `${(i * 17) % 75}%`,
                color: 'rgba(251, 146, 60, 0.08)',
                animation: `numberFade ${10 + i * 2}s ease-in-out infinite`,
                animationDelay: `${i * 1.2}s`,
              }}
            >
              {numbers[i % numbers.length]}
            </div>
          );
        })}



        {/* Occasional glitch flickers */}
        {[...Array(10)].map((_, i) => (
          <div
            key={`glitch-${i}`}
            className="absolute w-32 h-16 border border-orange-400/20"
            style={{
              left: `${(i * 11) % 90}%`,
              top: `${(i * 13) % 80}%`,
              animation: `glitchFlicker ${8 + i * 2}s ease-in-out infinite`,
              animationDelay: `${i * 1.5}s`,
            }}
          />
        ))}

        <style>{`
          @keyframes timelineDrift {
            0%, 100% { transform: translateY(-10px); opacity: 0.2; }
            50% { transform: translateY(10px); opacity: 0.4; }
          }
          @keyframes numberFade {
            0%, 80%, 100% { opacity: 0; transform: scale(1); }
            10%, 70% { opacity: 0.12; transform: scale(1.1); }
          }
          @keyframes pixelDrift {
            0%, 100% { transform: translate(0, 0); opacity: 0.15; }
            50% { transform: translate(20px, -30px); opacity: 0.35; }
          }
          @keyframes glitchFlicker {
            0%, 90%, 100% { opacity: 0; }
            92%, 96% { opacity: 0.3; }
            94% { opacity: 0; }
          }
        `}</style>
      </div>
    );
  }

  // 5. Personalization - "Color Morph Aurora Field"
  if (currentPath === '/personalization') {
    return (
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        {/* Background Image Layer */}
        <div 
          className="absolute inset-0 opacity-35 bg-cover bg-center"
          style={{ 
            backgroundImage: `url(${chatBackground})`
          }}
        />
        {/* Transparent aurora ribbons */}
        {[...Array(5)].map((_, i) => (
          <div
            key={`aurora-${i}`}
            className="absolute w-full h-32 blur-3xl"
            style={{
              top: `${10 + i * 18}%`,
              background: `linear-gradient(to right, 
                transparent,
                ${i % 5 === 0 ? 'rgba(236, 72, 153, 0.15)' :
                  i % 5 === 1 ? 'rgba(147, 51, 234, 0.15)' :
                  i % 5 === 2 ? 'rgba(59, 130, 246, 0.15)' :
                  i % 5 === 3 ? 'rgba(168, 85, 247, 0.15)' :
                  'rgba(139, 92, 246, 0.15)'},
                transparent
              )`,
              animation: `auroraFlow ${12 + i * 3}s ease-in-out infinite`,
              animationDelay: `${i * 1.8}s`,
            }}
          />
        ))}

        {/* Smooth color-flow motion waves */}
        {[...Array(6)].map((_, i) => (
          <div
            key={`flow-${i}`}
            className="absolute rounded-full blur-2xl"
            style={{
              width: `${250 + i * 100}px`,
              height: `${180 + i * 60}px`,
              left: `${(i * 18) % 85}%`,
              top: `${(i * 15) % 70}%`,
              background: `radial-gradient(ellipse, ${
                i % 4 === 0 ? 'rgba(236, 72, 153, 0.12)' :
                i % 4 === 1 ? 'rgba(147, 51, 234, 0.12)' :
                i % 4 === 2 ? 'rgba(59, 130, 246, 0.12)' :
                'rgba(34, 211, 238, 0.12)'
              }, transparent 70%)`,
              animation: `colorMorph ${15 + i * 3}s ease-in-out infinite`,
              animationDelay: `${i * 2}s`,
            }}
          />
        ))}

        {/* Light swaying glow trails */}
        {[...Array(12)].map((_, i) => (
          <div
            key={`trail-${i}`}
            className="absolute h-1 rounded-full blur-md"
            style={{
              width: `${120 + (i % 4) * 40}px`,
              left: `${(i * 8) % 90}%`,
              top: `${10 + i * 7}%`,
              background: `linear-gradient(to right, transparent, ${
                i % 4 === 0 ? 'rgba(236, 72, 153, 0.4)' :
                i % 4 === 1 ? 'rgba(147, 51, 234, 0.4)' :
                i % 4 === 2 ? 'rgba(59, 130, 246, 0.4)' :
                'rgba(34, 211, 238, 0.4)'
              }, transparent)`,
              animation: `trailSway ${8 + i * 2}s ease-in-out infinite`,
              animationDelay: `${i * 0.8}s`,
            }}
          />
        ))}



        <style>{`
          @keyframes auroraFlow {
            0%, 100% { transform: translateX(-50px) scaleY(1); opacity: 0.15; }
            50% { transform: translateX(50px) scaleY(1.2); opacity: 0.25; }
          }
          @keyframes colorMorph {
            0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.15; }
            50% { transform: translate(30px, -20px) scale(1.2); opacity: 0.25; }
          }
          @keyframes trailSway {
            0%, 100% { transform: translateX(0) translateY(0); opacity: 0.25; }
            50% { transform: translateX(40px) translateY(-15px); opacity: 0.45; }
          }
          @keyframes morphFloat {
            0%, 100% { transform: translate(0, 0); opacity: 0.2; }
            33% { transform: translate(20px, -25px); opacity: 0.4; }
            66% { transform: translate(-15px, 15px); opacity: 0.3; }
          }
        `}</style>
      </div>
    );
  }

  // 6. Settings - "Cyber Matrix Grid Pulse"
  if (currentPath === '/settings') {
    return (
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        {/* Background Image Layer */}
        <div 
          className="absolute inset-0 opacity-25 bg-cover bg-center"
          style={{ 
            backgroundImage: `url(${backgroundPattern})`,
            mixBlendMode: 'overlay'
          }}
        />
        {/* Pulsing hex/dot matrix */}
        {[...Array(120)].map((_, i) => {
          const row = Math.floor(i / 12);
          const col = i % 12;
          return (
            <div
              key={`hex-${i}`}
              className="absolute border border-cyan-400/20"
              style={{
                width: '32px',
                height: '32px',
                left: `${4 + col * 8}%`,
                top: `${5 + row * 9}%`,
                clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)',
                animation: `hexPulse ${3 + (i % 6) * 0.5}s ease-in-out infinite`,
                animationDelay: `${(col * 0.1 + row * 0.15) % 3}s`,
              }}
            />
          );
        })}



        {/* Slow moving diagnostics lines */}
        {[...Array(8)].map((_, i) => (
          <div
            key={`diag-${i}`}
            className="absolute w-full h-px bg-gradient-to-r from-transparent via-cyan-400/25 to-transparent blur-sm"
            style={{
              top: `${10 + i * 11}%`,
              animation: `diagFlow ${10 + i * 2}s linear infinite`,
              animationDelay: `${i * 1.2}s`,
            }}
          />
        ))}

        {/* Transparent techno grid overlay */}
        <div className="absolute inset-0" style={{
          backgroundImage: `
            linear-gradient(to right, rgba(34, 211, 238, 0.03) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(34, 211, 238, 0.03) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
          animation: 'gridPulse 8s ease-in-out infinite',
        }} />

        {/* Corner brackets */}
        {[...Array(4)].map((_, i) => (
          <div
            key={`bracket-${i}`}
            className="absolute w-16 h-16 border-2"
            style={{
              left: i % 2 === 0 ? '5%' : 'auto',
              right: i % 2 === 1 ? '5%' : 'auto',
              top: i < 2 ? '5%' : 'auto',
              bottom: i >= 2 ? '5%' : 'auto',
              borderTop: i < 2 ? '2px solid rgba(34, 211, 238, 0.3)' : 'none',
              borderBottom: i >= 2 ? '2px solid rgba(34, 211, 238, 0.3)' : 'none',
              borderLeft: i % 2 === 0 ? '2px solid rgba(34, 211, 238, 0.3)' : 'none',
              borderRight: i % 2 === 1 ? '2px solid rgba(34, 211, 238, 0.3)' : 'none',
              animation: `bracketGlow ${4 + i}s ease-in-out infinite`,
              animationDelay: `${i * 0.5}s`,
            }}
          />
        ))}

        <style>{`
          @keyframes hexPulse {
            0%, 100% { opacity: 0.15; transform: scale(1); }
            50% { opacity: 0.35; transform: scale(1.05); }
          }
          @keyframes systemBlink {
            0%, 80%, 100% { opacity: 0.2; }
            40% { opacity: 0.8; }
          }
          @keyframes diagFlow {
            0% { transform: translateX(-100%); opacity: 0; }
            50% { opacity: 0.4; }
            100% { transform: translateX(100%); opacity: 0; }
          }
          @keyframes gridPulse {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 0.8; }
          }
          @keyframes bracketGlow {
            0%, 100% { opacity: 0.25; }
            50% { opacity: 0.5; }
          }
        `}</style>
      </div>
    );
  }

  return null;
};

export default TabAnimations;
