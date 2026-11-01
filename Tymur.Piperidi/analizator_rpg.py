"""Wektorowy analizator balansu postaci RPG z wykorzystaniem NumPy."""

import csv
import numpy as np

NAZWY = np.array([
    "Wojownik", "Mag", "Łucznik", "Paladyn", "Łotrzyk",
    "Berserker", "Druid", "Strażnik"
])

# Kolumny: HP, atak, obrona, szybkość
STATYSTYKI = np.array([
    [120, 28, 18, 9],
    [75, 44, 6, 13],
    [95, 34, 10, 17],
    [140, 25, 22, 7],
    [80, 39, 8, 21],
    [110, 42, 7, 12],
    [105, 26, 15, 14],
    [155, 18, 26, 5],
], dtype=float)

WAGI = np.array([0.20, 0.40, 0.25, 0.15])
KOLUMNY = ("HP", "Atak", "Obrona", "Szybkość")
PLIK_CSV = "ranking_postaci.csv"


def waliduj(nazwy, dane):
    """Sprawdza strukturę i poprawność danych wejściowych."""
    nazwy = np.asarray(nazwy)
    dane = np.asarray(dane)
    if dane.ndim != 2 or dane.shape != (len(nazwy), 4):
        raise ValueError("Każda postać musi mieć dokładnie 4 statystyki.")
    if len(nazwy) < 2:
        raise ValueError("Potrzeba co najmniej dwóch postaci.")
    if len(set(nazwy.tolist())) != len(nazwy):
        raise ValueError("Nazwy postaci muszą być unikatowe.")
    if not np.all(np.isfinite(dane)) or np.any(dane < 0):
        raise ValueError("Statystyki muszą być nieujemnymi, skończonymi liczbami.")
    if WAGI.shape != (4,) or not np.isclose(np.sum(WAGI), 1.0):
        raise ValueError("Wagi muszą zawierać cztery wartości sumujące się do 1.")


def normalizuj(dane):
    """Normalizacja min-max osobno dla każdej kolumny."""
    dane = np.asarray(dane, dtype=float)
    minimum = np.min(dane, axis=0)
    rozpietosc = np.ptp(dane, axis=0)
    # Dla stałej kolumny zwracamy same zera (bez dzielenia przez zero).
    return np.divide(
        dane - minimum,
        rozpietosc,
        out=np.zeros_like(dane, dtype=float),
        where=rozpietosc != 0,
    )


def oblicz_sile(dane):
    """Wylicza wynik ważony na podstawie znormalizowanych statystyk."""
    return normalizuj(dane) @ WAGI


def okresl_role(dane):
    """Nadaje role na podstawie progów statystyk; ofensywa ma pierwszeństwo."""
    ofensywa = (dane[:, 1] >= 35) & (dane[:, 3] >= 12)
    obrona = (dane[:, 0] >= 120) & (dane[:, 2] >= 18)
    return np.select(
        [ofensywa, obrona],
        ["Szturmowiec", "Obrońca"],
        default="Wszechstronny",
    )


def macierz_pojedynkow(sila):
    """Zwraca prawdopodobieństwo wygranej postaci i z każdą inną postacią."""
    roznice = sila[:, None] - sila[None, :]
    wynik = 1 / (1 + np.exp(-8 * roznice))
    np.fill_diagonal(wynik, 0.5)
    return wynik


def filtruj_postacie(sila, role, minimalna_sila=0.5, rola=None):
    """Filtruje postacie po minimalnym wyniku i opcjonalnie po nazwie roli."""
    maska = sila >= minimalna_sila
    if rola is not None:
        maska &= role == rola
    return np.flatnonzero(maska)


def zapisz_csv(sciezka, nazwy, role, sila, srednie_szanse, ranking):
    """Zapisuje ranking w CSV z separatorem średnikowym i UTF-8 BOM."""
    with open(sciezka, "w", encoding="utf-8-sig", newline="") as plik:
        pisarz = csv.writer(plik, delimiter=";")
        pisarz.writerow([
            "Miejsce", "Postać", "Rola", "Siła", "Średnia szansa wygranej"
        ])
        for miejsce, indeks in enumerate(ranking, start=1):
            pisarz.writerow([
                miejsce,
                nazwy[indeks],
                role[indeks],
                f"{sila[indeks]:.4f}",
                f"{srednie_szanse[indeks]:.2%}",
            ])


def testy():
    """Testy jednostkowe obliczeń i przypadków brzegowych."""
    przyklad = np.array([
        [10, 20, 30, 40],
        [10, 50, 60, 40]
    ], dtype=float)
    wynik = normalizuj(przyklad)
    np.testing.assert_allclose(wynik[:, 0], [0, 0])
    np.testing.assert_allclose(wynik[:, 1], [0, 1])
    np.testing.assert_allclose(wynik[:, 3], [0, 0])

    proby = macierz_pojedynkow(np.array([0.1, 0.6, 0.9]))
    assert np.allclose(np.diag(proby), 0.5)
    assert np.allclose(proby + proby.T, 1.0)

    # Walidacja odrzuca dane niepoprawne.
    try:
        waliduj(np.array(["A", "B"]), np.array([[1, 2, 3, 4], [1, -1, 3, 4]]))
    except ValueError:
        pass
    else:
        raise AssertionError("Ujemna statystyka powinna zostać odrzucona.")

    # Wyniki są ograniczone do [0, 1], a sortowanie jest stabilne.
    rowne = np.array([0.5, 0.5, 0.2])
    assert np.argsort(-rowne, kind="stable").tolist() == [0, 1, 2]


def main():
    waliduj(NAZWY, STATYSTYKI)
    testy()

    sila = oblicz_sile(STATYSTYKI)
    role = okresl_role(STATYSTYKI)
    ranking = np.argsort(-sila, kind="stable")

    pojedynki = macierz_pojedynkow(sila)
    srednie_szanse = np.mean(pojedynki, axis=1)

    print("=== ANALIZA BALANSU POSTACI RPG ===")
    print("\nWyniki siły:")
    for indeks in ranking:
        print(f"{NAZWY[indeks]} ({role[indeks]}): {sila[indeks]:.4f}")

    print("\nRanking postaci:")
    for miejsce, indeks in enumerate(ranking, start=1):
        print(f"{miejsce}. {NAZWY[indeks]} — siła {sila[indeks]:.4f}")

    print("\nStatystyki zbioru:")
    print(f"Liczba postaci: {len(NAZWY)}")
    for numer, kolumna in enumerate(KOLUMNY):
        print(
            f"{kolumna}: min={np.min(STATYSTYKI[:, numer]):.2f}, "
            f"max={np.max(STATYSTYKI[:, numer]):.2f}, "
            f"średnia={np.mean(STATYSTYKI[:, numer]):.2f}"
        )
    print(f"Średnia siła: {np.mean(sila):.4f}")

    print("\nPostacie spełniające filtr siły >= 0.5:")
    wybrane = filtruj_postacie(sila, role, minimalna_sila=0.5)
    if len(wybrane):
        for indeks in wybrane[np.argsort(-sila[wybrane], kind="stable")]:
            print(f"- {NAZWY[indeks]} ({role[indeks]}): {sila[indeks]:.4f}")
    else:
        print("Brak postaci spełniających kryterium.")

    print("\nŚrednie szanse wygranej:")
    for indeks in ranking:
        print(f"{NAZWY[indeks]}: {srednie_szanse[indeks]:.2%}")

    zapisz_csv(PLIK_CSV, NAZWY, role, sila, srednie_szanse, ranking)
    print(f"\nZapisano ranking do pliku: {PLIK_CSV}")


if __name__ == "__main__":
    main()
