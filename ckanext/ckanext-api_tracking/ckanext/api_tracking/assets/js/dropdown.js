// Lắng nghe sự kiện khi người dùng thay đổi lựa chọn
document.addEventListener('DOMContentLoaded', function () {
    const statisticsSelect = document.getElementById('statistics_select');

    statisticsSelect.addEventListener('change', function () {
        const selectedValue = this.value; // Lấy giá trị đã chọn
        if (selectedValue) {
            window.location.href = selectedValue; // Chuyển hướng trình duyệt
        }
    });
});