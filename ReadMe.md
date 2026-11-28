# Pomiar Wizyjny Obiektów 2D

Aplikacja wspomagająca pomiary geometrii fizycznej na podstawie pojedynczego zdjęcia z kamery. Projekt stanowi część praktyczną pracy inżynierskiej.

System wykorzystuje znacznik referencyjny ArUco do wyliczania macierzy homografii i przeliczania pikseli na rzeczywiste współrzędne w centymetrach. W zależności od scenariusza testowego stosowane są znaczniki ArUco o bokach 5.0 cm lub 12.0 cm.

## Uruchomienie backendu

Wymagania: Python 3.10+, Node.js 18+ (wymagany wyłącznie do jednorazowego zbudowania interfejsu).

1. Sklonuj repozytorium na dysk lokalny.
2. Zainstaluj zależności backendu (w głównym folderze projektu):
   pip install -r requirements.txt
3. Zbuduj statyczną paczkę interfejsu webowego (jednorazowo):
   cd frontend
   npm install
   npm run build
   cd ..
4. Uruchom serwer aplikacji:
   python backend/api.py
5. Otwórz aplikację w przeglądarce pod adresem `http://127.0.0.1:8000` (interaktywna dokumentacja API Swagger UI: `http://127.0.0.1:8000/docs`).

## Struktura Projektu

Aplikacja została zrealizowana w architekturze klient–serwer z wyraźnym rozdzieleniem logiki obliczeniowej od warstwy sieciowej i prezentacji:

* `backend/core_math.py` – matematyczny silnik rzutowania. Zawiera autorską implementację wyznaczania macierzy homografii, przeliczania punktów z dzieleniem perspektywicznym oraz obliczania długości odcinków (NumPy).
* `backend/vision.py` – moduł przetwarzania obrazu w OpenCV. Realizuje detekcję znacznika ArUco z precyzją subpikselową oraz ekstrakcję otoczek wypukłych obiektów (filtr Gaussa, progowanie adaptacyjne, maskowanie znacznika, domknięcie morfologiczne).
* `backend/measurement.py` – analityka kształtów i algorytm decyzyjny. Rzutuje wierzchołki otoczki na centymetry, przeprowadza aproksymację wielokątną (`approxPolyDP`) z regułą 90% oraz rzutowanie odwrotne na piksele.
* `backend/image_utils.py` – dekodowanie strumienia bajtów, ograniczanie rozdzielczości obrazu (maks. 3200 px) oraz kodowanie podglądu w Base64.
* `backend/schemas.py` – modele danych Pydantic definiujące strukturę odpowiedzi JSON.
* `backend/measurement_service.py` – warstwa usługowa łącząca przetwarzanie obrazu z modelami odpowiedzi API.
* `backend/routes.py` – definicja punktów końcowych REST API (`/api/health`, `/api/check-aruco`, `/api/analyze`), walidacja plików i obsługa błędów HTTP.
* `backend/api.py` – punkt startowy serwera FastAPI (konfiguracja CORS, rejestracja tras i serwowanie zbudowanego frontendu przez `StaticFiles`).
* `frontend/` – interfejs webowy (React + Vite) odpowiedzialny za wgrywanie zdjęć, nakładkę wektorową SVG, podgląd szczegółów krawędzi oraz wykres metryczny 2D.

## Model Logiki i Filtrowanie

System operuje na hybrydowym potoku detekcyjnym i pomiarowym:

1. Ekstrakcja danych (`vision.py`): Filtr Gaussa wygładza teksturę tła i niweluje szum matrycy. Następnie progowanie adaptacyjne dokonuje binaryzacji w lokalnych oknach, co zapobiega gubieniu krawędzi przy nierównomiernym oświetleniu i cieniach. Wykryte kontury są filtrowane i zamykane otoczką wypukłą.
2. Decyzja pomiarowa (`measurement.py`): Wierzchołki otoczki wypukłej są rzutowane na płaszczyznę rzeczywistą i przybliżane czworokątem. Jeżeli czworokąt pokrywa co najmniej 90% pola otoczki (np. banknot, dokument), wymiary wyznaczane są jako średnie długości naprzeciwległych boków. W przeciwnym razie (obiekty okrągłe lub nieregularne, np. moneta, kluczyk) stosowana jest obwiednia `minAreaRect`.

## Dokumentacja Zdjęć Testowych

Folder testowy zawiera zbiór wyselekcjonowanych scenariuszy badających skuteczność algorytmów oraz fizyczne ograniczenia modelu homografii.

Model matematyczny zakłada, że wszystkie obserwowane płaszczyzny leżą na poziomie Z = 0 (bezpośrednio na blacie). Rozbieżności między wynikami pomiarów a wartościami rzeczywistymi służą badaniu wpływu błędu paralaksy, grubości przedmiotów oraz ekstrapolacji punktów.

### Dane laboratoryjne (grafika wygenerowana cyfrowo, znacznik ArUco 5.0 cm):
* `test_idealny_matematyczny.png` – Zielony prostokąt mierzony idealnie z góry. Wymiary rzeczywiste: 27.4 cm x 21.0 cm.
* `test_syntetyczny_kat_30st.png` – Identyczny zielony prostokąt wygenerowany z rzutu o kącie pochylenia 30 stopni.
* `test_idealny_matematyczny2.png` – Czerwony prostokąt referencyjny o zadanych wymiarach 25.0 cm x 19.0 cm (weryfikacja precyzji w środowisku bez zniekształceń optycznych obiektywu).

### Dane rzeczywiste (przedmioty z życia codziennego):
* Moneta 1 Euro (`IMG_0511.jpeg`) – Obiekt okrągły testujący przełączenie na `minAreaRect`. Średnica rzeczywista: 2.325 cm.
* Pendrive SanDisk (`IMG_0517.jpeg`, `IMG_0519.jpeg`) – Wymiar rzeczywisty: 6.0 cm x 2.0 cm.
* Czarny magnes (`IMG_0532.jpeg`, `IMG_0533.jpeg`) – Wymiar rzeczywisty: 7.8 cm x 5.8 cm.
* Magnes Ciechanowiec (`IMG_0532.jpeg`, `IMG_0533.jpeg`) – Wymiar rzeczywisty: 7.9 cm x 5.3 cm.
* Wizytówka DJ – Wymiar rzeczywisty: 9.0 cm x 5.0 cm.
* Banknot 100 zł (`IMG_0555.jpeg`) – Płaski obiekt z nadrukiem testujący filtry. Wymiar rzeczywisty: 13.8 cm x 6.9 cm.
* Kluczyk samochodowy (`IMG_2620.jpeg`, `IMG_2624.jpeg`) – Obiekt nieregularny testujący regułę 90%. Wymiar rzeczywisty: 8.4 cm x 4.0 cm.

### Weryfikacja błędu paralaksy:
* Tablet iPad (`IMG_0738.jpeg`, `IMG_0739.jpeg`) – Obiekt o dużej powierzchni i wyraźnej grubości w etui (25.0 cm x 19.0 cm). Położenie blisko krawędzi kadru w dużej odległości od małego znacznika generuje kilkucentymetrowy błąd, dokumentując ograniczenia optyki smartfonowej. Zastosowanie większego znacznika (12.0 cm) i mniejszego pochylenia aparatu znacząco redukuje błąd pomiarowy.