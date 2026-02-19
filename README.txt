# Habitly

Habitly to aplikacja webowa typu Habit Tracker, umożliwiająca zarządzanie nawykami,
monitorowanie postępów oraz budowanie systematyczności poprzez mechanizm streaków
i analizę tygodniowej aktywności użytkownika.

---

## Cel projektu

Celem projektu jest zaprojektowanie i implementacja aplikacji webowej,
która pozwala użytkownikowi:

- dodawać zadania (jednorazowe, dzienne, tygodniowe),
- oznaczać zadania jako ukończone,
- śledzić serie wykonanych dni (streak),
- analizować postęp dzienny i tygodniowy,
- zarządzać swoim kontem użytkownika.

Projekt skupia się na połączeniu przejrzystego interfejsu użytkownika
z logiką backendową.

---

## 🛠echnologie

### Backend
- Python
- Django

### Frontend
- HTML5
- CSS3
- JavaScript

## Architektura systemu

Projekt oparty jest o architekturę MVT (Model–View–Template),
zgodnie ze standardem frameworka Django.

Główne moduły aplikacji:

- Model zadania (typ: once / daily / weekly)
- System streaków
- Mechanizm obliczania postępu dziennego
- Widok tygodniowy aktywności

Warstwa frontendowa odpowiada za interaktywność interfejsu,
natomiast logika biznesowa realizowana jest po stronie backendu.

---

## Funkcjonalności (aktualny stan)

- Dodawanie zadań
- Oznaczanie zadań jako ukończone
- System streaków
- Widok tygodniowy
- Podgląd zadań typu once w kalendarzu (http://127.0.0.1:8000/calendar/)

---

## Struktura projektu





---

## Uruchomienie projektu

1. Klonowanie repozytorium:
   git clone <adres_repo>

2. Instalacja zależności:
   pip install -r requirements.txt

3. Migracje bazy danych:
   python manage.py migrate

4. Uruchomienie serwera:
   python manage.py runserver

---

## Plan dalszego rozwoju

- Rozbudowa systemu statystyk
- Implementacja wykresów aktywności
- Personalizacja użytkownika
- Wdrożenie aplikacji na serwer produkcyjny
- Statystyki długoterminowe
- Dashboard użytkownika



