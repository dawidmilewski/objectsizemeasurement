const API_URL = "http://localhost:8000/api";

export async function checkAruco(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_URL}/check-aruco`, {
    method: "POST",
    body: formData,
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "Błąd wczytywania obrazu.");
  }
  return data;
}

export async function analyzeImage(file, bokCm) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("bok_cm", bokCm.toString());

  const res = await fetch(`${API_URL}/analyze`, {
    method: "POST",
    body: formData,
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "Błąd analizy obrazu.");
  }
  return data;
}