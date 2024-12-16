document.addEventListener('DOMContentLoaded', function () {
    const trackingData = window.trackingData;

    if (!trackingData || trackingData.length === 0) {
        document.getElementById('noResourceMessage').style.display = 'block';
        return;
    }

    let labels = [];
    let datasets = [];
    let formatTypes = {};
    let totalAccess = 0; // Biến lưu tổng số lượt truy cập
    let chartType = 'bar'; // Loại biểu đồ mặc định

    processData(trackingData);

    const ctx = document.getElementById('statisticsChart').getContext('2d');
    let chart = createChart(chartType);

    // Cập nhật tiêu đề ngày bắt đầu đến ngày kết thúc và tổng số access
    updateDateRangeAndTotalAccess();

    // Lắng nghe thay đổi loại biểu đồ
    document.getElementById('chartType').addEventListener('change', function () {
        chartType = this.value;
        chart.destroy(); // Hủy biểu đồ cũ
        chart = createChart(chartType); // Tạo biểu đồ mới
        updateDateRangeAndTotalAccess(); // Cập nhật tiêu đề khi thay đổi biểu đồ
    });

    function createChart(type) {
        return new Chart(ctx, {
            type: type,
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: true, position: 'top' },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return `${context.dataset.label} - ${context.label}: ${context.raw} accesses`;
                            }
                        }
                    }
                },
                scales: type !== 'pie' ? {
                    x: { title: { display: true, text: 'Date Updated' } },
                    y: { beginAtZero: true, title: { display: true, text: 'Access Count' } }
                } : {}
            }
        });
    }

    function processData(data) {
        labels = [];
        datasets = [];
        formatTypes = {};
        totalAccess = 0; // Đặt lại tổng số lượt truy cập khi xử lý lại dữ liệu

        data.forEach(item => {
            item.resources.forEach(resource => {
                const formattedDate = formatDate(resource.date_updated);
                if (!labels.includes(formattedDate)) {
                    labels.push(formattedDate);
                }

                const formatType = item.format_type || 'Unknown';
                if (!formatTypes[formatType]) {
                    formatTypes[formatType] = new Array(labels.length).fill(0);
                }

                const dateIndex = labels.indexOf(formattedDate);
                formatTypes[formatType][dateIndex] += resource.total_access || 0;
                totalAccess += resource.total_access || 0; // Cộng tổng số lượt truy cập
            });
        });

        Object.keys(formatTypes).forEach(formatType => {
            datasets.push({
                label: formatType,
                data: formatTypes[formatType],
                backgroundColor: getColorForFormatType(formatType),
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            });
        });
    }

    function formatDate(dateString) {
        const date = new Date(dateString);
        return `${String(date.getDate()).padStart(2, '0')}-${String(date.getMonth() + 1).padStart(2, '0')}-${date.getFullYear()}`;
    }

    function getColorForFormatType(formatType) {
        const colors = {
            'XLSX': 'rgba(54, 162, 235, 0.6)',
            'PNG': 'rgba(255, 99, 132, 0.6)',
            'JPEG': 'rgba(255, 99, 132, 1)',
            'CSV': 'rgba(153, 102, 255, 0.6)',
            'Unknown': 'rgba(255, 159, 64, 0.6)',
        };
        return colors[formatType] || 'rgba(75, 192, 192, 0.2)';
    }

    // Hàm tính toán ngày bắt đầu và ngày kết thúc
    function getDateRange() {
        const allDates = [];
        trackingData.forEach(item => {
            item.resources.forEach(resource => {
                const formattedDate = formatDate(resource.date_updated);
                if (!allDates.includes(formattedDate)) {
                    allDates.push(formattedDate);
                }
            });
        });

        if (allDates.length === 0) {
            return { startDate: 'N/A', endDate: 'N/A' };
        }

        // Sắp xếp các ngày và lấy ngày bắt đầu và kết thúc
        allDates.sort((a, b) => new Date(a) - new Date(b));
        return { startDate: allDates[0], endDate: allDates[allDates.length - 1] };
    }

    // Cập nhật tiêu đề ngày bắt đầu đến ngày kết thúc và tổng số access
    function updateDateRangeAndTotalAccess() {
        const { startDate, endDate } = getDateRange();
        const dateRangeTitleElement = document.getElementById('dateRangeTitle');
        const totalAccessTitleElement = document.getElementById('totalAccessTitle');

        dateRangeTitleElement.innerHTML = `From <strong>${startDate}</strong> to <strong>${endDate}</strong>`;
        totalAccessTitleElement.innerHTML = `Total Accesses: <strong>${totalAccess}</strong>`;
    }

});
