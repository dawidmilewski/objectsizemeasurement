export default function DetailsModal({ object, onClose }) {
  if (!object) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Szczegóły — Obiekt {object.displayIndex}</h2>
          <button className="btn-icon" onClick={onClose}>
            ✕
          </button>
        </div>
        <p className="method-badge">
          {object.metoda === "czworokat"
            ? "Uśredniony czworokąt (wymiar pokrywa >90% kształtu)"
            : "minAreaRect (kształt nieregularny, obwiednia)"}
        </p>
        <div className="edges-box">
          <h3>Długości krawędzi</h3>
          <ul>
            {object.boki_otoczki_cm.map((bok, idx) => (
              <li key={idx}>
                <span>Bok {idx + 1}</span>
                <strong>{bok.toFixed(2)} cm</strong>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}