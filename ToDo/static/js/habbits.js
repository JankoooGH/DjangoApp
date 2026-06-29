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
