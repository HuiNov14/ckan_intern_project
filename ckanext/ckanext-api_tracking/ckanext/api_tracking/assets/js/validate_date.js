ckan.module('custom_form_validation', function ($) {
  return {
    initialize: function () {
      console.log("Custom form validation initialized for element:", this.el);
      const errorMessages = this.options.errors;
      const form = $('#tracking-form');
      const startDateInput = $('#start_date');
      const endDateInput = $('#end_date');
      const startDateError = $('#start-date-error');
      const endDateError = $('#end-date-error');

      const validateDates = function (event) {
        // Xóa thông báo lỗi cũ
        startDateError.text('');
        endDateError.text('');

        const startDate = new Date(startDateInput.val());
        const endDate = new Date(endDateInput.val());

        if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
          if (isNaN(startDate.getTime())) {
            startDateError.text(errorMessages.start_date_invalid);
          }
          if (isNaN(endDate.getTime())) {
            endDateError.text(errorMessages.end_date_invalid);
          }
          event.preventDefault(); // Ngăn không cho submit
          return false;
        }

        if (startDate > endDate) {
          startDateError.text(errorMessages.start_date_after_end_date);
          endDateError.text(errorMessages.end_date_before_start_date);
          event.preventDefault(); // Ngăn không cho submit
          return false;
        }

        return true;
      };

      // Kiểm tra khi người dùng submit form
      form.on('submit', validateDates);

      // Kiểm tra ngay khi thay đổi ngày
      startDateInput.on('change', validateDates);
      endDateInput.on('change', validateDates);
    }
  };
});


