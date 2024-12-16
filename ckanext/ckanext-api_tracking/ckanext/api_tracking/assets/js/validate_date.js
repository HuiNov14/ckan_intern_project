document.addEventListener('DOMContentLoaded', function () {
    // Lắng nghe sự kiện submit khi DOM đã được tải xong
    document.getElementById('tracking-form').addEventListener('submit', function (event) {
        if (!validateDates()) {
            event.preventDefault();
        }
    });

    document.getElementById('start_date').addEventListener('change', validateDates);
    document.getElementById('end_date').addEventListener('change', validateDates);

    function validateDates() {
        var startDate = document.getElementById('start_date').value;
        var endDate = document.getElementById('end_date').value;

        var startDateError = document.getElementById('start-date-error');
        var endDateError = document.getElementById('end-date-error');

        startDateError.textContent = '';
        endDateError.textContent = '';

        if (new Date(startDate) > new Date(endDate)) {
            startDateError.textContent = 'Start Date must be earlier than or equal to End Date.';
            endDateError.textContent = 'End Date must be later than or equal to Start Date.';
            return false;
        }
        return true;
    }
});