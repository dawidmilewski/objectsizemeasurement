# Vision Metrology - Pomiar Wizyjny Obiektów 2D

Aplikacja wspomagająca pomiary geometrii fizycznej w oparciu o widzenie komputerowe z pojedynczej kamery. Projekt stanowi część praktyczną pracy inżynierskiej. 

System wykorzystuje znacznik referencyjny ArUco do wyliczania macierzy homografii i dynamicznego mapowania pikseli na przestrzeń płaską w centymetrach. W zależności od środowiska testowego, na zdjęciach jako obiekt referencyjny stosowane są kalibratory ArUco o bokach 5.0 cm lub 12.0 cm.

## Uruchomienie programu

Środowisko: Python 3.10+

1. Sklonuj repozytorium na dysk lokalny.
2. Zainstaluj wymagane zależności projektowe, wykonując komendę w terminalu:
   pip install -r requirements.txt
3. Uruchom skrypt główny aplikacji:
   python main.py
4. W interfejsie podaj rzeczywisty wymiar boku wydrukowanego znacznika ArUco (np. 5.0 lub 12.0), wczytaj zdjęcie i kliknij "Rozpocznij Wykrywanie".

## Struktura Plików Aplikacji

Architektura oprogramowania została zbudowana z zachowaniem separacji warstw:

* main.py – Kontroler łączący logikę z widokiem. Odpowiada za wielowątkowość procesu, rzutowanie wizualizacji wyników bezpośrednio na ekran analizy oraz za wbudowany moduł generowania interaktywnych wykresów w Matplotlib.
* gui.py – Warstwa interfejsu użytkownika (UI). Zbudowana za pomocą biblioteki CustomTkinter. Obsługuje zdarzenia myszy i klawiatury (m.in. funkcje Pan & Zoom dla wczytanych obrazów) oraz dynamiczne zarządzanie listą wyników w panelu bocznym.
* vision.py – Moduł przetwarzania obrazu i detekcji. Realizuje ekstrakcję obiektów z tła przy użyciu rozmycia Gaussa, progowania adaptacyjnego oraz operacji morfologicznych. Moduł wykrywa znacznik ArUco z precyzją subpikselową, co jest kluczowe dla redukcji błędów kalibracyjnych. Wykorzystano bibliotekę OpenCV
* measurement.py – Analityka kształtów i algorytm decyzyjny. Transformuje zbiory pikseli w  punkty w rzeczywistej przestrzeni. Odpowiada za weryfikację geometrii obiektów poprzez algorytm approxPolyDP i dynamiczny wybór ostatecznej metody pomiarowej.
* core_math.py – Matematyczny silnik rzutowania. Zawiera autorską implementację układu równań. Rozwiązuje macierz homografii wykorzystywaną do obustronnego rzutowania punktów pomiędzy przestrzenią ekranu (piksele) a układem rzeczywistym (centymetry).

## Model Logiki i Filtrowanie

System operuje na hybrydowym potoku detekcyjnym i pomiarowym:

1. Ekstrakcja danych (vision.py): W pierwszej kolejności filtr Gaussa wygładza teksturę otoczenia i niweluje ziarno matrycy aparatu. Następnie progowanie adaptacyjne dokonuje binaryzacji obrazu poprzez analizę lokalnych sąsiedztw pikseli, co zapobiega gubieniu krawędzi obiektów przy nierównomiernym, domowym oświetleniu. Całość zamykana jest otoczką wypukłą, która sprowadza detaliczny kształt do uogólnionego geometrycznie wielokąta.
2. Decyzja Pomiarowa (measurement.py): Zamiast nakładania standardowej obwódki minAreaRect, która potęguje błędy wymiarowe przy dystorsji obiektywu, utworzono autorską logikę weryfikacji. Otoczka wypukła jest przyblizana do postaci czworokąta. Jeżeli wygenerowany czworokąt pokrywa minimum 90% pola badanej otoczki (np. banknot, dokument), ostateczny wymiar stanowi uśredniona długość naprzeciwległych fizycznych boków tego czworokąta, omijając przekłamania kątowe obiektywu. Gdy warunek 90% nie zostaje spełniony (np. dla obiektów okrągłych lub bardzo nieregularnych jak kluczyk/pendrive), system używa rzutu opisanego z obwódki minAreaRect jako zabezpieczenia.

## Dokumentacja Zdjęć Testowych

Folder testowy zawiera zbiór wyselekcjonowanych scenariuszy, badających skuteczność algorytmów oraz prezentujących fizyczne ograniczenia wykorzystania macierzy homografii. 

Model matematyczny aplikacji zakłada, że wszystkie obserwowane płaszczyzny spoczywają w przestrzeni Z = 0 (bezpośrednio na blacie). Rozbieznosc między wynikiem z aplikacji a poniższymi wartościami faktycznymi służy badaniu wpływu błędu paralaksy, grubości fizycznej przedmiotów oraz ekstrapolacji punktów.

### Dane laboratoryjne (grafika wygenerowana cyfrowo, znacznik ArUco 5.0 cm):
* test_idealny_matematyczny.png – Zielony prostokąt mierzony idealnie z góry. Wymiary rzeczywiste: 27.4 cm x 21.0 cm.
* test_syntetyczny_kat_30st.png – Identyczny zielony prostokąt, jednak wygenerowany z rzutu o kącie pochylenia 30 stopni. 
W testach laboratoryjnych wykorzystano również czerwony, wbudowany matematycznie prostokąt referencyjny, którego wymiary docelowe i zadane do pomiarów to 26.1 cm x 19.5 cm. Testy te weryfikują ścisłą efektywność w środowisku izolowanym od zniekształceń optycznych obiektywu.

### Dane rzeczywiste (przedmioty z życia codziennego):
* Moneta 1 Euro (IMG_0511.jpeg) – Obiekt poddawany weryfikacji algorytmu decyzyjnego dla przedmiotów okrągłych. Wymiar rzeczywisty: średnica 2.325 cm. 
* Pendrive SanDisk (IMG_0517.jpeg, IMG_0519.jpeg) – Wymiar rzeczywisty: 6.0 cm x 2.0 cm.
* Czarny magnes (IMG_0532.jpeg, IMG_0533.jpeg) – Wymiar rzeczywisty: 7.8 cm x 5.8 cm.
* Magnes Ciechanowiec (IMG_0532.jpeg, IMG_0533.jpeg) – Wymiar rzeczywisty: 7.9 cm x 5.3 cm.
* Wizytówka DJ – Wymiar rzeczywisty: 9.0 cm x 5.0 cm.
* Banknot 100 zł (IMG_0555.jpeg) – Obiekt referencyjny płaski z nadrukiem testującym filtry. Wymiar rzeczywisty: 13.8 cm x 6.9 cm.
* Kluczyk samochodowy (IMG_2620.jpeg, IMG_2624.jpeg) – Obiekt nieregularny testujący skrajnie aproksymację czworokąta i uruchomienie minAreaRect. Wymiar rzeczywisty: 8.4 cm x 4.0 cm.

### Weryfikacja błędu paralaksy:
* Tablet iPad (IMG_0738.jpeg, IMG_0739.jpeg) – Obiekt o dużej powierzchni brzegowej i wyraźnej grubości w etui. Położenie na krawędzi kadru z dużym odstępem od znacznika wymusza potężną ekstrapolację macierzy, generując kilkucentymetrowy niedomiar optyczny. Wymiar rzeczywisty urządzenia w pokrowcu: 25.0 cm x 19.0 cm. Przypadek dokumentuje ograniczenia optyki smartfonowej (brak telecentryczności) i wymóg stosowania ulepszonych algorytmów kalibracji matrycy przy zaawansowanych systemach. Ilustruje to też istotę dostosowania wielkości znacznika do obiektu. W przypadku zdjęć ze znacznikiem wielkośći 12cm błąd pomiarowy malał.
