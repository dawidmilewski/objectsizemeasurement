import { useState } from "react";

const PALETTE = ["#ff4d94", "#38bdf8", "#4ade80", "#facc15", "#c084fc", "#fb923c"];

export default function Plot2DModal({ objects, arucoSize, onClose }) {
  const [hiddenIds, setHiddenIds] = useState([]);

  const toggleObject = (id) => {
    setHiddenIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const allPoints = [
    [0, 0],
    [arucoSize, 0],
    [arucoSize, arucoSize],
    [0, arucoSize],
  ];

  objects.forEach((obj) => {
    if (!hiddenIds.includes(obj.id)) {
      allPoints.push(...obj.pelny_hull_cm, ...obj.czworokat_cm, ...obj.prostokat_cm);
    }
  });

  const xs = allPoints.map((p) => p[0]);
  const ys = allPoints.map((p) => p[1]);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);

  const svgWidth = 760;
  const svgHeight = 520;
  const pad = 56;

  const spanX = Math.max(maxX - minX, 1);
  const spanY = Math.max(maxY - minY, 1);
  const scale = Math.min((svgWidth - pad * 2) / spanX, (svgHeight - pad * 2) / spanY);

  const offsetX = (svgWidth - spanX * scale) / 2 - minX * scale;
  const offsetY = (svgHeight - spanY * scale) / 2 - minY * scale;
  const mapPt = ([x, y]) => [x * scale + offsetX, y * scale + offsetY];
  const mapPolygon = (pts) => pts.map(mapPt).map((p) => `${p[0]},${p[1]}`).join(" ");

  const arucoRect = [
    [0, 0],
    [arucoSize, 0],
    [arucoSize, arucoSize],
    [0, arucoSize],
  ];

  const gridStep = Math.max(1, Math.round(Math.max(spanX, spanY) / 10));
  const xTicks = [];
  for (let x = Math.floor(minX / gridStep) * gridStep; x <= maxX + gridStep; x += gridStep) {
    xTicks.push(x);
  }
  const yTicks = [];
  for (let y = Math.floor(minY / gridStep) * gridStep; y <= maxY + gridStep; y += gridStep) {
    yTicks.push(y);
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card modal-wide" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h2>Wizualizacja Wymiarów 2D</h2>
            <p className="modal-subtitle">
              Analiza zrzutowanych kształtów w układzie metrycznym [cm] (proporcje osi 1:1)
            </p>
          </div>
          <button className="btn-icon" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="plot-layout">
          <div className="plot-canvas-box">
            <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} className="plot-svg">
              {xTicks.map((x) => {
                const [sx] = mapPt([x, 0]);
                return (
                  <g key={`gx-${x}`}>
                    <line
                      x1={sx}
                      y1={pad / 2}
                      x2={sx}
                      y2={svgHeight - pad / 2}
                      stroke="#2a2d3d"
                      strokeDasharray="3 4"
                    />
                    <text
                      x={sx}
                      y={svgHeight - 10}
                      fill="#94a3b8"
                      fontSize="11"
                      textAnchor="middle"
                    >
                      {x}
                    </text>
                  </g>
                );
              })}

              {yTicks.map((y) => {
                const [, sy] = mapPt([0, y]);
                return (
                  <g key={`gy-${y}`}>
                    <line
                      x1={pad / 2}
                      y1={sy}
                      x2={svgWidth - pad / 2}
                      y2={sy}
                      stroke="#2a2d3d"
                      strokeDasharray="3 4"
                    />
                    <text x={14} y={sy + 4} fill="#94a3b8" fontSize="11">
                      {y}
                    </text>
                  </g>
                );
              })}

              <polygon
                points={mapPolygon(arucoRect)}
                fill="rgba(59, 130, 246, 0.12)"
                stroke="#3b82f6"
                strokeWidth="2"
                strokeDasharray="6 4"
              />

              {objects.map((obj, idx) => {
                if (hiddenIds.includes(obj.id)) return null;
                const color = PALETTE[idx % PALETTE.length];
                return (
                  <g key={obj.id}>
                    <polygon
                      points={mapPolygon(obj.pelny_hull_cm)}
                      fill="none"
                      stroke={color}
                      strokeWidth="1.8"
                      strokeDasharray="2 3"
                    />
                    <polygon
                      points={mapPolygon(obj.czworokat_cm)}
                      fill={`${color}22`}
                      stroke={color}
                      strokeWidth="2.6"
                    />
                    <polygon
                      points={mapPolygon(obj.prostokat_cm)}
                      fill="none"
                      stroke={color}
                      strokeWidth="1.2"
                      strokeDasharray="6 4"
                      opacity="0.7"
                    />
                  </g>
                );
              })}
            </svg>
          </div>

          <div className="plot-legend">
            <h3>Legenda warstw</h3>
            <div className="legend-item static">
              <span className="swatch dashed-blue" />
              <span>ArUco ({arucoSize} × {arucoSize} cm)</span>
            </div>
            <div className="legend-styles">
              <span>• Kropkowana: Pełna otoczka</span>
              <span>— Ciągła: Czworokąt</span>
              <span>- - Przerywana: minAreaRect</span>
            </div>
            <div className="legend-objects">
              {objects.map((obj, idx) => {
                const color = PALETTE[idx % PALETTE.length];
                const isHidden = hiddenIds.includes(obj.id);
                return (
                  <button
                    key={obj.id}
                    className={`legend-toggle ${isHidden ? "muted" : ""}`}
                    onClick={() => toggleObject(obj.id)}
                  >
                    <span className="dot" style={{ backgroundColor: color }} />
                    <span>
                      Obiekt {idx + 1} ({obj.dlugosc_cm.toFixed(1)} × {obj.szerokosc_cm.toFixed(1)} cm)
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}