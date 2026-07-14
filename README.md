# Habitly — RPG Habit Tracker

Aplikacja webowa do śledzenia nawyków z mechanikami gry RPG (XP, rangi, streaki, osiągnięcia). Projekt inżynierski realizowany w Django.

---

## Opis projektu

Habitly to system zarządzania nawykami, który zamienia codzienną rutynę w grę. Użytkownik tworzy zadania różnych typów, wykonuje je, zdobywa punkty doświadczenia i awansuje przez 5 rang — od Nowicjusza do Legendy.

Celem projektu jest zbadanie, czy mechaniki gamifikacji znane z gier RPG mogą zwiększać motywację do utrzymywania nawyków.

---

## Stack technologiczny

| Warstwa | Technologia |
|---|---|
| Backend | Python 3.12, Django 5.x |
| Baza danych | SQLite (development), PostgreSQL (produkcja) |
| Frontend | HTML5, CSS3 (vanilla, bez frameworków), JavaScript (vanilla) |
| Autoryzacja | Django Auth (sesje, CSRF) |
| Deployment | Railway / Render (planowany) |

Decyzja o budowie frontendu bez Bootstrap/Tailwind była świadoma — system stylów oparty na CSS Custom Properties (oklch color tokens, design tokens, glassmorphism) został zaprojektowany i zaimplementowany od zera.

---

## Aktualny stan projektu

### Zaimplementowane funkcjonalności

**System zadań**
- Trzy typy zadań z odrębną logiką:
  - `DAILY` — zadania codzienne ze streakm (licznik dni z rzędu) i bonusami za 7 i 30 dni
  - `WEEKLY` — zadania tygodniowe z progiem wykonań (`weekly_target`) i tygodniowym streakm
  - `ONCE` — zadania jednorazowe z datą wykonania
- Operacje CRUD (tworzenie, odczyt, usuwanie) — edycja w toku
- Oznaczanie zadań jako wykonanych z natychmiastową aktualizacją UI (AJAX, bez przeładowania strony)

**Gamifikacja**
- System XP: +10 (ONCE), +15 (DAILY), +25 (WEEKLY)
- Bonusy za streaki: +20 XP przy 7-dniowym streak, +50 XP przy 30-dniowym
- 5 rang z progami XP: Nowicjusz (0), Adept (200), Wojownik (500), Mistrz (1000), Legenda (2000)
- Pasek postępu XP w sidebarze aktualizowany w czasie rzeczywistym

**Interfejs użytkownika**
- Dashboard z postępem dnia, statystykami i listą zadań
- Strona Nawyki — zarządzanie zadaniami (dodawanie, usuwanie, color picker)
- Kalendarz misji — grid miesięczny z oznaczeniem dni aktywności, lista zadań po kliknięciu w dzień
- Profil użytkownika — statystyki, podział nawyków, dni z aktywnością
- Landing page z sekcjami marketingowymi i animacjami scroll-reveal
- Tryb jasny/ciemny (toggle, stan w localStorage)

**Backend / architektura**
- Rejestracja i logowanie (Django Auth)
- Model `TaskLog` — log wykonanych zadań (podstawa kalendarza i statystyk)
- Model `TaskNote` — notatki do zadań (backend gotowy, UI w toku)
- Model `UserProfile` — XP, rangi, metody `rank()`, `rank_progress_percent()`, `xp_to_next_rank()`
- Zabezpieczenia: `@login_required`, CSRF na wszystkich formularzach i żądaniach AJAX, filtrowanie zasobów po `user=request.user`
- Post/Redirect/Get na operacjach modyfikujących dane

**Testy**
- Test regresyjny IDOR w `toggle_task` — weryfikuje że użytkownik nie może modyfikować zadań innego użytkownika

---

### Znane ograniczenia / w toku

| # | Element | Status |
|---|---|---|
| 1 | Edycja zadania (brak Update w CRUD) | Do implementacji |
| 2 | UI dla notatek do zadań | Do implementacji |
| 3 | Rozszerzenie testów (modele, XP, streaki) | W toku |
| 4 | Deployment (Railway/Render, `DEBUG=False`, env vars) | Planowany |
| 5 | Osiągnięcia (odznaki) | Planowany |
| 6 | Strony błędów 404/500 | Planowany |

---

## Planowane funkcjonalności (do końca projektu)

### Priorytet wysoki
- **Edycja zadań** — modal z wypełnionymi polami, PUT/PATCH endpoint
- **UI notatek** — panel notatek do każdego zadania (backend `TaskNote` już gotowy)
- **Rozszerzone testy** — testy jednostkowe logiki streaków, XP, rang; testy widoków autoryzacji
- **Deployment** — konfiguracja produkcyjna, zmienna `SECRET_KEY` z env, `collectstatic`, hosting

### Priorytet średni
- **System osiągnięć** — odznaki za progi XP, streak 7/30 dni, liczbę ukończonych zadań
- **Statystyki rozszerzone** — wykres aktywności w czasie (heatmapa lub wykres liniowy)
- **Strony błędów** — custom 404/500 w stylu aplikacji

### Priorytet niski / exploratory
- **Sugestie AI** — propozycje nawyków na podstawie historii
- **PWA** — tryb offline, ikona na ekranie głównym

---

## Struktura projektu

```
ToDoDjango/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── ToDoDjango/          # konfiguracja projektu (settings, urls główne)
└── ToDo/                # główna aplikacja
    ├── models.py        # Task, TaskLog, TaskNote, UserProfile
    ├── views.py         # widoki (auth, dashboard, nawyki, kalendarz, profil, notatki)
    ├── urls.py          # routing aplikacji
    ├── forms.py         # TaskForm, RegisterForm
    ├── tests.py         # testy
    ├── templates/ToDo/  # szablony HTML
    └── static/
        ├── css/         # main.css, habbits.css, calendar.css, profile.css, home.css, auth.css
        └── js/          # base.js, main.js, habbits.js, calendar.js
```

---

## Uruchomienie lokalne

### Opcja 1 — Docker (zalecana, nie wymaga Pythona)

Wymagania: [Docker Desktop](https://www.docker.com/products/docker-desktop/)

```bash
git clone <repo>
cd DjangoApp
docker compose up --build
```

Aplikacja dostępna pod `http://localhost:8000`

### Opcja 2 — Python lokalnie

```bash
git clone <repo>
cd DjangoApp
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Aplikacja dostępna pod `http://127.0.0.1:8000/`

---

## Uruchamianie testów

```bash
python manage.py test ToDo
```

---

## Dokumentacja do pracy inżynierskiej

Artefakty przygotowywane równolegle:
- [ ] Diagram ERD (modele i relacje)
- [ ] Opis architektury systemu
- [ ] Uzasadnienie decyzji projektowych (wybór Django, vanilla CSS, model TaskLog)
- [ ] Screenshoty UI

---

*Projekt realizowany jako praca inżynierska.*