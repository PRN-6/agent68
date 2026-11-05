import React, { useMemo, useEffect, useState } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MarkerType,
} from '@xyflow/react';
import type { Node, Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useSimulationStore } from '../store/simulationStore';

export const SocialGraphView: React.FC = () => {
  const { state, setSelectedNpcId } = useSimulationStore();
  const [graphData, setGraphData] = useState<{ nodes: any[]; edges: any[] }>({
    nodes: [],
    edges: [],
  });

  useEffect(() => {
    fetch('/api/social/graph')
      .then((res) => res.json())
      .then((data) => setGraphData(data))
      .catch((err) => console.error('Error fetching social graph:', err));
  }, [state?.clock.tick]);

  // Arrange 25 NPCs around an organic circle / clusters
  const nodes: Node[] = useMemo(() => {
    if (!graphData.nodes || graphData.nodes.length === 0) return [];
    const count = graphData.nodes.length;
    const radius = 380;
    const centerX = 500;
    const centerY = 450;

    return graphData.nodes.map((n, idx) => {
      const angle = (idx / count) * 2 * Math.PI;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);

      return {
        id: n.id,
        position: { x, y },
        data: { label: n.name, ...n },
        style: {
          background: '#1e293b',
          color: '#f8fafc',
          border: `2px solid ${n.color || '#3b82f6'}`,
          borderRadius: '12px',
          padding: '8px 12px',
          fontSize: '11px',
          fontWeight: '600',
          boxShadow: '0 4px 14px rgba(0,0,0,0.4)',
          width: 140,
          textAlign: 'center',
          cursor: 'pointer',
        },
      };
    });
  }, [graphData.nodes]);

  const edges: Edge[] = useMemo(() => {
    if (!graphData.edges) return [];
    return graphData.edges.map((e) => {
      let stroke = '#64748b';
      if (e.type === 'Close Friend') stroke = '#10b981';
      else if (e.type === 'Friend') stroke = '#06b6d4';
      else if (e.type === 'Rival') stroke = '#f43f5e';

      return {
        id: e.id,
        source: e.source,
        target: e.target,
        animated: e.type === 'Close Friend',
        style: {
          stroke,
          strokeWidth: Math.max(1.5, Math.min(e.familiarity / 18, 5)),
          opacity: 0.75,
        },
        label: `${e.type} (${Math.round(e.trust)}%)`,
        labelStyle: { fill: '#cbd5e1', fontSize: 9, fontWeight: 500 },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: stroke,
        },
      };
    });
  }, [graphData.edges]);

  const onNodeClick = (_: any, node: Node) => {
    setSelectedNpcId(node.id);
  };

  return (
    <div className="w-full h-full bg-slate-950 relative">
      {/* Legend */}
      <div className="absolute top-4 left-4 z-10 bg-slate-900/90 backdrop-blur-md p-3 rounded-xl border border-slate-800 shadow-xl text-xs space-y-1.5 text-slate-300">
        <h4 className="font-bold text-slate-100 text-[11px] uppercase tracking-wider mb-2">
          Social Ties Legend
        </h4>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-1 bg-emerald-500 rounded"></span>
          <span>Close Friend (High Trust & Affinity)</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-1 bg-cyan-500 rounded"></span>
          <span>Friend (Positive rapport)</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-1 bg-slate-400 rounded"></span>
          <span>Acquaintance (Casual familiar tie)</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-1 bg-rose-500 rounded"></span>
          <span>Rival / Conflict (Divergent goals)</span>
        </div>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodeClick={onNodeClick}
        fitView
        className="bg-slate-950"
      >
        <Background color="#334155" gap={20} size={1} />
        <Controls className="bg-slate-900 border-slate-700 text-slate-200" />
      </ReactFlow>
    </div>
  );
};
