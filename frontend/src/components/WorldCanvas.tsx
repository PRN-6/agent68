import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useSimulationStore } from '../store/simulationStore';

export const WorldCanvas: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  const { state, mapMetadata, selectedNpcId, setSelectedNpcId, setSelectedLocationId } = useSimulationStore();

  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 20, y: 20 });
  const [zoom, setZoom] = useState<number>(18);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

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

    // Center town on first load
    if (rect.width > 0 && zoom === 18 && pan.x === 20 && pan.y === 20) {
      const scale = Math.min(rect.width / 62, rect.height / 42);
      setZoom(Math.max(14, Math.floor(scale)));
      setPan({
        x: (rect.width - 60 * scale) / 2,
        y: (rect.height - 40 * scale) / 2,
      });
    }
  }, [zoom, pan.x, pan.y]);

  useEffect(() => {
    updateCanvasDimensions();
    window.addEventListener('resize', updateCanvasDimensions);
    return () => window.removeEventListener('resize', updateCanvasDimensions);
  }, [updateCanvasDimensions]);

  // Main Render Loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    ctx.save();
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, canvas.width / dpr, canvas.height / dpr);

    // Apply pan and zoom
    ctx.translate(pan.x, pan.y);
    ctx.scale(zoom / 20, zoom / 20);

    const unit = 20; // 1 coordinate unit = 20 pixels base

    // 1. Draw Ground Grass Background
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, 60 * unit, 40 * unit);

    // 2. Draw Districts
    if (mapMetadata?.districts) {
      for (const dist of mapMetadata.districts) {
        ctx.fillStyle = dist.color;
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.roundRect(
          dist.bounds.x * unit,
          dist.bounds.y * unit,
          dist.bounds.w * unit,
          dist.bounds.h * unit,
          12
        );
        ctx.fill();
        ctx.stroke();

        // District Label
        ctx.fillStyle = 'rgba(148, 163, 184, 0.4)';
        ctx.font = 'bold 11px system-ui';
        ctx.fillText(dist.name.toUpperCase(), (dist.bounds.x + 0.5) * unit, (dist.bounds.y + 1.2) * unit);
      }
    }

    // 3. Draw Roads
    if (mapMetadata?.roads) {
      for (const road of mapMetadata.roads) {
        ctx.strokeStyle = '#334155';
        ctx.lineWidth = road.width * unit;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(road.x1 * unit, road.y1 * unit);
        ctx.lineTo(road.x2 * unit, road.y2 * unit);
        ctx.stroke();

        // Dashed Centerline
        ctx.strokeStyle = '#64748b';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([6, 6]);
        ctx.beginPath();
        ctx.moveTo(road.x1 * unit, road.y1 * unit);
        ctx.lineTo(road.x2 * unit, road.y2 * unit);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    }

    // 4. Draw Buildings
    if (mapMetadata?.locations) {
      for (const loc of mapMetadata.locations) {
        const bx = loc.x * unit;
        const by = loc.y * unit;
        const bw = loc.width * unit;
        const bh = loc.height * unit;

        // Building Shadow
        ctx.fillStyle = 'rgba(0, 0, 0, 0.35)';
        ctx.beginPath();
        ctx.roundRect(bx + 3, by + 4, bw, bh, 8);
        ctx.fill();

        // Building Body
        ctx.fillStyle = '#1e293b';
        ctx.strokeStyle = loc.color || '#475569';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(bx, by, bw, bh, 8);
        ctx.fill();
        ctx.stroke();

        // Roof / Accent Bar
        ctx.fillStyle = loc.color || '#64748b';
        ctx.beginPath();
        ctx.roundRect(bx, by, bw, 6, [8, 8, 0, 0]);
        ctx.fill();

        // Building Name
        ctx.fillStyle = '#f8fafc';
        ctx.font = 'bold 10px system-ui';
        ctx.fillText(loc.name, bx + 6, by + 18, bw - 12);

        // Zone Tag
        ctx.fillStyle = '#94a3b8';
        ctx.font = '9px system-ui';
        ctx.fillText(loc.zone.toUpperCase(), bx + 6, by + 30);

        // Occupant Count Badge
        const occupants = state?.npcs.filter((n) => n.current_location === loc.id) || [];
        if (occupants.length > 0) {
          ctx.fillStyle = '#3b82f6';
          ctx.beginPath();
          ctx.arc(bx + bw - 12, by + 16, 9, 0, Math.PI * 2);
          ctx.fill();
          ctx.fillStyle = '#ffffff';
          ctx.font = 'bold 9px system-ui';
          ctx.textAlign = 'center';
          ctx.fillText(occupants.length.toString(), bx + bw - 12, by + 19);
          ctx.textAlign = 'left';
        }
      }
    }

    // 5. Draw Active Conversations & Speech Bubbles
    if (state?.recent_conversations) {
      for (const conv of state.recent_conversations) {
        if (!conv.is_completed && conv.messages.length > 0) {
          const lastMsg = conv.messages[conv.messages.length - 1];
          const speaker = state.npcs.find((n) => n.id === lastMsg.speaker_id);
          if (speaker) {
            const sx = speaker.x * unit;
            const sy = (speaker.y - 1.8) * unit;

            // Speech bubble
            ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
            ctx.strokeStyle = '#3b82f6';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.roundRect(sx - 70, sy - 26, 140, 24, 6);
            ctx.fill();
            ctx.stroke();

            // Speech tail
            ctx.beginPath();
            ctx.moveTo(sx - 4, sy - 2);
            ctx.lineTo(sx, sy + 4);
            ctx.lineTo(sx + 4, sy - 2);
            ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
            ctx.fill();

            // Speech text
            ctx.fillStyle = '#0f172a';
            ctx.font = 'bold 9px system-ui';
            const cleanText = lastMsg.message.length > 28 ? lastMsg.message.slice(0, 28) + '...' : lastMsg.message;
            ctx.fillText(`💬 ${cleanText}`, sx - 64, sy - 11);
          }
        }
      }
    }

    // 6. Draw 25 NPCs
    if (state?.npcs) {
      for (const npc of state.npcs) {
        const nx = npc.x * unit;
        const ny = npc.y * unit;
        const isSelected = selectedNpcId === npc.id;

        // Selection Pulse Ring
        if (isSelected) {
          ctx.strokeStyle = '#38bdf8';
          ctx.lineWidth = 3;
          ctx.beginPath();
          ctx.arc(nx, ny, 16, 0, Math.PI * 2);
          ctx.stroke();

          ctx.strokeStyle = 'rgba(56, 189, 248, 0.3)';
          ctx.lineWidth = 6;
          ctx.beginPath();
          ctx.arc(nx, ny, 20, 0, Math.PI * 2);
          ctx.stroke();
        }

        // Avatar Shadow
        ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
        ctx.beginPath();
        ctx.ellipse(nx, ny + 10, 10, 5, 0, 0, Math.PI * 2);
        ctx.fill();

        // NPC Circle Avatar
        ctx.fillStyle = npc.avatar_color || '#3b82f6';
        ctx.beginPath();
        ctx.arc(nx, ny, 10, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Initial inside avatar
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 9px system-ui';
        ctx.textAlign = 'center';
        ctx.fillText(npc.name[0], nx, ny + 3);

        // Name Tag
        ctx.font = isSelected ? 'bold 11px system-ui' : '10px system-ui';
        ctx.fillStyle = isSelected ? '#38bdf8' : '#e2e8f0';
        ctx.fillText(npc.name.split(' ')[0], nx, ny + 20);

        // Activity Snippet Tag
        ctx.fillStyle = '#94a3b8';
        ctx.font = '8px system-ui';
        const actLabel = npc.current_activity.length > 18 ? npc.current_activity.slice(0, 18) + '...' : npc.current_activity;
        ctx.fillText(actLabel, nx, ny + 29);

        ctx.textAlign = 'left';
      }
    }

    // 7. Day / Night Atmospheric Lighting Overlay
    if (state?.clock) {
      const hour = state.clock.sim_hour;
      let overlayColor = 'rgba(0, 0, 0, 0)';

      if (hour >= 21 || hour < 5) {
        // Deep Night
        overlayColor = 'rgba(15, 23, 42, 0.45)';
      } else if (hour >= 5 && hour < 7) {
        // Dawn
        overlayColor = 'rgba(244, 114, 182, 0.12)';
      } else if (hour >= 17 && hour < 21) {
        // Evening / Sunset
        overlayColor = 'rgba(251, 146, 60, 0.15)';
      }

      if (overlayColor !== 'rgba(0, 0, 0, 0)') {
        ctx.fillStyle = overlayColor;
        ctx.fillRect(0, 0, 60 * unit, 40 * unit);
      }

      // Rain Weather Effect
      if (state.weather?.is_rain) {
        ctx.strokeStyle = 'rgba(147, 197, 253, 0.35)';
        ctx.lineWidth = 1;
        for (let i = 0; i < 40; i++) {
          const rx = (i * 37 + (state.clock.tick * 8) % 1200) % (60 * unit);
          const ry = (i * 53 + (state.clock.tick * 15) % 800) % (40 * unit);
          ctx.beginPath();
          ctx.moveTo(rx, ry);
          ctx.lineTo(rx - 4, ry + 12);
          ctx.stroke();
        }
      }
    }

    ctx.restore();
  }, [state, mapMetadata, pan, zoom, selectedNpcId]);

  // Click handler to select NPC or Building
  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Convert screen coord to world unit
    const scale = zoom / 20;
    const worldX = (mouseX - pan.x) / (20 * scale);
    const worldY = (mouseY - pan.y) / (20 * scale);

    // 1. Check if clicked an NPC
    if (state?.npcs) {
      for (const npc of state.npcs) {
        const dx = npc.x - worldX;
        const dy = npc.y - worldY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist <= 1.2) {
          setSelectedNpcId(npc.id);
          setSelectedLocationId(null);
          return;
        }
      }
    }

    // 2. Check if clicked a Building
    if (mapMetadata?.locations) {
      for (const loc of mapMetadata.locations) {
        if (
          worldX >= loc.x &&
          worldX <= loc.x + loc.width &&
          worldY >= loc.y &&
          worldY <= loc.y + loc.height
        ) {
          setSelectedLocationId(loc.id);
          return;
        }
      }
    }

    // Clicked empty ground
    setSelectedNpcId(null);
    setSelectedLocationId(null);
  };

  // Pan controls
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
    const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
    setZoom((prev) => Math.max(10, Math.min(prev * zoomFactor, 45)));
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
      <div className="absolute bottom-4 left-4 flex items-center space-x-2 bg-slate-900/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-700/60 shadow-lg text-xs text-slate-300">
        <button
          onClick={() => setZoom((z) => Math.min(z + 3, 45))}
          className="hover:text-white px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 font-bold"
        >
          +
        </button>
        <button
          onClick={() => setZoom((z) => Math.max(z - 3, 10))}
          className="hover:text-white px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 font-bold"
        >
          -
        </button>
        <span className="text-slate-400">Zoom: {Math.round((zoom / 20) * 100)}%</span>
        <span className="text-slate-600">|</span>
        <button
          onClick={() => {
            setZoom(18);
            updateCanvasDimensions();
          }}
          className="hover:text-white text-slate-400 underline"
        >
          Reset View
        </button>
      </div>

      {/* Legend & Town Stats */}
      <div className="absolute top-4 left-4 bg-slate-900/80 backdrop-blur-md px-3 py-2 rounded-lg border border-slate-700/60 shadow-lg text-xs text-slate-300 flex items-center space-x-4">
        <div className="flex items-center space-x-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
          <span>25 Inhabitants Active</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
          <span>12 Residential Mansions & Flats</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
          <span>8 Public Squares & Shops</span>
        </div>
      </div>
    </div>
  );
};
