function toggleTheme() {
    document.body.classList.toggle('light');
    const isLight = document.body.classList.contains('light');
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
    updateThemeBtn(isLight);
}

function updateThemeBtn(isLight) {
    const btn = document.getElementById('theme-toggle');
    btn.innerHTML = isLight
        ? '<i class="fa-solid fa-moon"></i>Tryb ciemny'
        : '<i class="fa-solid fa-lightbulb"></i>Tryb jasny';
}

document.addEventListener('DOMContentLoaded', function () {
    // motyw
    const saved = localStorage.getItem('theme');
    if (saved === 'light') {
        document.body.classList.add('light');
        updateThemeBtn(true);
    }
});