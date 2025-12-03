// Global state for Editor Lab - manages editing queue and clips
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface VideoClip {
  id: string;
  videoId: number;
  url: string;
  thumbnail?: string;
  duration: number;
  width: number;
  height: number;
  title: string;
  // Editing properties
  trimStart: number;
  trimEnd: number;
  speed: number;
  volume: number;
  fadeIn: number;
  fadeOut: number;
  brightness: number;
  contrast: number;
  rotation: number;
  flipH: boolean;
  flipV: boolean;
  order: number;
}

interface EditorStore {
  clips: VideoClip[];
  selectedClipId: string | null;
  isExporting: boolean;
  exportProgress: number;
  
  // Actions
  addClip: (video: any) => void;
  removeClip: (clipId: string) => void;
  updateClip: (clipId: string, updates: Partial<VideoClip>) => void;
  selectClip: (clipId: string | null) => void;
  reorderClips: (clips: VideoClip[]) => void;
  clearAll: () => void;
  setExportProgress: (progress: number) => void;
  setIsExporting: (isExporting: boolean) => void;
}

export const useEditorStore = create<EditorStore>()(
  persist(
    (set, get) => ({
      clips: [],
      selectedClipId: null,
      isExporting: false,
      exportProgress: 0,

      addClip: (video: any) => {
        const clips = get().clips;
        
        // Check if already added
        if (clips.find(c => c.videoId === video.id)) {
          return;
        }

        const newClip: VideoClip = {
          id: `clip-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          videoId: video.id,
          url: video.url,
          thumbnail: video.thumbnail,
          duration: video.duration,
          width: video.width,
          height: video.height,
          title: `Clip ${clips.length + 1}`,
          trimStart: 0,
          trimEnd: video.duration,
          speed: 1,
          volume: 100,
          fadeIn: 0,
          fadeOut: 0,
          brightness: 100,
          contrast: 100,
          rotation: 0,
          flipH: false,
          flipV: false,
          order: clips.length,
        };

        set({ clips: [...clips, newClip] });
      },

      removeClip: (clipId: string) => {
        const clips = get().clips.filter(c => c.id !== clipId);
        // Reorder remaining clips
        const reordered = clips.map((clip, index) => ({
          ...clip,
          order: index,
        }));
        set({ 
          clips: reordered,
          selectedClipId: get().selectedClipId === clipId ? null : get().selectedClipId
        });
      },

      updateClip: (clipId: string, updates: Partial<VideoClip>) => {
        set({
          clips: get().clips.map(clip =>
            clip.id === clipId ? { ...clip, ...updates } : clip
          ),
        });
      },

      selectClip: (clipId: string | null) => {
        set({ selectedClipId: clipId });
      },

      reorderClips: (clips: VideoClip[]) => {
        const reordered = clips.map((clip, index) => ({
          ...clip,
          order: index,
        }));
        set({ clips: reordered });
      },

      clearAll: () => {
        set({ clips: [], selectedClipId: null });
      },

      setExportProgress: (progress: number) => {
        set({ exportProgress: progress });
      },

      setIsExporting: (isExporting: boolean) => {
        set({ isExporting });
      },
    }),
    {
      name: 'editor-storage',
    }
  )
);
