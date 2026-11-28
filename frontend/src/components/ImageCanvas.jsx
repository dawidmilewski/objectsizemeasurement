import { toSvgPoints, getCentroid } from "../utils/geometry";

export default function ImageCanvas({
  stageRef,
  imageSrc,
  imgSize,
  arucoPoints,
  objects,
  zoom,
  pan,
  onUploadClick,
  onWheel,
  onMouseDown,
  onMouseMove,
  onMouseUp,
}) {
  const strokeBase = imgSize.width ? Math.max(2, imgSize.width / 450) : 2;
  const fontBase = imgSize.width ? Math.max(16, imgSize.width / 45) : 18;

  return (
    <div
      ref={stageRef}
      className={`canvas-stage ${zoom > 1 ? "pannable" : ""}`}
      onWheel={(e) => onWheel(e, Boolean(imageSrc))}
      onMouseDown={onMouseDown}
      onMouseMove={onMouseMove}
      onMouseUp={onMouseUp}
      onMouseLeave={onMouseUp}
    >
      {!imageSrc ? (
        <div className="placeholder" onClick={onUploadClick}>
          <div className="placeholder-icon">⬆</div>
          <p>Kliknij tutaj lub użyj przycisku „Wczytaj obraz”</p>
          <span>Obsługiwane formaty: PNG, JPG, JPEG, BMP</span>
        </div>
      ) : (
        <div
          className="image-layer-wrap"
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
          }}
        >
          <img src={imageSrc} alt="Podgląd pomiaru" draggable={false} className="preview-img" />
          <svg
            className="overlay-svg"
            viewBox={`0 0 ${imgSize.width} ${imgSize.height}`}
            preserveAspectRatio="xMidYMid meet"
          >
            {arucoPoints && (
              <g>
                <polygon
                  points={toSvgPoints(arucoPoints)}
                  fill="rgba(59, 130, 246, 0.15)"
                  stroke="#3b82f6"
                  strokeWidth={strokeBase}
                />
                <text
                  x={arucoPoints[3][0]}
                  y={arucoPoints[3][1] + fontBase}
                  fill="#60a5fa"
                  fontSize={fontBase * 0.9}
                  fontWeight="700"
                >
                  ArUco
                </text>
              </g>
            )}

            {objects.map((obj, idx) => {
              const targetPoly =
                obj.metoda === "czworokat" ? obj.czworokat_px : obj.rogi_prostokata_px;
              const [cx, cy] = getCentroid(targetPoly);

              return (
                <g key={obj.id}>
                  {obj.surowy_hull_px.length > 0 && (
                    <polygon
                      points={toSvgPoints(obj.surowy_hull_px)}
                      fill="none"
                      stroke="#ef4444"
                      strokeWidth={strokeBase * 1.2}
                    />
                  )}
                  <polygon
                    points={toSvgPoints(targetPoly)}
                    fill="rgba(34, 197, 94, 0.12)"
                    stroke="#22c55e"
                    strokeWidth={strokeBase}
                  />
                  <text
                    x={cx}
                    y={cy}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize={fontBase}
                    fontWeight="800"
                    stroke="#000000"
                    strokeWidth={strokeBase * 1.5}
                    paintOrder="stroke"
                    fill="#4ade80"
                  >
                    O {idx + 1}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>
      )}

      {imageSrc && (
        <div className="canvas-legend">
          <div className="canvas-legend-item">
            <span className="legend-line legend-blue" />
            <span>Znacznik ArUco</span>
          </div>
          <div className="canvas-legend-item">
            <span className="legend-line legend-red" />
            <span>Surowa otoczka wypukła</span>
          </div>
          <div className="canvas-legend-item">
            <span className="legend-line legend-green" />
            <span>Dopasowany kształt pomiarowy</span>
          </div>
        </div>
      )}
    </div>
  );
}