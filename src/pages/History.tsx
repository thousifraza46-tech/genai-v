import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Play,
  Download,
  Edit3,
  Share2,
  Trash2,
  X,
  Calendar,
  Clock,
  HardDrive,
  Video as VideoIcon,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useEditorStore } from "@/store/editorStore";

interface VideoHistoryItem {
  id: string;
  title: string;
  prompt: string;
  thumbnail: string;
  videoUrl: string;
  dateCreated: string;
  duration: number;
  fileSize: number;
}

const History = () => {
  const navigate = useNavigate();
  const addClip = useEditorStore((state) => state.addClip);
  const [videos, setVideos] = useState<VideoHistoryItem[]>([]);
  const [selectedVideo, setSelectedVideo] = useState<VideoHistoryItem | null>(null);
  const [showPlayer, setShowPlayer] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);
  const [showShareModal, setShowShareModal] = useState<VideoHistoryItem | null>(null);

  useEffect(() => {
    loadVideoHistory();
  }, []);

  const loadVideoHistory = async () => {
    try {
      const savedHistory = localStorage.getItem("videoHistory");
      if (savedHistory) {
        setVideos(JSON.parse(savedHistory));
      } else {
        // Demo data
        setVideos([
          {
            id: "1",
            title: "Beautiful Sunset Beach",
            prompt: "A stunning sunset over a tropical beach with palm trees",
            thumbnail: "/api/placeholder/400/225",
            videoUrl: "/assets/videos/sample1.mp4",
            dateCreated: new Date().toISOString(),
            duration: 30,
            fileSize: 15.2,
          },
          {
            id: "2",
            title: "Mountain Adventure",
            prompt: "Epic mountain landscape with snow peaks and clouds",
            thumbnail: "/api/placeholder/400/225",
            videoUrl: "/assets/videos/sample2.mp4",
            dateCreated: new Date(Date.now() - 86400000).toISOString(),
            duration: 45,
            fileSize: 22.8,
          },
          {
            id: "3",
            title: "City Life Timelapse",
            prompt: "Fast-paced city life with busy streets and lights",
            thumbnail: "/api/placeholder/400/225",
            videoUrl: "/assets/videos/sample3.mp4",
            dateCreated: new Date(Date.now() - 172800000).toISOString(),
            duration: 60,
            fileSize: 31.5,
          },
        ]);
      }
    } catch (error) {
      console.error("Error loading video history:", error);
    }
  };

  const handlePlayVideo = (video: VideoHistoryItem) => {
    setSelectedVideo(video);
    setShowPlayer(true);
  };

  const handleDownload = async (video: VideoHistoryItem) => {
    try {
      const link = document.createElement("a");
      link.href = video.videoUrl;
      link.download = `${video.title.replace(/\s+/g, "_")}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Download error:", error);
      alert("Failed to download video");
    }
  };

  const handleOpenInEditor = (video: VideoHistoryItem) => {
    addClip({
      id: video.id,
      type: "video",
      url: video.videoUrl,
      duration: video.duration,
      thumbnail: video.thumbnail,
      title: video.title,
    });
    navigate("/editor-lab");
  };

  const handleShare = (video: VideoHistoryItem) => {
    setShowShareModal(video);
  };

  const handleShareToWhatsApp = (video: VideoHistoryItem) => {
    const text = encodeURIComponent(`Check out my AI-generated video: ${video.title}`);
    const url = encodeURIComponent(window.location.origin + video.videoUrl);
    window.open(`https://wa.me/?text=${text}%20${url}`, "_blank");
  };

  const handleShareToTelegram = (video: VideoHistoryItem) => {
    const text = encodeURIComponent(`Check out my AI-generated video: ${video.title}`);
    const url = encodeURIComponent(window.location.origin + video.videoUrl);
    window.open(`https://t.me/share/url?url=${url}&text=${text}`, "_blank");
  };

  const handleShareViaEmail = (video: VideoHistoryItem) => {
    const subject = encodeURIComponent(`Check out: ${video.title}`);
    const body = encodeURIComponent(
      `I created this video using AI!\n\nTitle: ${video.title}\nPrompt: ${video.prompt}\n\nWatch it here: ${window.location.origin}${video.videoUrl}`
    );
    window.location.href = `mailto:?subject=${subject}&body=${body}`;
  };

  const handleCopyLink = async (video: VideoHistoryItem) => {
    try {
      const url = window.location.origin + video.videoUrl;
      await navigator.clipboard.writeText(url);
      alert("Link copied to clipboard!");
    } catch (error) {
      console.error("Copy error:", error);
      alert("Failed to copy link");
    }
  };

  const handleDelete = async (videoId: string) => {
    try {
      const updatedVideos = videos.filter((v) => v.id !== videoId);
      setVideos(updatedVideos);
      localStorage.setItem("videoHistory", JSON.stringify(updatedVideos));
      setShowDeleteConfirm(null);
    } catch (error) {
      console.error("Delete error:", error);
      alert("Failed to delete video");
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
  };

  const formatFileSize = (mb: number) => {
    return mb >= 1 ? `${mb.toFixed(1)} MB` : `${(mb * 1024).toFixed(0)} KB`;
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
          Video History
        </h1>
        <p className="text-muted-foreground">
          View and manage all your previously generated videos
        </p>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 bg-gradient-to-br from-primary/10 to-primary/5 border-primary/20">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-primary/20">
              <VideoIcon className="w-5 h-5 text-primary" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Videos</p>
              <p className="text-2xl font-bold text-foreground">{videos.length}</p>
            </div>
          </div>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-accent/10 to-accent/5 border-accent/20">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-accent/20">
              <Clock className="w-5 h-5 text-accent" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Duration</p>
              <p className="text-2xl font-bold text-foreground">
                {formatDuration(videos.reduce((acc, v) => acc + v.duration, 0))}
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-purple-500/10 to-purple-500/5 border-purple-500/20">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-purple-500/20">
              <HardDrive className="w-5 h-5 text-purple-500" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Size</p>
              <p className="text-2xl font-bold text-foreground">
                {formatFileSize(videos.reduce((acc, v) => acc + v.fileSize, 0))}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Video Grid */}
      {videos.length === 0 ? (
        <Card className="p-12 text-center">
          <VideoIcon className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
          <h3 className="text-lg font-semibold mb-2">No videos yet</h3>
          <p className="text-muted-foreground mb-4">
            Start creating amazing videos to see them here
          </p>
          <Button onClick={() => navigate("/generate-video")}>
            Create Your First Video
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {videos.map((video) => (
            <Card
              key={video.id}
              className="group overflow-hidden hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
            >
              {/* Thumbnail */}
              <div className="relative aspect-video overflow-hidden bg-muted">
                <img
                  src={video.thumbnail}
                  alt={video.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                  <Button
                    size="lg"
                    onClick={() => handlePlayVideo(video)}
                    className="rounded-full w-16 h-16 p-0"
                  >
                    <Play className="w-6 h-6" />
                  </Button>
                </div>
              </div>

              {/* Content */}
              <div className="p-4 space-y-3">
                {/* Title */}
                <h3 className="font-semibold text-lg line-clamp-1">{video.title}</h3>

                {/* Prompt */}
                <p className="text-sm text-muted-foreground line-clamp-2">
                  {video.prompt}
                </p>

                {/* Metadata */}
                <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    <span>{formatDate(video.dateCreated)}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    <span>{formatTime(video.dateCreated)}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <VideoIcon className="w-3 h-3" />
                    <span>{formatDuration(video.duration)}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <HardDrive className="w-3 h-3" />
                    <span>{formatFileSize(video.fileSize)}</span>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="grid grid-cols-2 gap-2 pt-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleDownload(video)}
                    className="w-full"
                  >
                    <Download className="w-4 h-4 mr-1" />
                    Download
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleOpenInEditor(video)}
                    className="w-full"
                  >
                    <Edit3 className="w-4 h-4 mr-1" />
                    Edit
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleShare(video)}
                    className="w-full"
                  >
                    <Share2 className="w-4 h-4 mr-1" />
                    Share
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setShowDeleteConfirm(video.id)}
                    className="w-full text-destructive hover:bg-destructive/10"
                  >
                    <Trash2 className="w-4 h-4 mr-1" />
                    Delete
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Video Player Modal */}
      {showPlayer && selectedVideo && (
        <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
          <div className="relative w-full max-w-4xl bg-background rounded-lg overflow-hidden">
            <button
              onClick={() => setShowPlayer(false)}
              className="absolute top-4 right-4 z-10 p-2 rounded-full bg-black/50 hover:bg-black/70 text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
            <video
              controls
              autoPlay
              className="w-full"
              src={selectedVideo.videoUrl}
            >
              Your browser does not support the video tag.
            </video>
            <div className="p-4">
              <h3 className="font-semibold text-lg">{selectedVideo.title}</h3>
              <p className="text-sm text-muted-foreground">{selectedVideo.prompt}</p>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-md p-6 space-y-4">
            <div className="flex items-center gap-3 text-destructive">
              <Trash2 className="w-6 h-6" />
              <h3 className="text-lg font-semibold">Delete Video?</h3>
            </div>
            <p className="text-muted-foreground">
              Are you sure you want to delete this video? This action cannot be undone.
            </p>
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => setShowDeleteConfirm(null)}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={() => handleDelete(showDeleteConfirm)}
                className="flex-1"
              >
                Delete
              </Button>
            </div>
          </Card>
        </div>
      )}

      {/* Share Modal */}
      {showShareModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-md p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Share Video</h3>
              <button
                onClick={() => setShowShareModal(null)}
                className="p-1 hover:bg-muted rounded-full transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-2">
              <Button
                variant="outline"
                onClick={() => handleShareToWhatsApp(showShareModal)}
                className="w-full justify-start"
              >
                <Share2 className="w-4 h-4 mr-2" />
                Share on WhatsApp
              </Button>
              <Button
                variant="outline"
                onClick={() => handleShareToTelegram(showShareModal)}
                className="w-full justify-start"
              >
                <Share2 className="w-4 h-4 mr-2" />
                Share on Telegram
              </Button>
              <Button
                variant="outline"
                onClick={() => handleShareViaEmail(showShareModal)}
                className="w-full justify-start"
              >
                <Share2 className="w-4 h-4 mr-2" />
                Share via Email
              </Button>
              <Button
                variant="outline"
                onClick={() => handleCopyLink(showShareModal)}
                className="w-full justify-start"
              >
                <Share2 className="w-4 h-4 mr-2" />
                Copy Link
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default History;
