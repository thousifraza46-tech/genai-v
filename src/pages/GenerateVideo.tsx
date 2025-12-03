import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { 
  Mic, 
  Sparkles, 
  FileText, 
  Volume2, 
  Image as ImageIcon, 
  Video, 
  Download, 
  Play,
  Plus,
  CheckCircle2,
  Loader2,
  ChevronDown,
  ChevronUp,
  Wifi,
  WifiOff,
  RefreshCw
} from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { useEditorStore } from "@/store/editorStore";
import { useToast } from "@/hooks/use-toast";
import { apiKeysService } from "@/services/apiKeysService";
import { API_CONFIG, getApiUrl, getAssetsUrl } from "@/config/api";

type StageStatus = "pending" | "generating" | "completed" | "error";

interface GeneratedImage {
  id: number;
  sceneNumber: number;
  url: string;
  description: string;
}

// Example prompts organized by category
const EXAMPLE_PROMPTS = {
  "Nature & Landscapes": [
    "Ocean sunset with golden rays reflecting on calm waves",
    "Mountain peak at sunrise with misty valleys and snow-capped peaks",
    "Forest path with sunlight filtering through tall trees",
    "Tropical beach with turquoise water and palm trees",
    "Desert landscape with sand dunes at golden hour",
  ],
  "Urban & Architecture": [
    "Bustling city street at night with neon lights and traffic",
    "Tokyo street at night with colorful billboards and neon signs",
    "Ancient ruins at sunset with marble columns",
    "Modern glass buildings reflecting clouds",
    "European old town with cobblestone streets and cafes",
  ],
  "Wildlife & Animals": [
    "African savanna at golden hour with elephants",
    "Underwater coral reef with tropical fish",
    "Eagle soaring through sky with mountains",
    "Garden with colorful flowers and butterflies",
    "Polar bears walking on Arctic ice floes",
  ],
  "Technology & Business": [
    "Modern office with people working on computers",
    "Professional video conference meeting",
    "Young startup team collaborating in open office",
    "Person analyzing data on multiple screens",
    "Data center with rows of servers and blue lights",
  ],
  "Food & Cuisine": [
    "Fresh sushi platter with nigiri and rolls",
    "Chef tossing pizza dough in Italian pizzeria",
    "Vibrant farmers market with fresh produce",
    "Beautiful dessert table with cakes and pastries",
    "Barista pouring latte art in coffee",
  ],
};

const GenerateVideo = () => {
  // API Configuration
  const API_BASE_URL = API_CONFIG.baseURL;
  
  // Editor store integration
  const { addClip, clips } = useEditorStore();
  const { toast } = useToast();
  
  // Backend connection state
  const [backendConnected, setBackendConnected] = useState(false);
  const [checkingConnection, setCheckingConnection] = useState(false);
  
  // Core state
  const [prompt, setPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [showExamples, setShowExamples] = useState(false);
  
  // Stage states
  const [scriptStatus, setScriptStatus] = useState<StageStatus>("pending");
  const [scriptContent, setScriptContent] = useState("");
  const [generatedScript, setGeneratedScript] = useState(""); // Store generated script for image search
  const [scriptProgress, setScriptProgress] = useState(0);
  
  const [audioStatus, setAudioStatus] = useState<StageStatus>("pending");
  const [audioUrl, setAudioUrl] = useState("");
  const [audioProgress, setAudioProgress] = useState(0);
  
  const [imagesStatus, setImagesStatus] = useState<StageStatus>("pending");
  const [generatedImages, setGeneratedImages] = useState<GeneratedImage[]>([]);
  const [imagesProgress, setImagesProgress] = useState(0);
  
  const [videoStatus, setVideoStatus] = useState<StageStatus>("pending");
  const [videoUrl, setVideoUrl] = useState("");
  const [videoProgress, setVideoProgress] = useState(0);
  const [generatedVideos, setGeneratedVideos] = useState<any[]>([]);
  const [selectedVideo, setSelectedVideo] = useState<any>(null);
  
  // Image-to-video conversion state
  const [convertingImages, setConvertingImages] = useState<Set<number>>(new Set());
  const [animatedVideos, setAnimatedVideos] = useState<Array<{imageId: number, videoUrl: string, sceneNumber: number}>>([]);
  
  // Fullscreen image viewer state
  const [fullscreenImage, setFullscreenImage] = useState<string | null>(null);
  
  // Voice recognition state
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState<any>(null);

  // Check backend connection on mount and every 30 seconds
  useEffect(() => {
    checkBackendConnection();
    const interval = setInterval(checkBackendConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  // Check backend connection
  const checkBackendConnection = async () => {
    setCheckingConnection(true);
    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (response.ok) {
        setBackendConnected(true);
        console.log('[Backend] ✅ Connected successfully');
      } else {
        throw new Error('Backend not responding');
      }
    } catch (error) {
      console.error('[Backend] ❌ Connection failed:', error);
      setBackendConnected(false);
    } finally {
      setCheckingConnection(false);
    }
  };

  // Load saved state from localStorage on mount
  useEffect(() => {
    const savedState = localStorage.getItem('generateVideoState');
    if (savedState) {
      try {
        const parsed = JSON.parse(savedState);
        setPrompt(parsed.prompt || "");
        setScriptStatus(parsed.scriptStatus || "pending");
        setScriptContent(parsed.scriptContent || "");
        setGeneratedScript(parsed.generatedScript || "");
        setScriptProgress(parsed.scriptProgress || 0);
        setAudioStatus(parsed.audioStatus || "pending");
        setAudioUrl(parsed.audioUrl || "");
        setAudioProgress(parsed.audioProgress || 0);
        setImagesStatus(parsed.imagesStatus || "pending");
        setGeneratedImages(parsed.generatedImages || []);
        setImagesProgress(parsed.imagesProgress || 0);
        setVideoStatus(parsed.videoStatus || "pending");
        setVideoUrl(parsed.videoUrl || "");
        setVideoProgress(parsed.videoProgress || 0);
        setGeneratedVideos(parsed.generatedVideos || []);
        setSelectedVideo(parsed.selectedVideo || null);
      } catch (error) {
        console.error('Error loading saved state:', error);
      }
    }
  }, []);

  // Save state to localStorage whenever it changes
  useEffect(() => {
    const stateToSave = {
      prompt,
      scriptStatus,
      scriptContent,
      generatedScript,
      scriptProgress,
      audioStatus,
      audioUrl,
      audioProgress,
      imagesStatus,
      generatedImages,
      imagesProgress,
      videoStatus,
      videoUrl,
      videoProgress,
      generatedVideos,
      selectedVideo
    };
    localStorage.setItem('generateVideoState', JSON.stringify(stateToSave));
  }, [prompt, scriptStatus, scriptContent, generatedScript, scriptProgress, audioStatus, audioUrl, audioProgress, imagesStatus, generatedImages, imagesProgress, videoStatus, videoUrl, videoProgress, generatedVideos, selectedVideo]);
  
  // Initialize speech recognition
  useState(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = false;
      recognitionInstance.lang = 'en-US';
      
      recognitionInstance.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setPrompt(prev => prev ? prev + ' ' + transcript : transcript);
        setIsListening(false);
      };
      
      recognitionInstance.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
      
      recognitionInstance.onend = () => {
        setIsListening(false);
      };
      
      setRecognition(recognitionInstance);
    }
  });
  
  const toggleVoiceInput = () => {
    if (!recognition) {
      alert('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
      return;
    }
    
    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      recognition.start();
      setIsListening(true);
    }
  };

  // Convert generated image to animated video
  const convertImageToVideo = async (image: GeneratedImage) => {
    // Check if already converting
    if (convertingImages.has(image.id)) return;
    
    // Add to converting set
    setConvertingImages(prev => new Set(prev).add(image.id));
    
    toast({
      title: "Creating Animation",
      description: `Converting Scene ${image.sceneNumber} to animated video...`,
    });
    
    try {
      // Send image URL to image-to-video endpoint
      const response = await fetch(`${API_BASE_URL}/huggingface/image-to-video`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_url: image.url,
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to convert image to video');
      }
      
      const data = await response.json();
      
      if (data.video_url) {
        // Add to animated videos
        setAnimatedVideos(prev => [...prev, {
          imageId: image.id,
          videoUrl: `${API_BASE_URL.replace('/api', '')}${data.video_url}`,
          sceneNumber: image.sceneNumber,
        }]);
        
        toast({
          title: "Animation Complete!",
          description: `Scene ${image.sceneNumber} animated successfully (5-second video)`,
        });
      } else {
        throw new Error('No video URL in response');
      }
      
    } catch (error) {
      console.error('Image-to-video conversion error:', error);
      toast({
        title: "Animation Failed",
        description: error instanceof Error ? error.message : "Failed to convert image to video",
        variant: "destructive",
      });
    } finally {
      // Remove from converting set
      setConvertingImages(prev => {
        const newSet = new Set(prev);
        newSet.delete(image.id);
        return newSet;
      });
    }
  };

  // Generate complete video pipeline
  const handleGenerate = async () => {
    if (!prompt.trim() || isGenerating) return;
    
    // Check backend connection first
    if (!backendConnected) {
      toast({
        title: "Backend Disconnected",
        description: "Checking connection...",
      });
      await checkBackendConnection();
      if (!backendConnected) {
        toast({
          title: "Cannot Generate",
          description: "Backend is not connected. Please ensure the server is running on port 5000.",
          variant: "destructive",
        });
        return;
      }
    }
    
    setIsGenerating(true);
    resetAllStages();
    
    try {
      // Stage 1: Script Generation
      const script = await generateScript();
      
      // Stage 2: Audio Generation (pass script directly)
      await generateAudio(script);
      
      // Stage 3: Image Generation (pass script directly)
      await generateImages(script);
      
      // Stage 4: Video Rendering
      await renderVideo();
      
    } catch (error) {
      console.error("Generation error:", error);
      toast({
        title: "Generation Error",
        description: error instanceof Error ? error.message : "An error occurred during generation",
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const resetAllStages = () => {
    setScriptStatus("pending");
    setScriptContent("");
    setGeneratedScript("");
    setScriptProgress(0);
    
    setAudioStatus("pending");
    setAudioUrl("");
    setAudioProgress(0);
    
    setImagesStatus("pending");
    setGeneratedImages([]);
    setImagesProgress(0);
    
    setVideoStatus("pending");
    setVideoUrl("");
    setVideoProgress(0);
  };

  const generateScript = (): Promise<string> => {
    return new Promise(async (resolve, reject) => {
      setScriptStatus("generating");
      setScriptProgress(0);
      
      try {
        console.log('[Script] Starting script generation for:', prompt);
        console.log('[Script] API URL:', `${API_BASE_URL}/generate/script`);
        
        // Simulate progress
        const progressInterval = setInterval(() => {
          setScriptProgress((prev) => Math.min(prev + 15, 90));
        }, 400);
        
        const response = await fetch(`${API_BASE_URL}/generate/script`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            prompt: prompt,
            duration: 30,
          }),
        });
        
        clearInterval(progressInterval);
        
        console.log('[Script] Response status:', response.status);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('[Script] API error:', response.status, errorText);
          throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('[Script] Success! Word count:', data.word_count);
        
        setScriptProgress(100);
        setTimeout(() => {
          setScriptStatus("completed");
          setGeneratedScript(data.script); // Store in state for images
          setScriptContent(data.script);
          resolve(data.script); // Return the script
        }, 300);
        
      } catch (error) {
        console.error("[Script] Generation failed:", error);
        setScriptStatus("error");
        // Use fallback script
        const fallback = getFallbackScript();
        setScriptContent(fallback);
        setGeneratedScript(fallback);
        setTimeout(() => resolve(fallback), 500);
      }
    });
  };

  const generateAudio = (script: string): Promise<void> => {
    return new Promise(async (resolve, reject) => {
      setAudioStatus("generating");
      setAudioProgress(0);
      
      try {
        console.log('[Audio] Starting audio generation');
        console.log('[Audio] Script length:', script.length, 'characters');
        console.log('[Audio] API URL:', `${API_BASE_URL}/generate/audio`);
        
        const progressInterval = setInterval(() => {
          setAudioProgress((prev) => Math.min(prev + 12, 90));
        }, 450);
        
        const response = await fetch(`${API_BASE_URL}/generate/audio`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            script: script,
          }),
        });
        
        clearInterval(progressInterval);
        
        console.log('[Audio] Response status:', response.status);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('[Audio] API error:', response.status, errorText);
          throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('[Audio] Success! Duration:', data.duration, 'seconds');
        console.log('[Audio] Audio path:', data.audio_path);
        console.log('[Audio] Audio URL:', data.audio_url);
        
        setAudioProgress(100);
        setTimeout(() => {
          setAudioStatus("completed");
          // Use backend URL if audio_path is provided
          if (data.audio_path) {
            const filename = data.audio_path.split(/[\\/]/).pop();
            const audioPath = `${API_BASE_URL.replace('/api', '')}/assets/audio/${filename}`;
            console.log('[Audio] Final Audio URL:', audioPath);
            setAudioUrl(audioPath);
          } else if (data.audio_url) {
            const audioPath = `${API_BASE_URL.replace('/api', '')}${data.audio_url}`;
            console.log('[Audio] Final Audio URL:', audioPath);
            setAudioUrl(audioPath);
          }
          resolve();
        }, 300);
        
      } catch (error) {
        console.error("[Audio] Generation failed:", error);
        setAudioStatus("error");
        setAudioUrl("fallback-audio.mp3");
        setTimeout(resolve, 500);
      }
    });
  };

  const generateImages = (script: string): Promise<void> => {
    return new Promise(async (resolve, reject) => {
      setImagesStatus("generating");
      setImagesProgress(0);
      
      try {
        // Use the generated script for better image matching
        const searchPrompt = script || prompt;
        console.log('[Images] Starting image generation');
        console.log('[Images] Using prompt/script:', searchPrompt.substring(0, 100) + '...');
        console.log('[Images] API URL:', `${API_BASE_URL}/generate/images`);
        
        const progressInterval = setInterval(() => {
          setImagesProgress((prev) => Math.min(prev + 8, 90));
        }, 500);
        
        const response = await fetch(`${API_BASE_URL}/generate/images`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            prompt: prompt,
            script: script,  // Send script for better context matching
            count: 3,
          }),
        });
        
        clearInterval(progressInterval);
        
        console.log('[Images] Response status:', response.status);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('[Images] API error:', response.status, errorText);
          throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('[Images] Success! Found', data.count, 'images');
        
        setImagesProgress(100);
        setTimeout(() => {
          setImagesStatus("completed");
          // Backend returns images array with proper structure
          if (data.images && data.images.length > 0) {
            console.log('[Images] Successfully loaded', data.images.length, 'images');
            data.images.forEach((img: any, idx: number) => {
              console.log(`  Image ${idx + 1}: ID=${img.id}, ${img.width}x${img.height}`);
            });
            setGeneratedImages(data.images);
          } else {
            console.warn('[Images] No images returned, using fallback');
            // Use fallback if no images returned
            setGeneratedImages(getFallbackImages());
          }
          resolve();
        }, 300);
        
      } catch (error) {
        console.error("[Images] Generation failed:", error);
        setImagesStatus("error");
        // Use fallback images
        console.warn('[Images] Using fallback images due to error');
        setGeneratedImages(getFallbackImages());
        setTimeout(resolve, 500);
      }
    });
  };

  const renderVideo = (): Promise<void> => {
    return new Promise(async (resolve, reject) => {
      setVideoStatus("generating");
      setVideoProgress(0);
      
      try {
        console.log('[Videos] Starting video search');
        console.log('[Videos] Prompt:', prompt);
        console.log('[Videos] API URL:', `${API_BASE_URL}/generate/videos`);
        
        const progressInterval = setInterval(() => {
          setVideoProgress((prev) => Math.min(prev + 10, 90));
        }, 450);
        
        // Fetch videos with script context for better matching
        const response = await fetch(`${API_BASE_URL}/generate/videos`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            prompt: prompt,
            script: generatedScript,  // Send script for better context matching
            count: 10,
          }),
        });
        
        clearInterval(progressInterval);
        
        console.log('[Videos] Response status:', response.status);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('[Videos] API error:', response.status, errorText);
          throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('[Videos] Success! Found', data.count, 'videos');
        
        setVideoProgress(100);
        setTimeout(() => {
          setVideoStatus("completed");
          if (data.videos && data.videos.length > 0) {
            console.log('[Videos] Successfully loaded', data.videos.length, 'videos');
            data.videos.slice(0, 3).forEach((vid: any, idx: number) => {
              console.log(`  Video ${idx + 1}: ID=${vid.id}, Duration=${vid.duration}s, ${vid.width}x${vid.height}`);
            });
            setGeneratedVideos(data.videos);
            setSelectedVideo(data.videos[0]); // Select first video by default
          } else {
            console.warn('[Videos] No videos returned from API, using fallback');
            setGeneratedVideos([]);
            setSelectedVideo(null);
          }
          resolve();
        }, 300);
        
      } catch (error) {
        console.error("Video fetching failed:", error);
        setVideoStatus("error");
        setGeneratedVideos([]);
        setSelectedVideo(null);
        setTimeout(resolve, 500);
      }
    });
  };

  const getFallbackScript = () => {
    return `**Scene 1 (0-10s): Opening**
Visual: Wide establishing shot introducing the concept
Narration: "Welcome to an exploration of ${prompt}"
Mood: Engaging, inviting

**Scene 2 (10-20s): Development**
Visual: Dynamic shots showcasing key elements
Narration: "Discover the fascinating details and unique aspects"
Mood: Informative, inspiring

**Scene 3 (20-30s): Conclusion**
Visual: Powerful closing shot with memorable imagery
Narration: "Experience the wonder and possibility"
Mood: Uplifting, memorable`;
  };

  const getFallbackImages = (): GeneratedImage[] => {
    return [
      {
        id: 1,
        sceneNumber: 1,
        url: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800",
        description: "Scene 1"
      },
      {
        id: 2,
        sceneNumber: 2,
        url: "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=800",
        description: "Scene 2"
      },
      {
        id: 3,
        sceneNumber: 3,
        url: "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800",
        description: "Scene 3"
      }
    ];
  };

  const regenerateVideo = () => {
    setVideoStatus("pending");
    setVideoProgress(0);
    renderVideo();
  };

  const getStatusColor = (status: StageStatus) => {
    switch (status) {
      case "completed": return "text-green-500";
      case "generating": return "text-blue-500";
      case "error": return "text-red-500";
      default: return "text-muted-foreground";
    }
  };

  const getStatusIcon = (status: StageStatus) => {
    switch (status) {
      case "completed": return <CheckCircle2 className="w-5 h-5" />;
      case "generating": return <Loader2 className="w-5 h-5 animate-spin" />;
      default: return null;
    }
  };

  return (
    <div className="h-full overflow-hidden">
      <div className="h-full flex flex-col p-6">
        
        {/* HEADER - Full Width */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-foreground mb-2">Generate Video</h1>
          <p className="text-muted-foreground">
            Describe your video idea, and AI will create it automatically
          </p>
        </div>

        {/* PROMPT INPUT - Full Width */}
        <Card className="border-2 border-border hover:border-primary/50 transition-colors mb-6 w-full">
          <div className="p-6">
            <div className="flex items-center gap-3 w-full">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Sparkles className="w-5 h-5 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <Textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Describe the video you want to create…"
                  className="min-h-[60px] text-base border-0 focus-visible:ring-0 p-0 resize-none bg-transparent w-full"
                  disabled={isGenerating}
                  rows={2}
                />
              </div>
              <Button
                onClick={handleGenerate}
                disabled={!prompt.trim() || isGenerating}
                className="h-11 px-8 text-base font-medium bg-primary hover:bg-primary/90 text-primary-foreground flex-shrink-0"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5 mr-2" />
                    Generate
                  </>
                )}
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="flex-shrink-0"
                disabled={isGenerating}
                onClick={toggleVoiceInput}
                title="Voice input"
              >
                <Mic className={`w-5 h-5 ${isListening ? 'text-red-500 animate-pulse' : ''}`} />
              </Button>
            </div>
          </div>
        </Card>

        {/* EXAMPLE PROMPTS - Full Width */}
        <Card className="border-2 border-border hover:border-primary/50 transition-colors mb-6 w-full">
          <div className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-base">Example Prompts</h3>
                <p className="text-xs text-muted-foreground">Click any prompt to use it</p>
              </div>
            </div>
            
            <div 
              className="p-3 flex items-center justify-between cursor-pointer hover:bg-muted/50 transition-colors rounded-lg border border-border mb-4"
              onClick={() => setShowExamples(!showExamples)}
            >
              <span className="font-medium text-sm">Browse Examples</span>
              {showExamples ? (
                <ChevronUp className="w-4 h-4 text-muted-foreground" />
              ) : (
                <ChevronDown className="w-4 h-4 text-muted-foreground" />
              )}
            </div>
            
            {showExamples && (
              <div className="grid grid-cols-3 gap-4 max-h-[400px] overflow-y-auto pr-2">
                {Object.entries(EXAMPLE_PROMPTS).map(([category, prompts]) => (
                  <div key={category}>
                    <h4 className="text-xs font-semibold text-muted-foreground mb-2 uppercase tracking-wide">
                      {category}
                    </h4>
                    <div className="space-y-2">
                      {prompts.map((examplePrompt, index) => (
                        <button
                          key={index}
                          onClick={() => {
                            setPrompt(examplePrompt);
                            setShowExamples(false);
                          }}
                          disabled={isGenerating}
                          className="w-full text-left px-3 py-2 text-sm rounded-lg border border-border hover:border-primary/50 hover:bg-primary/5 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {examplePrompt}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>

        {/* Generation Progress Section - Full Width */}
        <div className="grid grid-cols-4 gap-6 mb-6">
          {/* Stage 1: Script */}
          <Card className="border-2 border-border hover:border-primary/50 transition-colors">
            <div className={`p-4 ${
              scriptStatus === "completed" ? "bg-green-500/5" :
              scriptStatus === "generating" ? "bg-blue-500/5" :
              "bg-muted/30"
            }`}>
              <div className="flex items-center gap-3 mb-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  scriptStatus === "completed" ? "bg-green-500/10" :
                  scriptStatus === "generating" ? "bg-blue-500/10" :
                  "bg-muted"
                }`}>
                  <FileText className={`w-5 h-5 ${getStatusColor(scriptStatus)}`} />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-sm">Script Generation</h3>
                  {getStatusIcon(scriptStatus)}
                </div>
              </div>
              {scriptStatus === "generating" && (
                <Progress value={scriptProgress} className="h-1" />
              )}
            </div>
          </Card>

          {/* Stage 2: Audio */}
          <Card className="border-2 border-border hover:border-primary/50 transition-colors">
            <div className={`p-4 ${
              audioStatus === "completed" ? "bg-green-500/5" :
              audioStatus === "generating" ? "bg-blue-500/5" :
              "bg-muted/30"
            }`}>
              <div className="flex items-center gap-3 mb-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  audioStatus === "completed" ? "bg-green-500/10" :
                  audioStatus === "generating" ? "bg-blue-500/10" :
                  "bg-muted"
                }`}>
                  <Volume2 className={`w-5 h-5 ${getStatusColor(audioStatus)}`} />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-sm">Audio Generation</h3>
                  {getStatusIcon(audioStatus)}
                </div>
              </div>
              {audioStatus === "generating" && (
                <Progress value={audioProgress} className="h-1" />
              )}
            </div>
          </Card>

          {/* Stage 3: Images */}
          <Card className="border-2 border-border hover:border-primary/50 transition-colors">
            <div className={`p-4 ${
              imagesStatus === "completed" ? "bg-green-500/5" :
              imagesStatus === "generating" ? "bg-blue-500/5" :
              "bg-muted/30"
            }`}>
              <div className="flex items-center gap-3 mb-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  imagesStatus === "completed" ? "bg-green-500/10" :
                  imagesStatus === "generating" ? "bg-blue-500/10" :
                  "bg-muted"
                }`}>
                  <ImageIcon className={`w-5 h-5 ${getStatusColor(imagesStatus)}`} />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-sm">Image Generation</h3>
                  <p className="text-xs text-muted-foreground">3 scenes</p>
                  {getStatusIcon(imagesStatus)}
                </div>
              </div>
              {imagesStatus === "generating" && (
                <Progress value={imagesProgress} className="h-1" />
              )}
            </div>
          </Card>

          {/* Stage 4: Video */}
          <Card className="border-2 border-border hover:border-primary/50 transition-colors">
            <div className={`p-4 ${
              videoStatus === "completed" ? "bg-green-500/5" :
              videoStatus === "generating" ? "bg-blue-500/5" :
              "bg-muted/30"
            }`}>
              <div className="flex items-center gap-3 mb-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  videoStatus === "completed" ? "bg-green-500/10" :
                  videoStatus === "generating" ? "bg-blue-500/10" :
                  "bg-muted"
                }`}>
                  <Video className={`w-5 h-5 ${getStatusColor(videoStatus)}`} />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-sm">Video Rendering</h3>
                  {getStatusIcon(videoStatus)}
                </div>
              </div>
              {videoStatus === "generating" && (
                <Progress value={videoProgress} className="h-1" />
              )}
            </div>
          </Card>
        </div>

        {/* OUTPUT SECTIONS - Full Width Below */}
        <div className="space-y-6 w-full">
          
          {/* Script Output */}
          {scriptStatus !== "pending" && (
            <Card className="border-2 border-border hover:border-primary/50 transition-colors animate-fade-in mb-6">
              <div className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">Generated Script</h3>
                    <p className="text-xs text-muted-foreground">AI-generated video narration</p>
                  </div>
                </div>
                {scriptStatus === "generating" ? (
                  <div className="space-y-2">
                    <div className="h-4 bg-muted rounded animate-pulse" />
                    <div className="h-4 bg-muted rounded animate-pulse w-4/5" />
                    <div className="h-4 bg-muted rounded animate-pulse w-3/4" />
                  </div>
                ) : (
                  <div className="prose prose-sm max-w-none">
                    <pre className="whitespace-pre-wrap text-sm text-foreground bg-muted/30 p-4 rounded-lg border border-border">
                      {scriptContent}
                    </pre>
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* Audio Output */}
          {audioStatus !== "pending" && (
            <Card className="border-2 border-border hover:border-primary/50 transition-colors animate-fade-in mb-6">
              <div className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <Volume2 className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">Generated Audio</h3>
                    <p className="text-xs text-muted-foreground">Text-to-speech narration</p>
                  </div>
                </div>
                {audioStatus === "generating" ? (
                  <div className="flex items-center gap-3 p-4 bg-muted/30 rounded-lg">
                    <Loader2 className="w-5 h-5 animate-spin text-primary" />
                    <div className="flex-1">
                      <div className="h-12 bg-muted rounded animate-pulse" />
                    </div>
                  </div>
                ) : (
                  <div className="bg-muted/30 rounded-lg p-4 border border-border">
                    {audioUrl ? (
                      <audio controls className="w-full">
                        <source src={audioUrl} type="audio/mpeg" />
                        Your browser does not support the audio element.
                      </audio>
                    ) : (
                      <div className="text-center py-4 text-muted-foreground">
                        Audio generation failed. Please try again.
                      </div>
                    )}
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* Images Output */}
          {imagesStatus !== "pending" && (
            <Card className="border-2 border-border hover:border-primary/50 transition-colors animate-fade-in mb-6 w-full">
              <div className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <ImageIcon className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">Generated Images</h3>
                    <p className="text-xs text-muted-foreground">3 scenes</p>
                  </div>
                </div>
                {imagesStatus === "generating" ? (
                  <div className="grid grid-cols-3 gap-3">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="aspect-video bg-muted rounded-lg animate-pulse" />
                    ))}
                  </div>
                ) : (
                  <div className="grid grid-cols-3 gap-3">
                    {generatedImages.length > 0 ? (
                      generatedImages.map((img) => {
                        const isConverting = convertingImages.has(img.id);
                        const hasAnimatedVideo = animatedVideos.some(v => v.imageId === img.id);
                        
                        return (
                          <div 
                            key={img.id} 
                            className="group relative"
                          >
                            <img
                              src={img.url}
                              alt={img.description}
                              className="w-full aspect-video object-cover rounded-lg border border-border transition-transform"
                              onError={(e) => {
                                // Fallback if image fails to load
                                const target = e.target as HTMLImageElement;
                                target.src = 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800';
                              }}
                            />
                            
                            {/* Hover overlay with buttons */}
                            <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex flex-col items-center justify-center gap-2">
                              <Button
                                size="sm"
                                variant="secondary"
                                className="w-32"
                                onClick={() => setFullscreenImage(img.url)}
                              >
                                <ImageIcon className="w-4 h-4 mr-2" />
                                View Image
                              </Button>
                              
                              <Button
                                size="sm"
                                className="w-32"
                                onClick={() => convertImageToVideo(img)}
                                disabled={isConverting || hasAnimatedVideo}
                              >
                                {isConverting ? (
                                  <>
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    Converting...
                                  </>
                                ) : hasAnimatedVideo ? (
                                  <>
                                    <CheckCircle2 className="w-4 h-4 mr-2" />
                                    Animated
                                  </>
                                ) : (
                                  <>
                                    <Play className="w-4 h-4 mr-2" />
                                    Animate
                                  </>
                                )}
                              </Button>
                            </div>
                            
                            <div className="absolute top-2 left-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                              Scene {img.sceneNumber}
                            </div>
                            
                            {/* Status badge */}
                            {hasAnimatedVideo && (
                              <div className="absolute top-2 right-2 bg-green-500 text-white text-xs px-2 py-1 rounded flex items-center gap-1">
                                <CheckCircle2 className="w-3 h-3" />
                                Animated
                              </div>
                            )}
                          </div>
                        );
                      })
                    ) : (
                      <div className="col-span-3 text-center py-8 text-muted-foreground">
                        No images generated. Check your API keys.
                      </div>
                    )}
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* Animated Videos from Images */}
          {animatedVideos.length > 0 && (
            <Card className="border-2 border-green-500/30 hover:border-green-500/50 bg-gradient-to-br from-green-500/5 to-emerald-500/5 transition-colors animate-fade-in w-full">
              <div className="p-8">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 rounded-lg bg-green-500/10 flex items-center justify-center">
                    <Play className="w-7 h-7 text-green-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-3xl">Animated Videos</h3>
                    <p className="text-sm text-muted-foreground">5-second cinematic animations from your generated images</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-4">
                  {animatedVideos.map((video, index) => (
                    <div key={index} className="group relative">
                      <video
                        src={video.videoUrl}
                        className="w-full aspect-video object-cover rounded-lg border-2 border-green-500/30 shadow-lg"
                        controls
                        preload="metadata"
                      />
                      <div className="absolute top-2 left-2 bg-green-500 text-white text-xs px-2 py-1 rounded flex items-center gap-1">
                        <Play className="w-3 h-3" />
                        Scene {video.sceneNumber}
                      </div>
                      <div className="mt-2 flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          className="flex-1"
                          onClick={() => {
                            const a = document.createElement('a');
                            a.href = video.videoUrl;
                            a.download = `animated_scene_${video.sceneNumber}.mp4`;
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                          }}
                        >
                          <Download className="w-4 h-4 mr-2" />
                          Download
                        </Button>
                        <Button
                          size="sm"
                          className="flex-1"
                          onClick={() => {
                            // Add to editor lab
                            addClip({
                              id: `animated_${video.imageId}_${Date.now()}`,
                              url: video.videoUrl,
                              type: 'video',
                              name: `Animated Scene ${video.sceneNumber}`,
                              duration: 5,
                            });
                            toast({
                              title: "Added to Editor Lab",
                              description: `Scene ${video.sceneNumber} animation added to your project`,
                            });
                          }}
                        >
                          <Plus className="w-4 h-4 mr-2" />
                          Add to Editor
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          )}

          {/* Final Video Output */}
          {videoStatus !== "pending" && (
            <Card className="border-2 border-primary/30 hover:border-primary/50 bg-gradient-to-br from-primary/5 to-accent/5 transition-colors animate-fade-in w-full">
              <div className="p-8">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                    <Video className="w-7 h-7 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-3xl">Final Video</h3>
                    <p className="text-sm text-muted-foreground">Select and preview video clips</p>
                  </div>
                </div>
                {videoStatus === "generating" && (
                  <div className="w-full bg-muted rounded-2xl flex items-center justify-center border-2 border-dashed border-border" style={{ height: '550px' }}>
                    <div className="text-center space-y-4">
                      <Loader2 className="w-20 h-20 animate-spin text-primary mx-auto" />
                      <p className="text-lg text-muted-foreground font-medium">Rendering final video...</p>
                      <Progress value={videoProgress} className="w-80 mx-auto h-2" />
                    </div>
                  </div>
                )}
                {videoStatus !== "generating" && (
                  <div>
                    {/* Main Video Player - Full Width */}
                    <div className="w-full bg-black rounded-2xl mb-6 overflow-hidden border-2 border-border shadow-2xl" style={{ height: '550px' }}>
                      {selectedVideo ? (
                        <video 
                          key={selectedVideo.id}
                          controls 
                          autoPlay
                          className="w-full h-full object-contain"
                          onError={(e) => {
                            console.error('Video failed to load:', selectedVideo.url);
                          }}
                        >
                          <source src={selectedVideo.url} type="video/mp4" />
                          Your browser does not support the video element.
                        </video>
                      ) : (
                        <div className="flex items-center justify-center h-full">
                          <div className="text-center space-y-5 px-8">
                            <Video className="w-24 h-24 text-white/70 mx-auto" />
                            <p className="text-white/70 text-lg font-medium">No videos found</p>
                            <p className="text-white/50 text-sm max-w-md mx-auto">
                              Try a different prompt or check your internet connection.
                            </p>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Video Grid - 10 Videos (Below Player) */}
                    {generatedVideos.length > 0 && (
                      <div className="mb-6">
                        <h4 className="text-sm font-semibold mb-3 text-muted-foreground">Available Videos ({generatedVideos.length})</h4>
                        <div className="grid grid-cols-5 gap-3">
                          {generatedVideos.map((vid, index) => (
                            <div 
                              key={vid.id}
                              onClick={() => {
                                console.log('Selected video:', vid);
                                setSelectedVideo(vid);
                              }}
                              className={`relative group cursor-pointer rounded-lg overflow-hidden border-2 transition-all ${
                                selectedVideo?.id === vid.id 
                                  ? 'border-primary ring-2 ring-primary/20' 
                                  : 'border-border hover:border-primary/50'
                              }`}
                            >
                              <div className="aspect-video bg-black relative">
                                {vid.thumbnail ? (
                                  <img 
                                    src={vid.thumbnail}
                                    alt={`Video ${index + 1}`}
                                    className="w-full h-full object-cover"
                                    onError={(e) => {
                                      // Fallback to video element if thumbnail fails
                                      const target = e.target as HTMLImageElement;
                                      target.style.display = 'none';
                                      const videoEl = target.nextElementSibling as HTMLVideoElement;
                                      if (videoEl) videoEl.style.display = 'block';
                                    }}
                                  />
                                ) : null}
                                <video 
                                  src={vid.url}
                                  className="w-full h-full object-cover"
                                  style={{ display: vid.thumbnail ? 'none' : 'block' }}
                                  muted
                                  preload="metadata"
                                />
                                {/* Hover Overlay with Play and Add Buttons */}
                                <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3">
                                  <Button
                                    size="icon"
                                    variant="secondary"
                                    className="rounded-full bg-white/90 hover:bg-white text-black w-10 h-10"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      console.log('Playing video:', vid);
                                      setSelectedVideo(vid);
                                    }}
                                  >
                                    <Play className="w-5 h-5 fill-black" />
                                  </Button>
                                  <Button
                                    size="icon"
                                    variant="secondary"
                                    className="rounded-full bg-primary hover:bg-primary/90 text-primary-foreground w-10 h-10"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      console.log('Add to Editor clicked for video:', vid);
                                      try {
                                        // Check if already added
                                        const isAdded = clips.find(clip => clip.videoId === vid.id);
                                        if (!isAdded) {
                                          addClip(vid);
                                          toast({
                                            title: "✓ Video Added Successfully!",
                                            description: "Video has been added to Editor Lab",
                                          });
                                        } else {
                                          toast({
                                            title: "Already Added",
                                            description: "This video is already in Editor Lab",
                                          });
                                        }
                                      } catch (error) {
                                        console.error('Error adding clip:', error);
                                        toast({
                                          title: "Error adding clip",
                                          description: "Failed to add clip to Editor Lab",
                                          variant: "destructive",
                                        });
                                      }
                                    }}
                                  >
                                    {clips.find(clip => clip.videoId === vid.id) ? (
                                      <CheckCircle2 className="w-5 h-5" />
                                    ) : (
                                      <Plus className="w-5 h-5" />
                                    )}
                                  </Button>
                                </div>
                                {selectedVideo?.id === vid.id && (
                                  <div className="absolute top-2 right-2 bg-primary text-primary-foreground text-xs px-2 py-1 rounded-full font-semibold">
                                    Playing
                                  </div>
                                )}
                                {clips.find(clip => clip.videoId === vid.id) && (
                                  <div className="absolute top-2 left-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full font-semibold flex items-center gap-1">
                                    <CheckCircle2 className="w-3 h-3" />
                                    Added
                                  </div>
                                )}
                              </div>
                              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2">
                                <p className="text-white text-xs truncate">Video {index + 1}</p>
                                <p className="text-white/60 text-[10px]">{Math.round(vid.duration)}s • {vid.width}x{vid.height}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    <div className="flex gap-4 mt-6">
                      <Button 
                        className="flex-1 h-14 bg-primary hover:bg-primary/90 text-primary-foreground text-lg font-semibold"
                        onClick={() => {
                          if (selectedVideo) {
                            const link = document.createElement('a');
                            link.href = selectedVideo.url;
                            link.download = `video-${selectedVideo.id}.mp4`;
                            link.click();
                          }
                        }}
                        disabled={!selectedVideo}
                      >
                        <Download className="w-6 h-6 mr-2" />
                        Download Selected Video
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </Card>
          )}
        </div> {/* End output sections */}

      </div> {/* End main container */}
      
      {/* Fullscreen Image Modal */}
      {fullscreenImage && (
        <div 
          className="fixed inset-0 z-[100] bg-black flex items-center justify-center p-4 animate-fade-in"
          onClick={() => setFullscreenImage(null)}
        >
          <div className="relative max-w-7xl max-h-full">
            <img 
              src={fullscreenImage} 
              alt="Fullscreen view" 
              className="max-w-full max-h-[100vh] object-contain"
              onClick={(e) => e.stopPropagation()}
            />
            <Button
              variant="secondary"
              size="icon"
              className="absolute top-4 right-4 bg-white/10 hover:bg-white/20 text-white border-white/20 backdrop-blur-sm"
              onClick={() => setFullscreenImage(null)}
            >
              <ChevronDown className="w-6 h-6 rotate-45" />
            </Button>
            <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-white/10 backdrop-blur-sm text-white px-4 py-2 rounded-full text-sm">
              Click anywhere to close
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GenerateVideo;
