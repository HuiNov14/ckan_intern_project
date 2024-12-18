document.addEventListener('DOMContentLoaded', function () {
    const data = window.trackingData;
    const trackingData = data.days || [];

    const ctx = document.getElementById('statisticsChart').getContext('2d');
    let chart; 

    function renderChart(labels, activeCounts, chartType = 'bar') {
        if (chart) chart.destroy(); 

        chart = new Chart(ctx, {
            type: chartType,
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Active User Count',
                        data: activeCounts,
                        backgroundColor: 'rgba(54, 162, 235, 0.6)', 
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Active User Count by Date'
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Active User Count'
                        },
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Hàm chuẩn bị dữ liệu
    function prepareData() {
        // Lấy danh sách ngày và active_user_count từ dữ liệu
        const labels = trackingData.map(item => item.date);
        const activeCounts = trackingData.map(item => item.active_user_count);

        // Gọi hàm renderChart để vẽ biểu đồ
        renderChart(labels, activeCounts);
    }

    // Gọi hàm chuẩn bị dữ liệu và vẽ biểu đồ lần đầu
    prepareData();

    // Sự kiện thay đổi kiểu biểu đồ
    document.getElementById('chartType').addEventListener('change', function () {
        const chartType = this.value;
        prepareData();
        chart.config.type = chartType;
        chart.update();
    });
});
