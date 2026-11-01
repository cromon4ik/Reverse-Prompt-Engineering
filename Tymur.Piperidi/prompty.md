# Prompty prowadzące od wersji A do analizatora RPG

> Każdy prompt należy wysłać osobno, w podanej kolejności, w nowej rozmowie z modelem. Na początku rozmowy należy przekazać wyłącznie plik `01_kod_poczatkowy.py`. Nie wolno przekazywać modelowi wersji docelowej ani jej fragmentów.

## Prompt 1 — zmiana reprezentacji danych i zależności

Przebuduj dane wejściowe programu tak, aby można było wykonywać obliczenia wektorowo. Użyj biblioteki NumPy. Nazwy postaci przechowuj w jednowymiarowej tablicy `NAZWY`, a ich cztery statystyki (HP, atak, obrona, szybkość) w dwuwymiarowej tablicy `STATYSTYKI` typu `float`, gdzie każdy wiersz odpowiada jednej postaci, a kolejność kolumn jest stała i udokumentowana. Zachowaj wszystkie 8 postaci i ich oryginalne wartości. Zdefiniuj osobną tablicę wag `[0.20, 0.40, 0.25, 0.15]` oraz nazwy kolumn. Na tym etapie nie usuwaj danych ani nie zmieniaj wartości. Kryterium: `STATYSTYKI.shape == (8, 4)`, `NAZWY.shape == (8,)`, wszystkie pierwotne wartości są zachowane, a NumPy jest rzeczywiście używane.

## Prompt 2 — walidacja danych i normalizacja min-max

Dodaj funkcję `waliduj(nazwy, dane)`, która zgłasza `ValueError`, jeśli dane nie są macierzą o dokładnie czterech kolumnach i liczbie wierszy równej liczbie nazw, jeśli jest mniej niż 2 postacie, jeśli nazwy się powtarzają albo jeśli statystyki zawierają wartości ujemne, NaN lub nieskończoność. Dodaj funkcję `normalizuj(dane)`, która normalizuje każdą kolumnę niezależnie metodą min-max do zakresu 0–1. Obsłuż kolumnę stałą: zwróć w niej same zera i nie dopuść do dzielenia przez zero. Użyj operacji NumPy z `axis=0` i `np.divide` z maską `where`. Kryterium: przetestuj zwykłe dane, kolumnę stałą, dane ujemne i nie-skończone.

## Prompt 3 — ważony wynik siły i ranking

Dodaj funkcję `oblicz_sile(dane)`, która wykorzystuje wynik normalizacji i mnożenie macierzy przez wektor wag `[0.20, 0.40, 0.25, 0.15]`. Nie wracaj do pętli obliczających wynik osobno dla każdej postaci. Wynik ma być jednowymiarową tablicą NumPy o długości równej liczbie postaci i mieścić się w zakresie 0–1. W `main()` wyznacz ranking malejąco według siły za pomocą `np.argsort(-sila, kind="stable")`, aby zachować kolejność wejściową przy remisie. Wypisz wynik i ranking z czterema miejscami po przecinku. Kryterium: kształt wyniku, zakres wartości i stabilność remisów.

## Prompt 4 — automatyczne przypisywanie ról

Dodaj funkcję `okresl_role(dane)`, która przypisuje role na podstawie wektorowych masek logicznych. Postać jest „Szturmowcem”, gdy atak >= 35 i szybkość >= 12. W przeciwnym razie jest „Obrońcą”, gdy HP >= 120 i obrona >= 18. Pozostałe postacie otrzymują rolę „Wszechstronny”. Użyj `np.select`, a nie pętli po postaciach. Zachowaj kolejność priorytetów: warunek ofensywny ma pierwszeństwo, gdyby oba warunki były spełnione. Kryterium: funkcja zwraca tablicę tekstową o długości liczby postaci; sprawdź co najmniej po jednym przykładzie każdej roli i przypadek spełniający oba warunki.

## Prompt 5 — macierz pojedynków i średnie szanse

Dodaj funkcję `macierz_pojedynkow(sila)`. Dla każdej uporządkowanej pary postaci oblicz prawdopodobieństwo zwycięstwa pierwszej nad drugą wzorem logistycznym `1 / (1 + exp(-8 * (sila_i - sila_j)))`. Zastosuj broadcasting NumPy, np. `sila[:, None] - sila[None, :]`; nie używaj zagnieżdżonych pętli. Ustaw przekątną macierzy na 0.5, ponieważ postać remisuje sama ze sobą. W `main()` oblicz średnią szansę wygranej każdej postaci jako średnią z jej wiersza. Kryterium: macierz ma rozmiar N×N, przekątna wynosi 0.5, a dla każdej pary `P(i,j) + P(j,i) == 1`.

## Prompt 6 — filtrowanie i statystyki zbioru

Dodaj funkcję filtrującą postacie według minimalnej siły oraz opcjonalnej roli. Przyjmij domyślny próg siły 0.5; funkcja ma zwracać indeksy pasujących postaci i działać na maskach NumPy, bez ręcznego przepisywania rekordów. W raporcie pokaż postacie spełniające próg. Dodaj statystyki każdej kolumny: minimum, maksimum i średnią, a także liczbę postaci i średnią siłę. Kryterium: filtr nie modyfikuje danych źródłowych, poprawnie zwraca pusty wynik, gdy nic nie pasuje, i pozwala dodatkowo ograniczyć wynik do wybranej roli.

## Prompt 7 — eksport CSV i raport konsolowy

Dodaj eksport rankingu do pliku `ranking_postaci.csv`. Użyj modułu `csv`, kodowania `utf-8-sig`, `newline=""` i separatora średnikowego `;`, aby plik poprawnie otwierał się w polskim Excelu. Nagłówki: `Miejsce`, `Postać`, `Rola`, `Siła`, `Średnia szansa wygranej`. Zapisuj rekordy w kolejności rankingu; siłę formatuj do 4 miejsc po przecinku, a średnią szansę jako procent z 2 miejscami. Raport konsolowy ma czytelnie prezentować role, siłę, ranking, statystyki, wyniki filtrowania i średnie szanse. Kryterium: CSV zawiera nagłówek i dokładnie jeden wiersz na postać, ranking w pliku jest malejący, polskie znaki są zachowane.

## Prompt 8 — testy, integracja i odporność

Dodaj funkcję `testy()` uruchamianą przed właściwą analizą. Użyj `np.testing.assert_allclose` do sprawdzenia normalizacji kolumn zmiennych i stałych. Sprawdź macierz pojedynków: przekątna 0.5 oraz symetria dopełniająca (`M + M.T == 1`). Dodaj testy odrzucania błędnych danych przez walidację oraz stabilności rankingu przy równych wynikach. Upewnij się, że wszystkie funkcje są wywoływane w logicznej kolejności w `main()`, a program można uruchomić bez argumentów. Nie zmieniaj danych źródłowych. Uruchom program i popraw wszystkie błędy. Kryterium: program kończy się kodem 0, drukuje raport i tworzy poprawny CSV.

---

## Dwie korekty promptów po testach

1. **Korekta po teście kolumny stałej (Prompt 2):** jeśli pierwsza implementacja dzieliła przez `max-min` bez obsługi zera, dopisz: „Nie używaj zwykłego dzielenia dla całej macierzy. Wykorzystaj `np.divide(..., out=np.zeros_like(...), where=rozpietosc != 0)`. Dodaj test, w którym co najmniej jedna kolumna ma identyczną wartość we wszystkich wierszach; wynik tej kolumny musi wynosić dokładnie zero i nie może pojawić się ostrzeżenie o dzieleniu przez zero.”

2. **Korekta po teście pojedynków/CSV (Prompty 5 i 7):** jeśli model pominął remis postaci z samą sobą lub zapisał CSV przecinkami, dopisz: „Po obliczeniu macierzy jawnie ustaw przekątną na 0.5 i sprawdź `np.allclose(M + M.T, 1.0)`. Przy eksporcie użyj `encoding='utf-8-sig'`, `newline=''` oraz `delimiter=';'`; po zapisie odczytaj plik ponownie przez `csv.reader` i sprawdź, że nagłówek ma pięć pól, a liczba rekordów danych jest równa liczbie postaci.”

> Uwaga dokumentacyjna: w przekazanym materiale kod wersji B jest ucięty po wyznaczeniu rankingu. Próg filtra 0.5 oraz szczegóły raportu w tym projekcie są jawnie przyjętymi wymaganiami rekonstrukcji, a nie potwierdzonymi odczytem brakujących linii B.
