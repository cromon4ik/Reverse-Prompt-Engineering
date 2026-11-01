# Raport analizy, implementacji i testów

## 1. Zauważone zmiany między wersją A a widoczną częścią wersji B

| Obszar | Wersja A | Wersja B (widoczny fragment) / rekonstrukcja |
|---|---|---|
| Zależności | Tylko standardowy Python | `numpy` do obliczeń tablicowych; `csv` do eksportu |
| Dane | Lista słowników | Oddzielna tablica nazw i macierz statystyk `N×4` typu float |
| Wagi | Wzór z wagami 0.1, 2, 1.5, 1 | Wektor wag `[0.20, 0.40, 0.25, 0.15]` |
| Wynik siły | Bezpośredni wzór na surowych statystykach | Normalizacja min-max każdej kolumny, następnie iloczyn macierzy i wag |
| Walidacja | Brak | Kontrola wymiarów, liczby postaci, unikatowości nazw, skończoności i nieujemności danych |
| Kolumna stała | Nie dotyczy | Normalizacja zwraca zera; brak dzielenia przez zero |
| Ranking | Jedna najlepsza postać | Pełny ranking malejący, stabilne sortowanie |
| Role | Brak | Klasyfikacja na podstawie ataku/szybkości oraz HP/obrony |
| Pojedynki | Brak | Macierz prawdopodobieństw oparta na funkcji logistycznej |
| Średnie szanse | Brak | Średnia z wiersza macierzy pojedynków dla każdej postaci |
| Eksport | Brak | CSV z separatorem `;`, UTF-8 BOM, miejscem, nazwą, rolą, siłą i szansą |
| Testowanie | Brak | Testy normalizacji, kolumn stałych, pojedynków, walidacji i stabilnego rankingu |

## 2. Kolejność przebudowy

1. Przeniesienie danych do tablic NumPy bez zmiany wartości.
2. Walidacja danych i bezpieczna normalizacja.
3. Wektorowe obliczanie ważonej siły oraz stabilny ranking.
4. Klasyfikacja ról przez maski logiczne.
5. Symulacja pojedynków przez broadcasting i wyliczenie średnich szans.
6. Filtrowanie oraz statystyki opisowe.
7. Raport i eksport CSV.
8. Testy regresyjne i integracyjne.

## 3. Weryfikacja wymagań

| Wymaganie | Działa? | Dowód / test |
|---|---|---|
| Dane w tablicy nazw i macierzy NumPy | Tak | `NAZWY.shape == (8,)`, `STATYSTYKI.shape == (8, 4)` |
| Zachowanie oryginalnych statystyk | Tak | W macierzy są wszystkie wartości z wersji A |
| Walidacja wymiarów i liczby postaci | Tak | `waliduj()` zgłasza `ValueError` dla błędnego kształtu i mniej niż 2 postaci |
| Walidacja nazw unikatowych | Tak | Kontrola `set(nazwy.tolist())` |
| Walidacja wartości | Tak | `np.isfinite` oraz `dane < 0` |
| Normalizacja min-max | Tak | Test `np.testing.assert_allclose` dla kolumn zmiennych |
| Kolumna stała bez dzielenia przez zero | Tak | Test oczekuje `[0, 0]` w kolumnie stałej |
| Wynik ważony NumPy | Tak | `normalizuj(dane) @ WAGI` |
| Stabilny ranking | Tak | Test remisu: kolejność indeksów pozostaje wejściowa |
| Role | Tak | `np.select` z priorytetem Szturmowca przed Obrońcą |
| Macierz pojedynków | Tak | Test przekątnej 0.5 i `M + M.T == 1` |
| Średnie szanse wygranej | Tak | `np.mean(macierz, axis=1)` |
| Filtrowanie | Tak | Funkcja zwraca indeksy według progu 0.5 i opcjonalnej roli |
| Statystyki | Tak | Min, max, średnia dla każdej kolumny i średnia siła |
| Eksport CSV | Tak | `ranking_postaci.csv`, separator `;`, UTF-8 BOM, 5 kolumn i 8 rekordów |
| Raport konsolowy | Tak | `main()` drukuje role, ranking, statystyki, filtr i szanse |

## 4. Dwie rzeczywiste korekty / przypadki brzegowe do udokumentowania

**Korekta 1 — stała kolumna.** Prosta normalizacja `(dane-min)/(max-min)` zawodzi, gdy dana statystyka ma identyczną wartość u wszystkich postaci. Rozwiązanie: dzielenie przez `np.divide` z `out=np.zeros_like(...)` i `where=rozpietosc != 0`. Test wymusza wynik `[0, 0]` dla stałej kolumny.

**Korekta 2 — symetria pojedynków i format CSV.** Sama funkcja logistyczna nie ustawia jawnie przekątnej, a standardowy domyślny separator CSV może być niewygodny w polskim Excelu. Rozwiązanie: jawne `np.fill_diagonal(wynik, 0.5)` oraz zapis z `encoding="utf-8-sig"`, `newline=""`, `delimiter=";"`. Test sprawdza `M + M.T == 1`, a plik wynikowy należy otworzyć i sprawdzić liczbę kolumn oraz rekordów.

## 5. Ograniczenie porównania

W wiadomości źródłowej pełny kod `02_kod_docelowy.py` nie był widoczny — fragment kończył się po `ranking = np.argsort(-sila, kind="stable")` z informacją o 35 dalszych liniach. Dlatego nie da się uczciwie potwierdzić dokładnych progów filtrowania, treści raportu ani nazwy pliku CSV w brakującej części B. W implementacji przyjęto i opisano jawnie próg filtra 0.5 oraz nazwę `ranking_postaci.csv`. Aby wykazać pełną zgodność 1:1 z B, trzeba porównać te szczegóły z kompletnym plikiem nauczyciela.
