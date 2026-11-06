import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import { ZoomIn, ZoomOut, MessageSquare } from 'lucide-react';

export const WorldCanvas: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  const {
    state,
    mapMetadata,
    selectedNpcId,
    setSelectedNpcId,
    setSelectedLocationId,
    mapTheme,
    setMapTheme,
    setIsTilesetModalOpen,
  } = useSimulationStore();

  const [pan, setPan] = useState<{ x: number; y: number }>({ x: -600, y: -200 });
  const [zoom, setZoom] = useState<number>(0.55);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [showCallouts, setShowCallouts] = useState<boolean>(true);

  // Cached map & sprite images
  const themeImages = useRef<{
    base: HTMLImageElement | null;
    fore: HTMLImageElement | null;
  }>({
    base: null,
    fore: null,
  });
  const spriteCache = useRef<Map<string, HTMLImageElement>>(new Map());

  // Previous NPC positions to determine movement direction
  const prevPositions = useRef<Map<string, { x: number; y: number; dir: string }>>(new Map());

  // Load MMORPG Fantasy Map on Mount
  useEffect(() => {
    const bImg = new Image();
    bImg.src = '/assets/the_ville/the_ville_base.png?v=fantasy_realm_v4';
    bImg.onload = () => {
      themeImages.current.base = bImg;
    };
    if (bImg.complete) {
      themeImages.current.base = bImg;
    }

    const fImg = new Image();
    fImg.src = '/assets/the_ville/the_ville_foreground.png?v=fantasy_realm_v4';
    fImg.onload = () => {
      themeImages.current.fore = fImg;
    };
    if (fImg.complete) {
      themeImages.current.fore = fImg;
    }
  }, []);

  // Preload character sprite sheets as NPCs appear
  useEffect(() => {
    // Preload Kenney walk sheets
    for (let i = 1; i <= 5; i++) {
      const kKey = `kenney_char_${i}`;
      if (!spriteCache.current.has(kKey)) {
        const kImg = new Image();
        kImg.src = `/assets/characters/kenney/${kKey}.png`;
        kImg.onload = () => { spriteCache.current.set(kKey, kImg); };
        if (kImg.complete) spriteCache.current.set(kKey, kImg);
      }
    }

    // Preload Stanford character sheets
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

  // Main Canvas Render Loop (60 FPS)
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

      // 1. Draw Active Pixel Art Base Map
      const activeBase = themeImages.current.base;
      if (activeBase && activeBase.complete) {
        ctx.drawImage(activeBase, 0, 0);
      } else {
        ctx.fillStyle = '#228B22';
        ctx.fillRect(0, 0, 4480, 3200);
      }

      // 2. Draw Party Formation Bonds / Link Lines
      if (state?.parties && state?.npcs) {
        for (const party of state.parties) {
          const members = state.npcs.filter((n) => party.member_ids.includes(n.id));
          if (members.length > 1) {
            ctx.save();
            ctx.strokeStyle = party.banner_color || '#38bdf8';
            ctx.lineWidth = 1.5;
            ctx.setLineDash([4, 4]);

            for (let i = 0; i < members.length - 1; i++) {
              const p1 = members[i];
              const p2 = members[i + 1];
              const dist = Math.hypot(p1.x - p2.x, p1.y - p2.y);
              // Only draw link when members are reasonably near each other (traveling or in same chamber)
              if (dist < 18) {
                ctx.beginPath();
                ctx.moveTo(p1.x * 32 + 16, p1.y * 32 + 16);
                ctx.lineTo(p2.x * 32 + 16, p2.y * 32 + 16);
                ctx.stroke();
              }
            }
            ctx.restore();
          }
        }
      }

      // 3. Draw 25 Animated Pixel Art Adventurers
      if (state?.npcs) {
        const animStep = Math.floor((Date.now() / 180) % 4);

        for (const npc of state.npcs) {
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

          // Selection Glow Ring
          if (isSelected) {
            ctx.fillStyle = 'rgba(56, 189, 248, 0.4)';
            ctx.beginPath();
            ctx.arc(px + 16, py + 16, 26, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 2.5;
            ctx.stroke();
          }

          // Sprite Rendering
          let spriteKey = npc.sprite_name || 'Klaus_Mueller';
          if (mapTheme === 'kenney_urban') {
            const charNum = ((npc.id.charCodeAt(npc.id.length - 1) || 0) % 5) + 1;
            spriteKey = `kenney_char_${charNum}`;
          }
          const spriteImg = spriteCache.current.get(spriteKey);

          if (spriteImg && spriteImg.complete) {
            let srcY = 0; // down
            if (direction === 'left') srcY = 32;
            else if (direction === 'right') srcY = 64;
            else if (direction === 'up') srcY = 96;

            const isMoving = npc.is_moving;
            const srcX = isMoving ? animStep * 32 : 32;

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

          // MMORPG Micro HP Bar above head
          const maxHp = npc.max_hp || 100;
          const currentHp = Math.max(0, Math.min(npc.hp ?? 100, maxHp));
          const hpPct = currentHp / maxHp;
          const hpBarW = 32;
          const hpBarH = 4;
          const hpBarX = px;
          const hpBarY = py - 7;

          ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
          ctx.fillRect(hpBarX - 1, hpBarY - 1, hpBarW + 2, hpBarH + 2);
          ctx.fillStyle = hpPct > 0.5 ? '#22c55e' : hpPct > 0.25 ? '#eab308' : '#ef4444';
          ctx.fillRect(hpBarX, hpBarY, hpBarW * hpPct, hpBarH);

          // Activity Speech Bubble above HP Bar
          const initials = npc.name
            .split(' ')
            .map((w) => w[0])
            .join('');

          ctx.fillStyle = '#ffffff';
          ctx.strokeStyle = '#334155';
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.roundRect(px - 12, py - 24, 56, 15, 3);
          ctx.fill();
          ctx.stroke();

          // Tail
          ctx.beginPath();
          ctx.moveTo(px + 12, py - 9);
          ctx.lineTo(px + 16, py - 6);
          ctx.lineTo(px + 20, py - 9);
          ctx.fillStyle = '#ffffff';
          ctx.fill();

          ctx.fillStyle = '#0f172a';
          ctx.font = 'bold 8px system-ui';
          ctx.textAlign = 'left';
          ctx.fillText(`${initials}:`, px - 8, py - 13);

          // Activity Icon
          let icon = '💬';
          const act = npc.current_activity.toLowerCase();
          if (act.includes('fight') || act.includes('boss') || act.includes('crypt') || act.includes('skeleton')) icon = '⚔️';
          else if (act.includes('loot') || act.includes('vault') || act.includes('chest')) icon = '💰';
          else if (act.includes('ale') || act.includes('toast') || act.includes('tavern')) icon = '🍺';
          else if (act.includes('heal') || act.includes('holy')) icon = '✨';
          else if (act.includes('sleep') || act.includes('rest')) icon = '💤';
          else if (act.includes('march') || act.includes('bridge')) icon = '🛡️';

          ctx.font = '8px system-ui';
          ctx.fillText(icon, px + 20, py - 13);

          // Name & MMORPG Class / Level Tag below character
          ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
          ctx.fillRect(px - 18, py + 34, 68, 22);
          ctx.fillStyle = isSelected ? '#38bdf8' : '#f8fafc';
          ctx.font = 'bold 9px system-ui';
          ctx.textAlign = 'center';
          ctx.fillText(npc.name.split(' ')[0], px + 16, py + 44);

          // Class Tag
          ctx.fillStyle = '#38bdf8';
          ctx.font = '8px system-ui';
          ctx.fillText(`Lv.${npc.level || 1} ${npc.rpg_class || 'Hero'}`, px + 16, py + 53);
          ctx.textAlign = 'left';
        }
      }

      // 4. Draw Foreground Layer (Roofs, tree canopies for depth sorting)
      const activeFore = themeImages.current.fore;
      if (activeFore && activeFore.complete) {
        ctx.drawImage(activeFore, 0, 0);
      }

      // 5. Dungeon Ambient Darkness & Torchlight System
      // Sector X >= 110 tiles (3520px) is the Subterranean Dungeon
      const dungeonStartX = 110 * 32;
      ctx.save();
      // Dungeon Darkness Mask
      ctx.fillStyle = 'rgba(10, 5, 20, 0.55)';
      ctx.fillRect(dungeonStartX, 0, 4480 - dungeonStartX, 3200);

      // Glowing Torch Light Radii at Dungeon Brazier points & around adventurers in dungeon
      const torchLocations = [
        [114 * 32 + 16, 47 * 32 + 16],
        [114 * 32 + 16, 53 * 32 + 16],
        [124 * 32 + 16, 71 * 32 + 16],
        [132 * 32 + 16, 71 * 32 + 16],
        [124 * 32 + 16, 85 * 32 + 16],
        [132 * 32 + 16, 85 * 32 + 16],
        [128 * 32, 78 * 32], // Boss summon altar
      ];

      if (state?.npcs) {
        for (const npc of state.npcs) {
          if (npc.x >= 110) {
            torchLocations.push([npc.x * 32 + 16, npc.y * 32 + 16]);
          }
        }
      }

      for (const [tx, ty] of torchLocations) {
        const rad = 65 + Math.sin(Date.now() / 200 + tx) * 5;
        const grad = ctx.createRadialGradient(tx, ty, 5, tx, ty, rad);
        grad.addColorStop(0, 'rgba(254, 215, 170, 0.45)');
        grad.addColorStop(0.5, 'rgba(239, 68, 68, 0.18)');
        grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(tx, ty, rad, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();

      // 6. Day / Night & Weather Atmospheric Lighting
      if (state?.clock) {
        const hour = state.clock.sim_hour;
        let overlayColor = 'rgba(0, 0, 0, 0)';

        if (hour >= 21 || hour < 5) {
          overlayColor = 'rgba(15, 23, 42, 0.42)';
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
  }, [pan, zoom, state, selectedNpcId, mapTheme]);

  // Click on canvas to select NPC or Location
  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    const worldPx = (mouseX - pan.x) / zoom;
    const worldPy = (mouseY - pan.y) / zoom;
    const worldTileX = worldPx / 32;
    const worldTileY = worldPy / 32;

    // Check if clicked an NPC
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

  // Zoom directly to specific fantasy landmark
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
          <span>Chronicle Callouts</span>
        </button>
        <span className="text-slate-600">|</span>
        <button
          onClick={() => zoomToSector(44, 45)}
          className="hover:text-white text-slate-400 underline"
        >
          Reset View
        </button>
      </div>

      {/* MMORPG Sector Quick Jump Bookmarks */}
      <div className="absolute top-4 left-4 bg-slate-900/90 backdrop-blur-md px-3 py-2 rounded-xl border border-slate-700/60 shadow-xl text-xs text-slate-300 flex items-center space-x-2 z-10 overflow-x-auto max-w-[85vw]">
        <span className="font-bold text-slate-400 uppercase text-[10px] tracking-wider whitespace-nowrap">Realm Sectors:</span>
        <button
          onClick={() => zoomToSector(44, 20)}
          className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition whitespace-nowrap"
        >
          🛡️ Guild Hall
        </button>
        <button
          onClick={() => zoomToSector(20, 22)}
          className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition whitespace-nowrap"
        >
          🍺 Dragon's Flagon
        </button>
        <button
          onClick={() => zoomToSector(41, 40)}
          className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition whitespace-nowrap"
        >
          ⛲ Town Square
        </button>
        <button
          onClick={() => zoomToSector(18, 48)}
          className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition whitespace-nowrap"
        >
          🔨 Ironforge
        </button>
        <button
          onClick={() => zoomToSector(66, 48)}
          className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition whitespace-nowrap"
        >
          🧪 Arcane Sanctum
        </button>
        <button
          onClick={() => zoomToSector(19, 74)}
          className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition whitespace-nowrap"
        >
          ⚔️ Hero Arena
        </button>
        <button
          onClick={() => zoomToSector(83, 50)}
          className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition whitespace-nowrap"
        >
          🌉 Stone Bridge
        </button>
        <button
          onClick={() => zoomToSector(100, 50)}
          className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition whitespace-nowrap"
        >
          🌲 Whispering Forest
        </button>
        <button
          onClick={() => zoomToSector(115, 50)}
          className="px-2 py-1 rounded-lg bg-purple-950 hover:bg-purple-900 text-purple-200 border border-purple-700 transition whitespace-nowrap"
        >
          💀 Dungeon Gate
        </button>
        <button
          onClick={() => zoomToSector(128, 79)}
          className="px-2 py-1 rounded-lg bg-rose-950 hover:bg-rose-900 text-rose-200 border border-rose-700 transition whitespace-nowrap"
        >
          🔥 Abyssal Boss
        </button>
      </div>

      {/* Map Theme Toggle & Kenney Urban Tileset Info */}
      <div className="absolute top-4 right-4 bg-slate-900/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-700/60 shadow-xl text-xs text-slate-300 flex items-center space-x-2 z-10">
        <span className="font-bold text-slate-400 uppercase text-[10px] tracking-wider">Map Style:</span>
        <button
          onClick={() => setMapTheme(mapTheme === 'the_ville' ? 'kenney_urban' : 'the_ville')}
          className="flex items-center space-x-1 px-2.5 py-1 rounded-lg border font-semibold text-xs transition bg-indigo-600/30 text-indigo-300 border-indigo-500/60 shadow-inner"
          title="Toggle fantasy characters & urban sprite styles"
        >
          <span>{mapTheme === 'the_ville' ? '⚔️ Fantasy RPG' : '🏙️ Kenney Urban'}</span>
        </button>
        <button
          onClick={() => setIsTilesetModalOpen(true)}
          className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs transition flex items-center space-x-1"
          title="Inspect Kenney RPG Tileset Atlas"
        >
          <span>📦 Kenney Pack</span>
        </button>
      </div>

      {/* Stanford Generative Agents Magnified Callout Boxes (MMORPG Fantasy Themed!) */}
      {showCallouts && (
        <>
          {/* Callout 1: Guild Hall Expedition Briefing */}
          <div
            className="absolute top-20 left-64 w-84 bg-slate-900/95 backdrop-blur-md border-2 border-sky-500/70 rounded-2xl shadow-2xl p-3 z-10 text-slate-100 transition-all hover:scale-105 cursor-pointer"
            onClick={() => zoomToSector(44, 20)}
          >
            <div className="flex items-center justify-between pb-1.5 border-b border-slate-800 mb-2">
              <span className="font-bold text-xs text-sky-400 flex items-center space-x-1">
                <span>🛡️</span>
                <span>Expedition Council at Adventurer's Guild</span>
              </span>
              <span className="text-[10px] text-slate-400 font-mono">Guild Hall</span>
            </div>
            <div className="bg-slate-950/70 p-2.5 rounded-xl border border-slate-800/80 font-mono text-[11px] space-y-1 text-slate-300">
              <p className="text-indigo-300">
                <span className="font-bold text-white">[Sir Arthur]:</span> "Clara, ensure the Vanguard has enough holy blessings. The Crypt awaits."
              </p>
              <p className="text-pink-300">
                <span className="font-bold text-white">[Clara]:</span> "The Light protects us, Commander. My staff of renewal is ready."
              </p>
            </div>
          </div>

          {/* Callout 2: Shadow Crypts Boss Encounter */}
          <div
            className="absolute bottom-16 right-96 w-88 bg-slate-900/95 backdrop-blur-md border-2 border-rose-500/70 rounded-2xl shadow-2xl p-3 z-10 text-slate-100 transition-all hover:scale-105 cursor-pointer"
            onClick={() => zoomToSector(128, 79)}
          >
            <div className="flex items-center justify-between pb-1.5 border-b border-slate-800 mb-2">
              <span className="font-bold text-xs text-rose-400 flex items-center space-x-1">
                <span>🔥</span>
                <span>Confronting the Abyssal Overlord</span>
              </span>
              <span className="text-[10px] text-slate-400 font-mono">Floor 3 - Sanctum</span>
            </div>
            <div className="bg-slate-950/70 p-2.5 rounded-xl border border-slate-800/80 font-mono text-[11px] space-y-1 text-slate-300">
              <p className="text-red-400">
                <span className="font-bold text-white">[Tamara]:</span> "Raise your shields! The Dragon is channeling void fire!"
              </p>
              <p className="text-amber-300">
                <span className="font-bold text-white">[Wolfgang]:</span> "I will counter with Meteor Storm! Stand firm, Crimson Dawn!"
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
