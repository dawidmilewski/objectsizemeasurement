export default function Sidebar({
  loading,
  arucoInput,
  onArucoInputChange,
  arucoFound,
  objects,
  onUploadClick,
  onAnalyze,
  onOpenChart,
  onShowDetails,
  onDeleteObject,
}) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-dot" />
        <div>
          <h1>Pomiar Wizyjny</h1>
          <span>System pomiaru 2D z ArUco</span>
        </div>
      </div>

      <section className="panel-section">
        <h2>1. Kalibracja</h2>
        <button className="btn btn-primary" disabled={loading} onClick={onUploadClick}>
          Wczytaj obraz
        </button>

        <label className="field-label">
          Fizyczny rozmiar znacznika [cm]
          <input
            type="text"
            className="text-input"
            value={arucoInput}
            onChange={(e) => onArucoInputChange(e.target.value)}
          />
        </label>
      </section>

      <section className="panel-section">
        <h2>2. Analiza Obrazu</h2>
        <button
          className="btn btn-accent"
          disabled={loading || !arucoFound}
          onClick={onAnalyze}
        >
          {loading ? "Analizowanie..." : "Rozpocznij wykrywanie"}
        </button>
      </section>

      <section className="panel-section results-section">
        <h2>3. Wyniki i Wykresy</h2>
        <button
          className="btn btn-secondary"
          disabled={objects.length === 0}
          onClick={onOpenChart}
        >
          Pokaż interaktywny wykres 2D
        </button>

        <div className="results-list">
          {objects.length === 0 ? (
            <div className="empty-state">Brak wykrytych obiektów</div>
          ) : (
            objects.map((obj, idx) => (
              <div key={obj.id} className="result-card">
                <div className="result-info">
                  <strong>Obiekt {idx + 1}</strong>
                  <span>Długość: {obj.dlugosc_cm.toFixed(2)} cm</span>
                  <span>Szerokość: {obj.szerokosc_cm.toFixed(2)} cm</span>
                </div>
                <div className="result-actions">
                  <button
                    className="btn-small btn-outline"
                    onClick={() => onShowDetails({ ...obj, displayIndex: idx + 1 })}
                  >
                    Szczegóły
                  </button>
                  <button
                    className="btn-small btn-danger"
                    onClick={() => onDeleteObject(obj.id)}
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </section>
    </aside>
  );
}