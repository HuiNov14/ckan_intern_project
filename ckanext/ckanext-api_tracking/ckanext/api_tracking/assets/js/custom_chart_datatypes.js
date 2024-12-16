document.addEventListener('DOMContentLoaded', function () {
    const trackingData = window.trackingData;

    if (!trackingData || trackingData.length === 0) {
        document.getElementById('noResourceMessage').style.display = 'block';
        return;
    }

    let labels = [];
    let datasets = [];
    let formatTypes = {};
    let chartType = 'bar'; // Loại biểu đồ mặc định

    processData(trackingData);

    const ctx = document.getElementById('statisticsChart').getContext('2d');
    let chart = createChart(chartType);

    document.getElementById('chartType').addEventListener('change', function () {
        chartType = this.value;
        chart.destroy(); // Hủy biểu đồ cũ
        chart = createChart(chartType); // Tạo biểu đồ mới
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
                scales: type !== 'pie' ? { // Không hiển thị trục nếu là Pie Chart
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
});
