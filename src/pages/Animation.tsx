import { useState } from "react";
import { motion } from "framer-motion";
import { Upload, Video, Sparkles, Wand2, Download, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";

const Animation = () => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>("");
  const [generatedVideoUrl, setGeneratedVideoUrl] = useState<string>("");
  const [isConverting, setIsConverting] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.type.startsWith("image/")) {
        toast.error("Please upload a valid image file");
        return;
      }
      
      setSelectedImage(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      setGeneratedVideoUrl(""); // Reset video when new image is uploaded
      toast.success("Image uploaded successfully!");
    }
  };

  const convertImageToVideo = async () => {
    if (!selectedImage) {
      toast.error("Please upload an image first");
      return;
    }

    setIsConverting(true);
    setProgress(0);

    try {
      console.log("[Image-to-Video] Starting conversion...");
      console.log("[Image-to-Video] Image file:", selectedImage.name, selectedImage.type, selectedImage.size, "bytes");
      
      // Show progress simulation
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 2000);

      // Create form data
      const formData = new FormData();
      formData.append("image", selectedImage);
      
      console.log("[Image-to-Video] FormData created, sending request...");

      toast.info("🎬 Creating animated video from your image...", {
        description: "Generating smooth animation with zoom and pan effects (5 seconds)"
      });

      // Send request to backend
      console.log("[Image-to-Video] Sending POST to", getApiUrl(API_CONFIG.endpoints.huggingfaceImageToVideo));
      const response = await fetch(getApiUrl(API_CONFIG.endpoints.huggingfaceImageToVideo), {
        method: "POST",
        body: formData,
      });

      console.log("[Image-to-Video] Response received, status:", response.status);
      clearInterval(progressInterval);

      if (!response.ok) {
        console.error("[Image-to-Video] Error response:", response.status, response.statusText);
        const error = await response.json().catch(() => ({ 
          error: "Server error",
          details: `HTTP ${response.status}: ${response.statusText}` 
        }));
        
        console.error("[Image-to-Video] Error details:", error);
        
        // Provide helpful error messages
        let errorMessage = error.details || error.error || "Failed to convert image to video";
        
        if (response.status === 503) {
          errorMessage = "AI model is currently loading. Please wait 20 seconds and try again.";
        } else if (response.status === 500) {
          errorMessage = "Server error. Please check if the backend is running on port 5000.";
        }
        
        throw new Error(errorMessage);
      }

      console.log("[Image-to-Video] Conversion successful! Reading video blob...");
      setProgress(100);

      // Get video blob with proper type
      const videoBlob = await response.blob();
      console.log("[Image-to-Video] Video blob received:");
      console.log("  - Size:", videoBlob.size, "bytes");
      console.log("  - Type:", videoBlob.type);
      
      // Ensure the blob has the correct MIME type
      const properBlob = new Blob([videoBlob], { type: 'video/mp4' });
      const videoUrl = URL.createObjectURL(properBlob);
      console.log("[Image-to-Video] Video URL created:", videoUrl);
      setGeneratedVideoUrl(videoUrl);

      toast.success("🎉 Video generated successfully!", {
        description: "Your animated video is ready!"
      });
      
    } catch (error: any) {
      console.error("[Image-to-Video] Error:", error);
      console.error("[Image-to-Video] Error stack:", error.stack);
      toast.error("Failed to convert image to video", {
        description: error.message || "Please try again"
      });
    } finally {
      setIsConverting(false);
      setProgress(0);
    }
  };

  const downloadVideo = () => {
    if (!generatedVideoUrl) return;
    
    const a = document.createElement("a");
    a.href = generatedVideoUrl;
    a.download = "animated_video.mp4";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    toast.success("Video downloaded!");
  };

  return (
    <div className="h-full p-8 overflow-auto">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center gap-3">
            <Wand2 className="w-10 h-10 text-primary" />
            <h2 className="text-4xl font-bold bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
              Image to Video
            </h2>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <Card className="p-8 space-y-6 shadow-lg border-2">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-lg bg-primary/10">
                <Upload className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-2xl font-semibold">Upload Image</h3>
            </div>

            {/* Upload Area */}
            <div className="border-2 border-dashed border-primary/30 rounded-xl p-8 text-center hover:border-primary/60 transition-all duration-300 hover:shadow-lg">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
                id="image-upload"
                disabled={isConverting}
              />
              <label htmlFor="image-upload" className="cursor-pointer">
                {previewUrl ? (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="space-y-4"
                  >
                    <img
                      src={previewUrl}
                      alt="Preview"
                      className="max-h-80 mx-auto rounded-lg shadow-xl object-contain"
                    />
                    <p className="text-sm text-muted-foreground font-medium">
                      Click to change image
                    </p>
                  </motion.div>
                ) : (
                  <div className="space-y-6">
                    <motion.div
                      animate={{ scale: [1, 1.1, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                      className="flex justify-center"
                    >
                      <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center shadow-lg">
                        <Upload className="w-10 h-10 text-white" />
                      </div>
                    </motion.div>
                    <div>
                      <p className="text-xl font-semibold mb-2">
                        Click to upload an image
                      </p>
                      <p className="text-sm text-muted-foreground">
                        PNG, JPG, WEBP up to 10MB
                      </p>
                    </div>
                  </div>
                )}
              </label>
            </div>

            {/* Convert Button */}
            <Button
              onClick={convertImageToVideo}
              disabled={!selectedImage || isConverting}
              className="w-full h-14 text-lg font-semibold bg-gradient-to-r from-primary to-purple-600 hover:from-primary/90 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
              size="lg"
            >
              {isConverting ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Converting... {progress}%
                </>
              ) : (
                <>
                  <Video className="w-5 h-5 mr-2" />
                  Generate Animated Video
                </>
              )}
            </Button>

            {isConverting && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-3"
              >
                <div className="h-3 bg-secondary rounded-full overflow-hidden shadow-inner">
                  <motion.div
                    className="h-full bg-gradient-to-r from-primary to-purple-600"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.5, ease: "easeInOut" }}
                  />
                </div>
                <div className="text-center space-y-1">
                  <p className="text-sm font-medium text-foreground flex items-center justify-center gap-2">
                    <Sparkles className="w-4 h-4 text-primary animate-pulse" />
                    AI is animating your image...
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Using Stable Video Diffusion model
                  </p>
                </div>
              </motion.div>
            )}
          </Card>

          {/* Output Section */}
          <Card className="p-8 space-y-6 shadow-lg border-2">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-lg bg-purple-600/10">
                <Video className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="text-2xl font-semibold">Generated Video</h3>
            </div>

            {generatedVideoUrl ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="space-y-6"
              >
                <div className="relative rounded-xl overflow-hidden shadow-2xl bg-black">
                  <video
                    src={generatedVideoUrl}
                    controls
                    autoPlay
                    loop
                    muted
                    className="w-full max-h-96 object-contain"
                  />
                  <div className="absolute top-3 right-3">
                    <div className="px-3 py-1.5 bg-black/70 backdrop-blur-sm rounded-full text-xs font-medium text-white flex items-center gap-1.5">
                      <Sparkles className="w-3 h-3 text-primary" />
                      AI Generated
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <Button
                    onClick={downloadVideo}
                    variant="outline"
                    className="w-full h-12 text-base font-semibold border-2 hover:bg-primary/10 hover:border-primary transition-all duration-300"
                    size="lg"
                  >
                    <Download className="w-5 h-5 mr-2" />
                    Download Video
                  </Button>

                  <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/30">
                    <p className="text-sm text-green-700 dark:text-green-400 font-medium flex items-center gap-2">
                      <Sparkles className="w-4 h-4" />
                      Video generation complete!
                    </p>
                  </div>
                </div>
              </motion.div>
            ) : (
              <div className="h-96 flex flex-col items-center justify-center text-center space-y-4 border-2 border-dashed border-muted-foreground/20 rounded-xl">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                  className="w-24 h-24 rounded-full border-4 border-primary/20 border-t-primary"
                />
                <div className="space-y-2">
                  <p className="text-lg font-medium text-muted-foreground">
                    No video generated yet
                  </p>
                  <p className="text-sm text-muted-foreground/70">
                    Upload an image and click "Generate" to create your animated video
                  </p>
                </div>
              </div>
            )}
          </Card>
        </div>

        {/* Info Section */}
        <Card className="p-6 bg-gradient-to-r from-primary/5 to-purple-600/5 border-primary/20">
          <div className="flex items-start gap-4">
            <div className="p-2 rounded-lg bg-primary/10">
              <Sparkles className="w-6 h-6 text-primary" />
            </div>
            <div className="flex-1 space-y-2">
              <h4 className="font-semibold text-lg">How it works</h4>
              <ul className="text-sm text-muted-foreground space-y-1.5">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary" />
                  Upload any image (landscape, portrait, or any subject)
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary" />
                  AI analyzes the image and generates smooth motion
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary" />
                  Download your animated video in MP4 format
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary" />
                  Processing time: 30-60 seconds per image
                </li>
              </ul>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Animation;
