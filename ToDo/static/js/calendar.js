let currentYear = new Date().getFullYear();
let currentMonth = new Date().getMonth() + 1;
const today = new Date();
const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;


const WEEKDAYS = ['Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'Sb', 'Nd'];

const MONTHS = ['Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
    'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień'];
function renderCalendar(year, month) {
    const firstDay = new Date(year, month - 1, 1).getDay();
    const daysInMonth = new Date(year, month, 0).getDate();
    const startOffset = (firstDay + 6) % 7;



    let html = `
      <div class="cal-header">
        <span>${MONTHS[month - 1]} ${year}</span>
        <div class="cal-header-nav">
          <button onclick="changeMonth(-1)">‹</button>
          <button onclick="goToday()">Dziś</button>
          <button onclick="changeMonth(1)">›</button>
        </div>
      </div>
      <div class="cal-grid">`;

    // Nagłówki dni tygodnia
    for (const day of WEEKDAYS) {
        html += `<div class="cal-weekday">${day}</div>`;
    }

    // Puste komórki przed 1szym dniem
    for (let i = 0; i < startOffset; i++) {
        html += `<div class="cal-day empty"></div>`;
    }

    // Dni miesiąca - uzupełnij pętlę
    for (let d = 1; d <= daysInMonth; d++) {
        const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(d).padStart(2, '0')}`; // np. "2026-05-01" - użyj year, month, d
        const isToday = dateStr === todayStr;
        html += `<div class="cal-day ${isToday ? 'today' : ''}" data-date="${dateStr}" onclick="loadDayData('${dateStr}')">${d}</div>`;
    }


    html += '</div>';
    document.querySelector('.calendar').innerHTML = html;
}

function changeMonth(dir) {
    currentMonth += dir;
    if (currentMonth > 12) { currentMonth = 1; currentYear++; }
    if (currentMonth < 1)  { currentMonth = 12; currentYear--; }
    renderCalendar(currentYear, currentMonth);
    loadMonthData(currentYear, currentMonth);
}

function goToday() {
    currentYear = new Date().getFullYear();
    currentMonth = new Date().getMonth() + 1;
    renderCalendar(currentYear, currentMonth);
}

document.addEventListener('DOMContentLoaded', function () {
    renderCalendar(currentYear, currentMonth);
    loadMonthData(currentYear, currentMonth);
    loadDayData(todayStr);
});

function loadMonthData(year, month) {
    fetch(`/calendar/month/?year=${year}&month=${month}`)
        .then(r => r.json())
        .then(data => {
            // data to słownik {"2026-06-01": 3, "2026-06-03": 2, ...}
            for (const [dateStr, count] of Object.entries(data)) {
                const dayEl = document.querySelector(`.cal-day[data-date="${dateStr}"]`);
                if (dayEl) {
                    dayEl.innerHTML += `<span class="cal-dot">${count}</span>`;
                }
            }
        });
}


function loadDayData(dateStr) {
    fetch(`/calendar/day/?date=${dateStr}`)
        .then(r => r.json())
        .then(tasks => {
            const section = document.querySelector('.task-list');

            const dateObj = new Date(dateStr + 'T00:00:00');
            const formattedCap = dateObj.toLocaleDateString('pl-PL', { weekday: 'long', day: 'numeric', month: 'long' });
            const completedCount = tasks.filter(t => t.completed).length;


            if (tasks.length === 0) {
                section.innerHTML = `<p>Brak zadań w tym dniu.</p>`;
                return;
            }

            let html = `<h3>${formattedCap}</h3>
                <p>${completedCount} z ${tasks.length} zadań ukończonych</p>`;

            for (const task of tasks) {
                const badge = task.type === 'WEEKLY'
                ? `<span class="badge badge--weekly">Tygodniowe</span>`
                : task.type === 'DAILY'
                    ? `<span class="badge badge--daily">Codzienne</span>`
                    : `<span class="badge badge--once">Jednorazowe</span>`;


                html +=
                    `<div class="habit-card">
                    <div class="habit-card__accent accent-${task.color}"></div>
                    <div class="habit-card__body">
                        <div class="habit-card__title">${task.title}</div>
                        <div class="habit-card__xp">+${task.xp} XP · ${{ 'DAILY': 'Codzienne', 'WEEKLY': 'Tygodniowe', 'ONCE': 'Jednorazowe' }[task.type]}</div>                    </div>
                    <span class="badge">${task.completed 
                        ? `<span class="badge badge--done">✓ ukończone</span>` 
                        : `<span class="badge badge--pending">oczekuje</span>`}
                    </span>
                    </div>`
            }
            section.innerHTML = html;
        });
}






