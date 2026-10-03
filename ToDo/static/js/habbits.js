function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// ── Modal ────────────────────────────────────────
const overlay = document.getElementById('modal-overlay');

function openModal()  { overlay.style.display = 'flex';
    setTimeout(() => overlay.classList.add('open'), 10); }
function closeModal() { overlay.classList.remove('open');
    setTimeout(() => overlay.style.display = 'none', 200); }

function selectColor(el) {
          document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
          el.classList.add('selected');
          document.getElementById('color-input').value = el.dataset.color;
}


const deleteOverlay = document.getElementById('delete-overlay');


function openDeleteModal(id, title) {
    document.getElementById('delete-form').action = `/delete/${id}/`;
    document.getElementById('delete-modal-text').textContent = `Usunąć "${title}"?`;
    deleteOverlay.style.display = 'flex';
    setTimeout(() => deleteOverlay.classList.add('open'), 10);}


function closeDeleteModal() { deleteOverlay.classList.remove('open');
    setTimeout(() => deleteOverlay.style.display = 'none', 200);}

function openEditModal(btn) {
    document.getElementById('task-form').action = `/edit/${btn.dataset.id}/`;

    document.getElementById('id_title').value = btn.dataset.title;
    document.getElementById('id_description').value = btn.dataset.description;
    document.getElementById('id_task_type').value = btn.dataset.type;
    document.getElementById('id_weekly_target').value = btn.dataset.weeklyTarget;
    document.getElementById('id_date').value = btn.dataset.date;

    document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
    document.querySelector(`.color-swatch[data-color="${btn.dataset.color}"]`).classList.add('selected');
    document.getElementById('color-input').value = btn.dataset.color;

    openModal();
}

function selectColor(el) {
    document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
    el.classList.add('selected');
    document.getElementById('color-input').value = el.dataset.color;
}

function openNewModal() {
    document.getElementById('task-form').action = "/dashboard/";
    document.getElementById('task-form').reset();
    document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
    document.querySelector('.color-swatch[data-color="indigo"]').classList.add('selected');
    document.getElementById('color-input').value = 'indigo';
    openModal();
}

// ══════════════════════════════════════════
// NOTATKI
// ══════════════════════════════════════════
let currentNoteTaskId = null;
let notesCache = [];
let currentNoteId = null;
let isEditingNote = false;

const notesOverlay = document.getElementById('notes-overlay');

function openNotesModal(el) {
    currentNoteTaskId = el.dataset.id;
    setNotesTitle(el.dataset.title);

    notesOverlay.style.display = 'flex';
    setTimeout(() => notesOverlay.classList.add('open'), 10);

    showNotesListView();
}

function closeNotesModal() {
    notesOverlay.classList.remove('open');
    setTimeout(() => notesOverlay.style.display = 'none', 200);
}

function handleNotesOverlayClick(e) {
    if (e.target === notesOverlay) closeNotesModal();
}

function setNotesTitle(title) {
    document.getElementById('notes-task-title').textContent = title;
    document.getElementById('notes-task-title-2').textContent = title;
    document.getElementById('notes-task-title-3').textContent = title;
}

function showView(viewId) {
    ['notes-list-view', 'note-form-view', 'note-detail-view'].forEach(id => {
        document.getElementById(id).style.display = (id === viewId) ? 'block' : 'none';
    });
}

function showNotesListView() {
    showView('notes-list-view');
    loadNotes();
}

function loadNotes() {
    fetch(`/note/${currentNoteTaskId}/list/`)
        .then(r => r.json())
        .then(data => {
            notesCache = data.notes;
            renderNotesList(notesCache);
        });
}

function renderNotesList(notes) {
    const container = document.getElementById('notes-list');

    if (notes.length === 0) {
        container.innerHTML = `<p class="notes-empty">Brak notatek.</p>`;
        return;
    }

    let html = '';
    for (const note of notes) {
        html += `
            <button type="button" class="note-list-item" onclick="showNoteDetailView(${note.id})">
                <i class="fa-regular fa-file-lines"></i>
                <span class="note-list-item__title">${note.title}</span>
                <i class="fa-solid fa-chevron-right note-list-item__chevron"></i>
            </button>`;
    }
    container.innerHTML = html;
}

function showNoteFormView(editMode = false) {
    isEditingNote = editMode;
    const subtitle = document.getElementById('note-form-subtitle');
    const titleInput = document.getElementById('note-title');
    const contentInput = document.getElementById('note-content');

    if (editMode) {
        const note = notesCache.find(n => n.id === currentNoteId);
        subtitle.textContent = 'Edytuj notatkę.';
        titleInput.value = note ? note.title : '';
        contentInput.value = note ? note.content : '';
    } else {
        subtitle.textContent = 'Dodaj nową notatkę.';
        titleInput.value = '';
        contentInput.value = '';
    }

    showView('note-form-view');
}

function saveOrUpdateNote() {
    const title = document.getElementById('note-title').value.trim();
    const content = document.getElementById('note-content').value.trim();
    if (!title) return;

    const formData = new FormData();
    formData.append('title', title);
    formData.append('content', content);

    const url = isEditingNote
        ? `/note/${currentNoteId}/edit/`
        : `/note/${currentNoteTaskId}/save/`;

    fetch(url, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrfToken() },
        body: formData
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'ok') showNotesListView();
    });
}

function showNoteDetailView(noteId) {
    currentNoteId = noteId;
    const note = notesCache.find(n => n.id === noteId);
    if (!note) return;

    document.getElementById('note-detail-date').textContent = formatNoteDateLong(note.created_at);
    document.getElementById('note-detail-title').textContent = note.title;
    document.getElementById('note-detail-content').textContent = note.content;

    showView('note-detail-view');
}

function deleteCurrentNote() {
    if (!currentNoteId) return;

    fetch(`/note/${currentNoteId}/delete/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrfToken() }
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'ok') showNotesListView();
    });
}

function formatNoteDateShort(iso) {
    return new Date(iso).toLocaleDateString('pl-PL', { day: 'numeric', month: 'short' });
}

function formatNoteDateLong(iso) {
    return new Date(iso).toLocaleString('pl-PL', {
        day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit'
    });
}



document.addEventListener('DOMContentLoaded', function () {

        function handleOverlayClick(e) {
          if (e.target === overlay) closeModal();
        }

        document.addEventListener('keydown', e => {
          if (e.key === 'Escape') closeModal();
        });

        // ── Conditional fields based on task type ────────
        const taskTypeSelect  = document.getElementById("id_task_type");
        const fieldWeekly     = document.getElementById("field-weekly-target");
        const fieldDate       = document.getElementById("field-date");

        function toggleConditionalFields() {
          const val = taskTypeSelect.value;
          fieldWeekly.style.display = (val === "WEEKLY") ? "block" : "none";
          fieldDate.style.display   = (val === "ONCE")   ? "block" : "none";
        }

        if (taskTypeSelect) {
          taskTypeSelect.addEventListener("change", toggleConditionalFields);
          toggleConditionalFields();
        }

        // Re-run on modal open
        const _origOpen = openModal;
        openModal = function() { _origOpen(); toggleConditionalFields(); };

});
