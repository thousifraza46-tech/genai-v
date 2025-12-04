import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { useEditorStore, VideoClip } from "@/store/editorStore";
import { useToast } from "@/hooks/use-toast";
import { API_CONFIG, getApiUrl } from "@/config/api";
import {
  Play,
  Pause,
  Download,
  Trash2,
  Scissors,
  Video,
  Volume2,
  Sun,
  RotateCw,
  FlipHorizontal,
  FlipVertical,
  Zap,
  Share2,
  Loader2,
  AlertCircle,
  GripVertical,
} from "lucide-react";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  horizontalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

// Sortable clip thumbnail component
interface SortableClipCardProps {
  clip: VideoClip;
  isSelected: boolean;
  onClick: (clip: VideoClip) => void;
  onRemove: (id: string) => void;
}

const SortableClipCard = ({ clip, isSelected, onClick, onRemove }: SortableClipCardProps) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({ id: clip.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`relative group rounded-lg overflow-hidden border-2 cursor-pointer transition-all ${
        isSelected
          ? "border-primary ring-2 ring-primary/20"
          : "border-border hover:border-primary/50"
      }`}
    >
      <div {...attributes} {...listeners} className="absolute top-2 left-2 z-10 cursor-move">
        <div className="bg-black/60 backdrop-blur-sm p-1 rounded">
          <GripVertical className="w-4 h-4 text-white" />
        </div>
      </div>

      <div 
        className="aspect-video bg-black relative" 
        onClick={() => onClick(clip)}
      >
        {clip.thumbnail ? (
          <img
            src={clip.thumbnail}
            alt={clip.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Video className="w-8 h-8 text-white/50" />
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
      </div>

      <Button
        size="icon"
        variant="destructive"
        className="absolute top-2 right-2 w-6 h-6 opacity-0 group-hover:opacity-100 transition-opacity"
        onClick={(e) => {
          e.stopPropagation();
          onRemove(clip.id);
        }}
      >
        <Trash2 className="w-3 h-3" />
      </Button>

      <div className="absolute bottom-0 left-0 right-0 p-2">
        <p className="text-white text-xs truncate font-medium">{clip.title}</p>
        <p className="text-white/60 text-[10px]">
          {(clip.trimEnd - clip.trimStart).toFixed(1)}s
        </p>
      </div>

      {isSelected && (
        <div className="absolute top-2 right-2 bg-primary text-primary-foreground text-xs px-2 py-1 rounded-full font-semibold">
          Editing
        </div>
      )}
    </div>
  );
};

const EditorLab = () => {
  const { toast } = useToast();
  const {
    clips,
    selectedClipId,
    isExporting,
    exportProgress,
    addClip,
    removeClip,
    updateClip,
    selectClip,
    reorderClips,
    clearAll,
    setExportProgress,
    setIsExporting,
  } = useEditorStore();

  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [showShareDialog, setShowShareDialog] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  const selectedClip = clips.find((c) => c.id === selectedClipId);

  // Update video properties when clip settings change
  useEffect(() => {
    if (videoRef.current && selectedClip) {
      videoRef.current.playbackRate = selectedClip.speed;
      // Ensure volume is between 0 and 1 (HTML5 video requirement)
      videoRef.current.volume = Math.min(1, selectedClip.volume / 100);
      
      // Ensure video stays within trim bounds
      if (videoRef.current.currentTime < selectedClip.trimStart || 
          videoRef.current.currentTime > selectedClip.trimEnd) {
        videoRef.current.currentTime = selectedClip.trimStart;
      }
    }
  }, [selectedClip]);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = clips.findIndex((c) => c.id === active.id);
      const newIndex = clips.findIndex((c) => c.id === over.id);
      reorderClips(arrayMove(clips, oldIndex, newIndex));
    }
  };

  const handlePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleExport = async () => {
    if (clips.length === 0) {
      toast({
        title: "No clips to export",
        description: "Add some clips to the timeline first",
        variant: "destructive",
      });
      return;
    }

    setIsExporting(true);
    setExportProgress(0);

    try {
      // Simulate export progress
      const progressInterval = setInterval(() => {
        const currentProgress = useEditorStore.getState().exportProgress;
        if (currentProgress >= 95) {
          clearInterval(progressInterval);
        } else {
          setExportProgress(Math.min(95, currentProgress + 5));
        }
      }, 200);

      // Call backend API to export video
      console.log("[EditorLab] Starting export with", clips.length, "clips");
      console.log("[EditorLab] Clips data:", clips);
      
      const response = await fetch(getApiUrl(API_CONFIG.endpoints.editorExport), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          clips: clips.map((clip) => ({
            url: clip.url,
            trimStart: clip.trimStart,
            trimEnd: clip.trimEnd,
            speed: clip.speed,
            volume: clip.volume,
            fadeIn: clip.fadeIn,
            fadeOut: clip.fadeOut,
            brightness: clip.brightness,
            contrast: clip.contrast,
            rotation: clip.rotation,
            flipH: clip.flipH,
            flipV: clip.flipV,
          })),
        }),
      });

      clearInterval(progressInterval);
      
      console.log("[EditorLab] Export response status:", response.status);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: "Unknown error" }));
        console.error("[EditorLab] Export failed:", errorData);
        throw new Error(errorData.error || "Export failed");
      }

      const data = await response.json();
      console.log("[EditorLab] Export successful:", data);
      setExportProgress(100);

      toast({
        title: "Video exported successfully!",
        description: "Your video is ready to download",
      });

      // Download the exported video
      if (data.video_url) {
        const link = document.createElement("a");
        link.href = data.video_url;
        link.download = `edited-video-${Date.now()}.mp4`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (error: any) {
      console.error("[EditorLab] Export error:", error);
      toast({
        title: "Export failed",
        description: error.message || "There was an error exporting your video. Please try again.",
        variant: "destructive",
      });
    } finally {
      setTimeout(() => {
        setIsExporting(false);
        setExportProgress(0);
      }, 1000);
    }
  };

  const handleCombineClips = async () => {
    if (clips.length < 2) {
      toast({
        title: "Not enough clips",
        description: "Select at least 2 clips to combine them into one video",
        variant: "destructive",
      });
      return;
    }

    setIsExporting(true);
    setExportProgress(0);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        const currentProgress = useEditorStore.getState().exportProgress;
        if (currentProgress >= 95) {
          clearInterval(progressInterval);
        } else {
          setExportProgress(Math.min(95, currentProgress + 5));
        }
      }, 300);

      console.log("[EditorLab] Combining", clips.length, "clips");
      
      // Call backend API to combine clips
      const response = await fetch(getApiUrl('/editor/combine-clips'), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          clips: clips.map((clip) => clip.url),
        }),
      });

      clearInterval(progressInterval);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: "Unknown error" }));
        console.error("[EditorLab] Combine failed:", errorData);
        throw new Error(errorData.error || "Failed to combine clips");
      }

      const data = await response.json();
      console.log("[EditorLab] Combine successful:", data);
      setExportProgress(100);

      toast({
        title: "Clips combined successfully!",
        description: `${data.clip_count} clips merged into one video (${data.duration.toFixed(1)}s)`,
      });

      // Download the combined video
      if (data.video_url) {
        const link = document.createElement("a");
        link.href = data.video_url;
        link.download = `combined-video-${Date.now()}.mp4`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (error: any) {
      console.error("[EditorLab] Combine error:", error);
      toast({
        title: "Combine failed",
        description: error.message || "Failed to combine video clips. Please try again.",
        variant: "destructive",
      });
    } finally {
      setTimeout(() => {
        setIsExporting(false);
        setExportProgress(0);
      }, 1000);
    }
  };

  const handleClearAll = () => {
    if (window.confirm("Are you sure you want to clear all clips? This cannot be undone.")) {
      clearAll();
      toast({
        title: "Editor cleared",
        description: "All clips have been removed",
      });
    }
  };

  const handleShare = async (platform: string) => {
    if (clips.length === 0) {
      toast({
        title: "No video to share",
        description: "Please add clips and export your video first",
        variant: "destructive",
      });
      setShowShareDialog(false);
      return;
    }

    // For now, copy the video URL to clipboard or show instructions
    const videoUrl = clips[0]?.url; // Get first clip URL as example
    
    if (platform === "Copy Link") {
      if (videoUrl) {
        navigator.clipboard.writeText(videoUrl);
        toast({
          title: "Link copied!",
          description: "Video URL has been copied to clipboard",
        });
      }
    } else {
      toast({
        title: `Share to ${platform}`,
        description: "Please export your video first, then share the downloaded file",
      });
    }
    
    setShowShareDialog(false);
  };

  return (
    <div className="h-full overflow-auto">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground mb-2">Editor Lab</h1>
            <p className="text-muted-foreground">
              Edit, trim, and enhance your video clips
            </p>
          </div>
          <div className="flex gap-3">
            {clips.length > 0 && (
              <>
                <Button variant="outline" onClick={handleClearAll}>
                  <Trash2 className="w-4 h-4 mr-2" />
                  Clear All
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setShowShareDialog(true)}
                  disabled={clips.length === 0}
                >
                  <Share2 className="w-4 h-4 mr-2" />
                  Share
                </Button>
                <Button
                  variant="outline"
                  onClick={handleCombineClips}
                  disabled={isExporting || clips.length < 2}
                  className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white border-0"
                >
                  {isExporting ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Combining...
                    </>
                  ) : (
                    <>
                      <Video className="w-4 h-4 mr-2" />
                      Combine Clips
                    </>
                  )}
                </Button>
                <Button
                  onClick={handleExport}
                  disabled={isExporting || clips.length === 0}
                  className="bg-primary hover:bg-primary/90"
                >
                  {isExporting ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Exporting... {exportProgress}%
                    </>
                  ) : (
                    <>
                      <Download className="w-4 h-4 mr-2" />
                      Export Video
                    </>
                  )}
                </Button>
              </>
            )}
          </div>
        </div>

        {clips.length === 0 ? (
          /* Empty State */
          <Card className="border-2 border-dashed border-border">
            <div className="p-12 text-center space-y-4">
              <Video className="w-16 h-16 mx-auto text-muted-foreground" />
              <div>
                <h3 className="text-lg font-semibold mb-2">No clips in timeline</h3>
                <p className="text-muted-foreground text-sm">
                  Go to <strong>Generate Video</strong> tab and click{" "}
                  <strong>"Add to Editor"</strong> on any video thumbnail
                </p>
              </div>
            </div>
          </Card>
        ) : (
          <>
            {/* Timeline Panel */}
            <Card className="border-2 border-border">
              <div className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Video className="w-5 h-5 text-primary" />
                  <h3 className="font-semibold text-lg">Clip Timeline</h3>
                  <span className="text-sm text-muted-foreground">
                    ({clips.length} {clips.length === 1 ? "clip" : "clips"})
                  </span>
                </div>

                <DndContext
                  sensors={sensors}
                  collisionDetection={closestCenter}
                  onDragEnd={handleDragEnd}
                >
                  <SortableContext
                    items={clips.map((c) => c.id)}
                    strategy={horizontalListSortingStrategy}
                  >
                    <div className="grid grid-cols-6 gap-3">
                      {clips.map((clip) => (
                        <SortableClipCard
                          key={clip.id}
                          clip={clip}
                          isSelected={clip.id === selectedClipId}
                          onClick={() => selectClip(clip.id)}
                          onRemove={() => removeClip(clip.id)}
                        />
                      ))}
                    </div>
                  </SortableContext>
                </DndContext>
              </div>
            </Card>

            {/* Main Editor Area */}
            <div className="grid grid-cols-2 gap-6">
              {/* Preview Panel */}
              <Card className="border-2 border-border">
                <div className="p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <Play className="w-5 h-5 text-primary" />
                    <h3 className="font-semibold text-lg">Preview</h3>
                  </div>

                  <div className="bg-black rounded-lg overflow-hidden mb-4">
                    {selectedClip ? (
                      <video
                        ref={videoRef}
                        src={selectedClip.url}
                        className="w-full aspect-video object-contain"
                        style={{
                          filter: `brightness(${selectedClip.brightness}%) contrast(${selectedClip.contrast}%)`,
                          transform: `rotate(${selectedClip.rotation}deg) scaleX(${selectedClip.flipH ? -1 : 1}) scaleY(${selectedClip.flipV ? -1 : 1})`,
                        }}
                        onTimeUpdate={(e) => {
                          const video = e.currentTarget;
                          const adjustedTime = video.currentTime;
                          setCurrentTime(adjustedTime);
                          
                          // Apply trim limits
                          if (video.currentTime < selectedClip.trimStart) {
                            video.currentTime = selectedClip.trimStart;
                          } else if (video.currentTime > selectedClip.trimEnd) {
                            video.currentTime = selectedClip.trimStart;
                            video.pause();
                            setIsPlaying(false);
                          }
                        }}
                        onLoadedMetadata={(e) => {
                          const video = e.currentTarget;
                          video.currentTime = selectedClip.trimStart;
                          video.playbackRate = selectedClip.speed;
                          video.volume = selectedClip.volume / 100;
                        }}
                        onPlay={() => setIsPlaying(true)}
                        onPause={() => setIsPlaying(false)}
                      />
                    ) : (
                      <div className="w-full aspect-video flex items-center justify-center">
                        <div className="text-center text-white/50">
                          <Video className="w-12 h-12 mx-auto mb-2" />
                          <p>Select a clip to preview</p>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-3">
                    <Button
                      size="icon"
                      variant="outline"
                      onClick={handlePlayPause}
                      disabled={!selectedClip}
                    >
                      {isPlaying ? (
                        <Pause className="w-4 h-4" />
                      ) : (
                        <Play className="w-4 h-4" />
                      )}
                    </Button>
                    <div className="flex-1">
                      <Slider
                        value={[currentTime]}
                        max={selectedClip?.duration || 100}
                        step={0.1}
                        onValueChange={([value]) => {
                          if (videoRef.current) {
                            videoRef.current.currentTime = value;
                            setCurrentTime(value);
                          }
                        }}
                        disabled={!selectedClip}
                      />
                    </div>
                    <span className="text-sm text-muted-foreground w-20 text-right">
                      {selectedClip
                        ? `${currentTime.toFixed(1)}s / ${selectedClip.duration.toFixed(1)}s`
                        : "0.0s"}
                    </span>
                  </div>
                </div>
              </Card>

              {/* Editing Tools */}
              <Card className="border-2 border-border">
                <div className="p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <Scissors className="w-5 h-5 text-primary" />
                    <h3 className="font-semibold text-lg">Editing Tools</h3>
                  </div>

                  {selectedClip ? (
                    <div className="space-y-6">
                      {/* Trim Controls */}
                      <div className="space-y-2">
                        <label className="text-sm font-medium flex items-center gap-2">
                          <Scissors className="w-4 h-4" />
                          Trim
                        </label>
                        <div className="space-y-3">
                          <div className="flex items-center gap-3">
                            <span className="text-xs text-muted-foreground w-12">
                              Start:
                            </span>
                            <Slider
                              value={[selectedClip.trimStart]}
                              max={selectedClip.duration}
                              step={0.1}
                              onValueChange={([value]) =>
                                updateClip(selectedClip.id, {
                                  trimStart: Math.min(value, selectedClip.trimEnd - 0.1),
                                })
                              }
                            />
                            <span className="text-xs text-muted-foreground w-12 text-right">
                              {selectedClip.trimStart.toFixed(1)}s
                            </span>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="text-xs text-muted-foreground w-12">
                              End:
                            </span>
                            <Slider
                              value={[selectedClip.trimEnd]}
                              max={selectedClip.duration}
                              step={0.1}
                              onValueChange={([value]) =>
                                updateClip(selectedClip.id, {
                                  trimEnd: Math.max(value, selectedClip.trimStart + 0.1),
                                })
                              }
                            />
                            <span className="text-xs text-muted-foreground w-12 text-right">
                              {selectedClip.trimEnd.toFixed(1)}s
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Speed Control */}
                      <div className="space-y-2">
                        <label className="text-sm font-medium flex items-center gap-2">
                          <Zap className="w-4 h-4" />
                          Speed: {selectedClip.speed.toFixed(1)}x
                        </label>
                        <Slider
                          value={[selectedClip.speed]}
                          min={0.25}
                          max={4}
                          step={0.25}
                          onValueChange={([value]) =>
                            updateClip(selectedClip.id, { speed: value })
                          }
                        />
                      </div>

                      {/* Volume Control */}
                      <div className="space-y-2">
                        <label className="text-sm font-medium flex items-center gap-2">
                          <Volume2 className="w-4 h-4" />
                          Volume: {selectedClip.volume}%
                        </label>
                        <Slider
                          value={[selectedClip.volume]}
                          max={200}
                          step={1}
                          onValueChange={([value]) =>
                            updateClip(selectedClip.id, { volume: value })
                          }
                        />
                      </div>

                      {/* Fade Controls */}
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <label className="text-sm font-medium">
                            Fade In: {selectedClip.fadeIn.toFixed(1)}s
                          </label>
                          <Slider
                            value={[selectedClip.fadeIn]}
                            max={5}
                            step={0.1}
                            onValueChange={([value]) =>
                              updateClip(selectedClip.id, { fadeIn: value })
                            }
                          />
                        </div>
                        <div className="space-y-2">
                          <label className="text-sm font-medium">
                            Fade Out: {selectedClip.fadeOut.toFixed(1)}s
                          </label>
                          <Slider
                            value={[selectedClip.fadeOut]}
                            max={5}
                            step={0.1}
                            onValueChange={([value]) =>
                              updateClip(selectedClip.id, { fadeOut: value })
                            }
                          />
                        </div>
                      </div>

                      {/* Brightness & Contrast */}
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <label className="text-sm font-medium flex items-center gap-2">
                            <Sun className="w-4 h-4" />
                            Brightness: {selectedClip.brightness}%
                          </label>
                          <Slider
                            value={[selectedClip.brightness]}
                            min={0}
                            max={200}
                            step={1}
                            onValueChange={([value]) =>
                              updateClip(selectedClip.id, { brightness: value })
                            }
                          />
                        </div>
                        <div className="space-y-2">
                          <label className="text-sm font-medium">
                            Contrast: {selectedClip.contrast}%
                          </label>
                          <Slider
                            value={[selectedClip.contrast]}
                            min={0}
                            max={200}
                            step={1}
                            onValueChange={([value]) =>
                              updateClip(selectedClip.id, { contrast: value })
                            }
                          />
                        </div>
                      </div>

                      {/* Transform Controls */}
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() =>
                            updateClip(selectedClip.id, {
                              rotation: (selectedClip.rotation + 90) % 360,
                            })
                          }
                        >
                          <RotateCw className="w-4 h-4 mr-2" />
                          Rotate
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() =>
                            updateClip(selectedClip.id, {
                              flipH: !selectedClip.flipH,
                            })
                          }
                        >
                          <FlipHorizontal className="w-4 h-4 mr-2" />
                          Flip H
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() =>
                            updateClip(selectedClip.id, {
                              flipV: !selectedClip.flipV,
                            })
                          }
                        >
                          <FlipVertical className="w-4 h-4 mr-2" />
                          Flip V
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-12 text-muted-foreground">
                      <AlertCircle className="w-12 h-12 mx-auto mb-3" />
                      <p>Select a clip to edit</p>
                    </div>
                  )}
                </div>
              </Card>
            </div>
          </>
        )}

        {/* Share Dialog */}
        {showShareDialog && (
          <div
            className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"
            onClick={() => setShowShareDialog(false)}
          >
            <Card
              className="max-w-md w-full p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-lg font-semibold mb-4">Share Video</h3>
              <div className="grid grid-cols-2 gap-3">
                {[
                  "WhatsApp",
                  "Email",
                  "Telegram",
                  "Google Drive",
                  "X (Twitter)",
                  "Link",
                ].map((platform) => (
                  <Button
                    key={platform}
                    variant="outline"
                    onClick={() => handleShare(platform)}
                  >
                    <Share2 className="w-4 h-4 mr-2" />
                    {platform}
                  </Button>
                ))}
              </div>
              <Button
                variant="ghost"
                className="w-full mt-4"
                onClick={() => setShowShareDialog(false)}
              >
                Cancel
              </Button>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default EditorLab;
