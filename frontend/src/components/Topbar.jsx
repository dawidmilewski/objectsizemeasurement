export default function Topbar({
  errorMessage,
  statusMessage,
  imageLoaded,
  zoom,
  onZoomIn,
  onZoomOut,
  onResetZoom,
}) {
  return (
    <header className="topbar">
      <div className="status-bar">
        {errorMessage ? (
          <span className="badge badge-error">{errorMessage}</span>
        ) : (
          <span className="status-text">{statusMessage}</span>
        )}
      </div>

      <div className="zoom-controls">
        <button className="btn-small btn-outline" disabled={!imageLoaded} onClick={onZoomOut}>
          −
        </button>
        <span className="zoom-value">{Math.round(zoom * 100)}%</span>
        <button className="btn-small btn-outline" disabled={!imageLoaded} onClick={onZoomIn}>
          +
        </button>
        <button className="btn-small btn-outline" disabled={!imageLoaded} onClick={onResetZoom}>
          Reset
        </button>
      </div>
    </header>
  );
}