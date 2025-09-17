    document.addEventListener("DOMContentLoaded", function() {
    const taskTypeSelect = document.getElementById("id_task_type");
    const weeklyTargetField = document.getElementById("weekly-target-field");

    function toggleWeeklyTarget() {
        if (taskTypeSelect.value === "WEEKLY") {
            weeklyTargetField.style.display = "block";
        } else {
            weeklyTargetField.style.display = "none";
        }
    }

    taskTypeSelect.addEventListener("change", toggleWeeklyTarget);
    toggleWeeklyTarget(); // ustaw od razu przy ładowaniu strony
});
