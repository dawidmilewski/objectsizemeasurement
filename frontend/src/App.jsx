import { useState, useRef } from "react";
import "./App.css";
import { checkAruco, analyzeImage } from "./services/api";
import { useZoomPan } from "./hooks/useZoomPan";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import ImageCanvas from "./components/ImageCanvas";
import DetailsModal from "./components/DetailsModal";
import Plot2DModal from "./components/Plot2DModal";

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [imageSrc, setImageSrc] = useState(null);
  const [imgSize, setImgSize] = useState({ width: 0, height: 0 });
  const [arucoPoints, setArucoPoints] = useState(null);
  const [arucoInput, setArucoInput] = useState("5.0");
  const [arucoSizeUsed, setArucoSizeUsed] = useState(5.0);
  const [objects, setObjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState(
    "Wczytaj zdjęcie ze znacznikiem ArUco, aby rozpocząć."
  );
  const [errorMessage, setErrorMessage] = useState(null);
  const [detailsObject, setDetailsObject] = useState(null);
  const [showChart, setShowChart] = useState(false);

  const fileInputRef = useRef(null);
  const {
    zoom,
    pan,
    stageRef,
    resetView,
    applyZoom,
    handleWheel,
    handleMouseDown,
    handleMouseMove,
    handleMouseUp,
  } = useZoomPan();

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    setObjects([]);
    setErrorMessage(null);
    setLoading(true);
    setStatusMessage("Wczytywanie obrazu i wyszukiwanie znacznika ArUco...");
    resetView();

    try {
      const data = await checkAruco(file);
      setImageSrc(data.image_base64);
      setImgSize({ width: data.width, height: data.height });
      setArucoPoints(data.punkty_aruco);

      if (data.aruco_found) {
        setStatusMessage("Wykryto znacznik ArUco. Możesz rozpocząć analizę obiektów.");
      } else {
        setErrorMessage("Nie wykryto znacznika ArUco na wczytanym zdjęciu.");
        setStatusMessage("Wczytaj inne zdjęcie z wyraźnym znacznikiem ArUco.");
      }
    } catch (err) {
      setErrorMessage(err.message);
      setStatusMessage("Wystąpił błąd podczas komunikacji z serwerem.");
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile || !arucoPoints) return;
    const parsedSize = parseFloat(arucoInput.trim().replace(",", "."));
    if (isNaN(parsedSize) || parsedSize <= 0) {
      setErrorMessage("Podaj poprawny fizyczny rozmiar znacznika w centymetrach.");
      return;
    }

    setErrorMessage(null);
    setLoading(true);
    setStatusMessage("Trwa wykrywanie konturów i przeliczanie wymiarów...");

    try {
      const data = await analyzeImage(selectedFile, parsedSize);
      setArucoPoints(data.punkty_aruco);
      setArucoSizeUsed(data.rozmiar_aruco_cm);
      setObjects(data.obiekty);
      setStatusMessage(`Zakończono analizę. Wykryto obiektów: ${data.obiekty.length}.`);
    } catch (err) {
      setErrorMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteObject = (id) => {
    setObjects((prev) => prev.filter((item) => item.id !== id));
  };

  return (
    <div className="app-shell">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/png,image/jpeg,image/bmp"
        onChange={handleFileChange}
        hidden
      />

      <Sidebar
        loading={loading}
        arucoInput={arucoInput}
        onArucoInputChange={setArucoInput}
        arucoFound={Boolean(arucoPoints)}
        objects={objects}
        onUploadClick={triggerFileInput}
        onAnalyze={handleAnalyze}
        onOpenChart={() => setShowChart(true)}
        onShowDetails={setDetailsObject}
        onDeleteObject={handleDeleteObject}
      />

      <main className="workspace">
        <Topbar
          errorMessage={errorMessage}
          statusMessage={statusMessage}
          imageLoaded={Boolean(imageSrc)}
          zoom={zoom}
          onZoomIn={() => applyZoom(1.25)}
          onZoomOut={() => applyZoom(1 / 1.25)}
          onResetZoom={resetView}
        />

        <ImageCanvas
          stageRef={stageRef}
          imageSrc={imageSrc}
          imgSize={imgSize}
          arucoPoints={arucoPoints}
          objects={objects}
          zoom={zoom}
          pan={pan}
          onUploadClick={triggerFileInput}
          onWheel={handleWheel}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
        />
      </main>

      <DetailsModal object={detailsObject} onClose={() => setDetailsObject(null)} />

      {showChart && (
        <Plot2DModal
          objects={objects}
          arucoSize={arucoSizeUsed}
          onClose={() => setShowChart(false)}
        />
      )}
    </div>
  );
}