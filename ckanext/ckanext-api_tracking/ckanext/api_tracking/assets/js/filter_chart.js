  document.addEventListener('DOMContentLoaded', function () {
    const statisticsSelect = document.getElementById('statistics_select');

    // Hàm cập nhật trạng thái ẩn/hiện của các tùy chọn
    const updateHiddenOptions = () => {
      const selectedValue = statisticsSelect.value;
      Array.from(statisticsSelect.options).forEach(option => {
        // Ẩn tùy chọn đang được chọn
        option.hidden = option.value === selectedValue;
      });
    };

    // Gọi hàm cập nhật trạng thái ngay khi trang tải
    updateHiddenOptions();

    // Gắn sự kiện 'change' để xử lý khi người dùng thay đổi giá trị
    statisticsSelect.addEventListener('change', function () {
      const selectedValue = this.value;
      if (selectedValue) {
        // Điều hướng đến URL tương ứng
        window.location.href = selectedValue;
      }
      // Cập nhật trạng thái ẩn/hiện của các tùy chọn
      updateHiddenOptions();
    });
  });