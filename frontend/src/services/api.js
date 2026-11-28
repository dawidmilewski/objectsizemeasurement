const API_URL =
  import.meta.env.VITE_API_URL ||
  (window.location.port === "5173" ? "http://localhost:8000/api" : "/api");

async function parseJsonSafe(res) {
  const text = await res.text();
  try {
    return text ? JSON.parse(text) : {};
  } catch {
    return { detail: `Nieoczekiwana odpowiedź serwera (HTTP ${res.status}).` };
  }
}

export async function checkAruco(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_URL}/check-aruco`, { method: "POST", body: formData });
  const data = await parseJsonSafe(res);
  if (!res.ok) throw new Error(data.detail || "Błąd wczytywania obrazu.");
  return data;
}

export async function analyzeImage(file, bokCm) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("bok_cm", bokCm.toString());

  const res = await fetch(`${API_URL}/analyze`, { method: "POST", body: formData });
  const data = await parseJsonSafe(res);
  if (!res.ok) throw new Error(data.detail || "Błąd analizy obrazu.");
  return data;
}