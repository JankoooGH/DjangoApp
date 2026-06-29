    // Pasek postępu
const CSRF_TOKEN = document.querySelector('.app-content').dataset.csrf;

function toggleTask(taskId, btn) {
    fetch(`/toggle/${taskId}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': CSRF_TOKEN }
    })
    .then(r => r.json())
    .then(data => {
        if (data.status !== 'ok') return;

        const li = btn.closest('li');

        btn.classList.toggle('checked', data.is_done);
        btn.textContent = data.is_done ? '✓' : '';
        li.classList.toggle('my-task--done', data.is_done);

        const titleEl = li.querySelector('.task-title, s.done');
        if (data.is_done) {
            titleEl.outerHTML = `<s class="task-title done">${titleEl.textContent}</s>`;
        } else {
            titleEl.outerHTML = `<span class="task-title">${titleEl.textContent}</span>`;
        }

        // streak dzienny
        const streakEl = li.querySelector('.task-streak');
        if (streakEl && data.streak !== null) {
            streakEl.textContent = `🔥 ${data.streak}`;
        }

        // weekly: postęp i streak osobno
        const progressEl = li.querySelector('.badge-weekly-progress');
        if (progressEl && data.weekly_progress !== null) {
            progressEl.textContent = `Ukończono: ${data.weekly_progress} z ${data.weekly_target}`;
        }
        if (streakEl && data.weekly_streak !== null) {
            streakEl.textContent = `🔥 ${data.weekly_streak}`;
        }

        updateProgressBar(data.day_progress, data.tasks_done, data.tasks_total);
        updateXP(data.xp);
    });
}

function updateProgressBar(progress, done, total) {
    const fill = document.querySelector('.progress-bar-fill');
    const pct = document.getElementById('day-pct-text');
    const count = document.querySelector('.progress-bar-count');
    const msg = document.getElementById('day-message');

    if (fill) fill.style.width = progress + '%';
    if (pct) pct.textContent = progress + '%';
    if (count) count.textContent = `${done}/${total}`;
    if (msg) {
        if (progress === 100)  msg.textContent = '🎉 Wszystko zrobione!';
        else if (progress >= 50) msg.textContent = '💪 Dobra robota!';
        else if (total === 0)  msg.textContent = '📋 Dodaj pierwsze zadanie';
        else msg.textContent = '🚀 Do dzieła!';
    }
}

function updateXP(xp) {
    // stat card
    const xpBlock = document.querySelector('.xp-block p:first-of-type');
    if (xpBlock) xpBlock.textContent = xp;

    // sidebar — lewa etykieta paska XP
    const xpLabel = document.querySelector('.xp-bar-labels span:first-child');
    if (xpLabel) xpLabel.textContent = `${xp} XP`;
}

document.addEventListener('DOMContentLoaded', function () {
    // inicjalizacja paska postępu
    const fill = document.querySelector('.progress-bar-fill');
    if (fill) {
        const target = fill.dataset.width;
        setTimeout(() => { fill.style.width = target + '%'; }, 50);
    }
    const pct = document.getElementById('day-pct-text');
    if (pct) pct.textContent = pct.dataset.progress + '%';
});