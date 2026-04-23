import React, { useEffect, useState, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import axios from 'axios';

const GraphVisualizer = () => {
  const [graphData,  setGraphData]  = useState({ nodes: [], links: [] });
  const [loading,    setLoading]    = useState(true);
  const [error,      setError]      = useState(null);
  const containerRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 550 });

  useEffect(() => {
    axios.get('http://127.0.0.1:8001/api/v1/graph/visualize')
      .then(res => {
        setGraphData(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Graph fetch error:', err);
        setError('Could not load graph data. Is the backend running on port 8001?');
        setLoading(false);
      });

    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width:  containerRef.current.offsetWidth,
          height: 550
        });
      }
    };
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  if (error) {
    return (
      <div className="bg-slate-900 rounded-xl h-[550px] flex items-center justify-center text-red-400 text-sm">
        {error}
      </div>
    );
  }

  return (
    <div
      className="bg-slate-900 rounded-xl overflow-hidden shadow-inner border border-slate-700 relative"
      ref={containerRef}
    >
      {/* Legend */}
      <div className="absolute top-4 left-4 z-10 bg-slate-800/90 p-3 rounded-lg text-xs text-white border border-slate-600 backdrop-blur">
        <h4 className="font-bold mb-2 border-b border-slate-500 pb-1">Graph Legend</h4>
        <div className="flex items-center gap-2 mb-1">
          <div className="w-3 h-3 rounded-full bg-blue-500"/>
          <span>University Course</span>
        </div>
        <div className="flex items-center gap-2 mb-1">
          <div className="w-3 h-3 rounded-full bg-teal-400"/>
          <span>Taught Skill</span>
        </div>
        <div className="mt-2 pt-2 border-t border-slate-600 text-slate-400">
          {graphData.nodes.length} nodes • {graphData.links.length} edges
        </div>
      </div>

      {/* Stats overlay */}
      <div className="absolute top-4 right-4 z-10 bg-slate-800/90 p-2 rounded-lg text-xs text-slate-300 border border-slate-600">
        Drag to explore • Scroll to zoom
      </div>

      {loading ? (
        <div className="h-[550px] flex items-center justify-center text-slate-400">
          <div className="text-center">
            <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-3"/>
            Loading Graph Physics...
          </div>
        </div>
      ) : graphData.nodes.length > 0 ? (
        <ForceGraph2D
          width={dimensions.width}
          height={dimensions.height}
          graphData={graphData}
          nodeRelSize={1}
          linkColor={() => 'rgba(255,255,255,0.15)'}
          linkWidth={1}
          backgroundColor="#0f172a"
          d3VelocityDecay={0.3}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const label    = node.id;
            const isCourse = node.group === 'Course';
            const fontSize = (isCourse ? 13 : 9) / globalScale;
            ctx.font = `${isCourse ? 'bold ' : ''}${fontSize}px Sans-Serif`;

            const textWidth     = ctx.measureText(label).width;
            const bckgDimensions = [textWidth + fontSize * 0.4, fontSize * 1.4];

            // Background pill
            ctx.fillStyle = isCourse ? 'rgba(37,99,235,0.85)' : 'rgba(15,23,42,0.75)';
            ctx.beginPath();
            ctx.roundRect(
              node.x - bckgDimensions[0] / 2,
              node.y - bckgDimensions[1] / 2,
              bckgDimensions[0],
              bckgDimensions[1],
              3
            );
            ctx.fill();

            ctx.textAlign    = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle    = isCourse ? '#bfdbfe' : '#2dd4bf';
            ctx.fillText(label, node.x, node.y);

            node.__bckgDimensions = bckgDimensions;
          }}
          nodePointerAreaPaint={(node, color, ctx) => {
            ctx.fillStyle = color;
            const b = node.__bckgDimensions;
            b && ctx.fillRect(
              node.x - b[0] / 2,
              node.y - b[1] / 2,
              b[0], b[1]
            );
          }}
        />
      ) : (
        <div className="h-[550px] flex items-center justify-center text-slate-400">
          No graph data available
        </div>
      )}
    </div>
  );
};

export default GraphVisualizer;
