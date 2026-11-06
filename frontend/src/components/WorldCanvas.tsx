import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import { ZoomIn, ZoomOut, MessageSquare } from 'lucide-react';

export const WorldCanvas: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  const { state, mapMetadata, selectedNpcId, setSelectedNpcId, setSelectedLocationId } = useSimulationStore();

  const [pan, setPan] = useState<{ x: number; y: number }>({ x: -600, y: -200 });
  const [zoom, setZoom] = useState<number>(0.55);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [showCallouts, setShowCallouts] = useState<boolean>(true);

  // Cached map & sprite images
  const mapBaseImgRef = useRef<HTMLImageElement | null>(null);
  const mapForeImgRef = useRef<HTMLImageElement | null>(null);
  const spriteCache = useRef<Map<string, HTMLImageElement>>(new Map());

  // Previous NPC positions to determine movement direction
  const prevPositions = useRef<Map<string, { x: number; y: number; dir: string }>>(new Map());

  // Load Smallville Map on Mount (loaded once, kept in memory)
  useEffect(() => {
    const baseImg = new Image();
    baseImg.src = '/assets/the_ville/the_ville_base.png';
    baseImg.onload = () => {
      mapBaseImgRef.current = baseImg;
    };
    if (baseImg.complete) {
      mapBaseImgRef.current = baseImg;
    }

    const foreImg = new Image();
    foreImg.src = '/assets/the_ville/the_ville_foreground.png';
    foreImg.onload = () => {
      mapForeImgRef.current = foreImg;
    };
    if (foreImg.complete) {
      mapForeImgRef.current = foreImg;
    }
  }, []);

  // Preload character sprite sheets as NPCs appear
  useEffect(() => {
    if (state?.npcs) {
      for (const npc of state.npcs) {
        const spriteName = npc.sprite_name || 'Klaus_Mueller';
        if (!spriteCache.current.has(spriteName)) {
          const sImg = new Image();
          sImg.src = `/assets/characters/${spriteName}.png`;
          sImg.onload = () => {
            spriteCache.current.set(spriteName, sImg);
          };
          if (sImg.complete) {
            spriteCache.current.set(spriteName, sImg);
          }
        }
      }
    }
  }, [state?.npcs]);

  // Resize canvas to fill container
  const updateCanvasDimensions = useCallback(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const rect = container.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;

    // Center town on initial load
    if (rect.width > 0 && pan.x === -600 && pan.y === -200) {
      setPan({
        x: rect.width / 2 - 2240 * zoom,
        y: rect.height / 2 - 1600 * zoom,
      });
    }
  }, [zoom, pan.x, pan.y]);

  useEffect(() => {
    updateCanvasDimensions();
    window.addEventListener('resize', updateCanvasDimensions);
    return () => window.removeEventListener('resize', updateCanvasDimensions);
  }, [updateCanvasDimensions]);

  // Main Canvas Render Loop (Runs at 60 FPS for smooth sprite animation)
  useEffect(() => {
    let animationFrameId: number;

    const render = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      const dpr = window.devicePixelRatio || 1;
      ctx.save();
      ctx.scale(dpr, dpr);
      ctx.clearRect(0, 0, canvas.width / dpr, canvas.height / dpr);

      // Pixelated crisp rendering for 2D pixel art
      ctx.imageSmoothingEnabled = false;

      // Apply Pan and Zoom
      ctx.translate(pan.x, pan.y);
      ctx.scale(zoom, zoom);

      // 1. Draw Smallville Pixel Art Base Map
      if (mapBaseImgRef.current && mapBaseImgRef.current.complete) {
        ctx.drawImage(mapBaseImgRef.current, 0, 0);
      } else {
        // Fallback placeholder while loading
        ctx.fillStyle = '#7ac943'; // grass green
        ctx.fillRect(0, 0, 4480, 3200);
      }

      // 2. Draw 25 Animated Pixel Art Character Sprites
      if (state?.npcs) {
        const animStep = Math.floor((Date.now() / 180) % 4);

        for (const npc of state.npcs) {
          // World coordinates: 1 unit = 32 pixels
          const px = npc.x * 32;
          const py = npc.y * 32;

          // Compute movement direction
          const prev = prevPositions.current.get(npc.id);
          let direction = prev?.dir || 'down';
          if (prev) {
            const dx = npc.x - prev.x;
            const dy = npc.y - prev.y;
            if (Math.abs(dx) > Math.abs(dy)) {
              if (dx > 0.01) direction = 'right';
              else if (dx < -0.01) direction = 'left';
            } else {
              if (dy > 0.01) direction = 'down';
              else if (dy < -0.01) direction = 'up';
            }
          }
          prevPositions.current.set(npc.id, { x: npc.x, y: npc.y, dir: direction });

          const isSelected = selectedNpcId === npc.id;

          // Selection Glow
          if (isSelected) {
            ctx.fillStyle = 'rgba(56, 189, 248, 0.4)';
            ctx.beginPath();
            ctx.arc(px + 16, py + 16, 24, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 2;
            ctx.stroke();
          }

          // Draw Character Sprite
          const spriteName = npc.sprite_name || 'Klaus_Mueller';
          const spriteImg = spriteCache.current.get(spriteName);

          if (spriteImg && spriteImg.complete) {
            // Source coordinates from atlas
            let srcY = 0; // down
            if (direction === 'left') srcY = 32;
            else if (direction === 'right') srcY = 64;
            else if (direction === 'up') srcY = 96;

            const isMoving = npc.is_moving;
            const srcX = isMoving ? animStep * 32 : 32; // idle is frame 1 (x=32)

            // Draw 32x32 pixel art sprite scaled slightly for visibility
            ctx.drawImage(
              spriteImg,
              srcX,
              srcY,
              32,
              32,
              px,
              py,
              32,
              32
            );
          } else {
            // Fallback avatar circle
            ctx.fillStyle = npc.avatar_color || '#3b82f6';
            ctx.beginPath();
            ctx.arc(px + 16, py + 16, 12, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 1.5;
            ctx.stroke();

            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 10px monospace';
            ctx.textAlign = 'center';
            ctx.fillText(npc.name[0], px + 16, py + 20);
          }

          // Initial & Speech Indicator Above Head (e.g., KM: 💬, AC: ☕, JL: 💬)
          const initials = npc.name
            .split(' ')
            .map((w) => w[0])
            .join('');

          // Speech Bubble Tag (Exactly matching Stanford paper style)
          ctx.fillStyle = '#ffffff';
          ctx.strokeStyle = '#334155';
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.roundRect(px - 10, py - 20, 52, 16, 4);
          ctx.fill();
          ctx.stroke();

          // Tail
          ctx.beginPath();
          ctx.moveTo(px + 12, py - 4);
          ctx.lineTo(px + 16, py);
          ctx.lineTo(px + 20, py - 4);
          ctx.fillStyle = '#ffffff';
          ctx.fill();

          ctx.fillStyle = '#0f172a';
          ctx.font = 'bold 9px system-ui';
          ctx.textAlign = 'left';
          ctx.fillText(`${initials}:`, px - 6, py - 9);

          // Icon in bubble
          const isConversing = npc.current_activity.toLowerCase().includes('converse') || npc.current_activity.toLowerCase().includes('social');
          const isEating = npc.current_activity.toLowerCase().includes('eat') || npc.current_activity.toLowerCase().includes('coffee');
          const isResting = npc.current_activity.toLowerCase().includes('sleep') || npc.current_activity.toLowerCase().includes('rest');

          let icon = '💬';
          if (isEating) icon = '☕';
          else if (isResting) icon = '💤';
          else if (!isConversing) icon = '...';

          ctx.font = '9px system-ui';
          ctx.fillText(icon, px + 18, py - 9);

          // Name label below sprite
          ctx.fillStyle = 'rgba(15, 23, 42, 0.75)';
          ctx.fillRect(px - 14, py + 34, 60, 14);
          ctx.fillStyle = isSelected ? '#38bdf8' : '#f8fafc';
          ctx.font = isSelected ? 'bold 10px system-ui' : '9px system-ui';
          ctx.textAlign = 'center';
          ctx.fillText(npc.name.split(' ')[0], px + 16, py + 44);
          ctx.textAlign = 'left';
        }
      }

      // 3. Draw Foreground Layer (Roofs and tree canopies for depth sorting)
      if (mapForeImgRef.current && mapForeImgRef.current.complete) {
        ctx.drawImage(mapForeImgRef.current, 0, 0);
      }

      // 4. Day / Night & Weather Atmospheric Lighting Overlay
      if (state?.clock) {
        const hour = state.clock.sim_hour;
        let overlayColor = 'rgba(0, 0, 0, 0)';

        if (hour >= 21 || hour < 5) {
          overlayColor = 'rgba(15, 23, 42, 0.45)';
        } else if (hour >= 5 && hour < 7) {
          overlayColor = 'rgba(244, 114, 182, 0.12)';
        } else if (hour >= 17 && hour < 21) {
          overlayColor = 'rgba(251, 146, 60, 0.14)';
        }

        if (overlayColor !== 'rgba(0, 0, 0, 0)') {
          ctx.fillStyle = overlayColor;
          ctx.fillRect(0, 0, 4480, 3200);
        }

        // Gentle Rain Overlay
        if (state.weather?.is_rain) {
          ctx.strokeStyle = 'rgba(186, 230, 253, 0.35)';
          ctx.lineWidth = 1.2;
          for (let i = 0; i < 90; i++) {
            const rx = (i * 97 + (state.clock.tick * 12) % 4480) % 4480;
            const ry = (i * 113 + (state.clock.tick * 22) % 3200) % 3200;
            ctx.beginPath();
            ctx.moveTo(rx, ry);
            ctx.lineTo(rx - 8, ry + 24);
            ctx.stroke();
          }
        }
      }

      ctx.restore();
      animationFrameId = requestAnimationFrame(render);
    };

    animationFrameId = requestAnimationFrame(render);
    return () => cancelAnimationFrame(animationFrameId);
  }, [pan, zoom, state, selectedNpcId]);

  // Click on canvas to select NPC or Location
  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Convert screen coordinates to world pixel coords
    const worldPx = (mouseX - pan.x) / zoom;
    const worldPy = (mouseY - pan.y) / zoom;
    const worldTileX = worldPx / 32;
    const worldTileY = worldPy / 32;

    // Check if clicked an NPC (within 24px)
    if (state?.npcs) {
      for (const npc of state.npcs) {
        const dx = npc.x * 32 + 16 - worldPx;
        const dy = npc.y * 32 + 16 - worldPy;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist <= 28) {
          setSelectedNpcId(npc.id);
          setSelectedLocationId(null);
          return;
        }
      }
    }

    // Check if clicked a building/room
    if (mapMetadata?.locations) {
      for (const loc of mapMetadata.locations) {
        if (
          worldTileX >= loc.x &&
          worldTileX <= loc.x + loc.width &&
          worldTileY >= loc.y &&
          worldTileY <= loc.y + loc.height
        ) {
          setSelectedLocationId(loc.id);
          return;
        }
      }
    }

    setSelectedNpcId(null);
    setSelectedLocationId(null);
  };

  // Drag & Pan handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    }
  };

  const handleMouseUp = () => setIsDragging(false);

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.15 : 0.85;
    setZoom((prev) => Math.max(0.2, Math.min(prev * zoomFactor, 2.2)));
  };

  // Zoom directly to specific Smallville landmark
  const zoomToSector = (tileX: number, tileY: number) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const targetZoom = 1.0;
    const rect = canvas.getBoundingClientRect();
    setZoom(targetZoom);
    setPan({
      x: rect.width / 2 - tileX * 32 * targetZoom,
      y: rect.height / 2 - tileY * 32 * targetZoom,
    });
  };

  return (
    <div
      ref={containerRef}
      className="relative w-full h-full bg-slate-950 overflow-hidden select-none cursor-grab active:cursor-grabbing"
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onWheel={handleWheel}
    >
      <canvas
        ref={canvasRef}
        onClick={handleCanvasClick}
        className="block w-full h-full"
      />

      {/* Floating Canvas Controls */}
      <div className="absolute bottom-4 left-4 flex items-center space-x-2 bg-slate-900/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-700/60 shadow-xl text-xs text-slate-300 z-10">
        <button
          onClick={() => setZoom((z) => Math.min(z * 1.25, 2.2))}
          className="hover:text-white p-1 rounded-lg bg-slate-800 border border-slate-700"
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={() => setZoom((z) => Math.max(z * 0.8, 0.2))}
          className="hover:text-white p-1 rounded-lg bg-slate-800 border border-slate-700"
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <span className="text-slate-400 font-mono">Zoom: {Math.round(zoom * 100)}%</span>
        <span className="text-slate-600">|</span>
        <button
          onClick={() => setShowCallouts((s) => !s)}
          className={`flex items-center space-x-1 px-2 py-0.5 rounded text-xs transition ${
            showCallouts ? 'bg-sky-600 text-white' : 'bg-slate-800 text-slate-400'
          }`}
        >
          <MessageSquare className="w-3.5 h-3.5" />
          <span>Callout Boxes</span>
        </button>
        <span className="text-slate-600">|</span>
        <button
          onClick={() => zoomToSector(75, 45)}
          className="hover:text-white text-slate-400 underline"
        >
          Reset View
        </button>
      </div>

      {/* Quick Landmark Bookmarks */}
      <div className="absolute top-4 left-4 bg-slate-900/90 backdrop-blur-md px-3 py-2 rounded-xl border border-slate-700/60 shadow-xl text-xs text-slate-300 flex items-center space-x-2 z-10">
        <span className="font-bold text-slate-400 uppercase text-[10px] tracking-wider">Smallville Sectors:</span>
        <button
          onClick={() => zoomToSector(77, 21)}
          className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
        >
          ☕ Hobbs Cafe
        </button>
        <button
          onClick={() => zoomToSector(84, 47)}
          className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
        >
          🏪 Willows Market
        </button>
        <button
          onClick={() => zoomToSector(27, 46)}
          className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
        >
          🌳 Johnson Park
        </button>
        <button
          onClick={() => zoomToSector(57, 22)}
          className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
        >
          🍺 Rose & Crown Pub
        </button>
        <button
          onClick={() => zoomToSector(116, 26)}
          className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
        >
          🎓 Oak Hill College
        </button>
      </div>

      {/* Stanford Generative Agents Magnified Callout Boxes (Matching Paper Visualization!) */}
      {showCallouts && (
        <>
          {/* Callout 1: Hobbs Cafe Conversation */}
          <div
            className="absolute top-16 left-80 w-80 bg-slate-900/95 backdrop-blur-md border-2 border-sky-500/70 rounded-2xl shadow-2xl p-3 z-10 text-slate-100 transition-all hover:scale-105 cursor-pointer"
            onClick={() => zoomToSector(77, 21)}
          >
            <div className="flex items-center justify-between pb-1.5 border-b border-slate-800 mb-2">
              <span className="font-bold text-xs text-sky-400 flex items-center space-x-1">
                <span>☕</span>
                <span>Joining for coffee at a cafe</span>
              </span>
              <span className="text-[10px] text-slate-400 font-mono">Hobbs Cafe</span>
            </div>
            <div className="bg-slate-950/70 p-2.5 rounded-xl border border-slate-800/80 font-mono text-[11px] space-y-1 text-slate-300">
              <p className="text-pink-300">
                <span className="font-bold text-white">[Clara]:</span> "Hey Marcus, mind if I join you for warm espresso?"
              </p>
              <p className="text-sky-300">
                <span className="font-bold text-white">[Marcus]:</span> "Not at all, Clara. How is your morning baking going?"
              </p>
            </div>
          </div>

          {/* Callout 2: Willows Market Gossip */}
          <div
            className="absolute bottom-16 right-96 w-84 bg-slate-900/95 backdrop-blur-md border-2 border-amber-500/70 rounded-2xl shadow-2xl p-3 z-10 text-slate-100 transition-all hover:scale-105 cursor-pointer"
            onClick={() => zoomToSector(84, 47)}
          >
            <div className="flex items-center justify-between pb-1.5 border-b border-slate-800 mb-2">
              <span className="font-bold text-xs text-amber-400 flex items-center space-x-1">
                <span>💬</span>
                <span>Sharing news with townsfolk</span>
              </span>
              <span className="text-[10px] text-slate-400 font-mono">The Willows Market</span>
            </div>
            <div className="bg-slate-950/70 p-2.5 rounded-xl border border-slate-800/80 font-mono text-[11px] space-y-1 text-slate-300">
              <p className="text-amber-300">
                <span className="font-bold text-white">[Samuel]:</span> "Have you heard anything new about the Autumn festival plans?"
              </p>
              <p className="text-emerald-300">
                <span className="font-bold text-white">[Sophie]:</span> "Yes! Arthur Vance is drafting the civic notice today."
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
