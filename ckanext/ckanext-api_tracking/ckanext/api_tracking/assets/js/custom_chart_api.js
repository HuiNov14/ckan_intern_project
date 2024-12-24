document.addEventListener('DOMContentLoaded', function () {
    console.log("===================>", window.trackingData);

    drawChart(window.trackingData);
});

function drawChart(data) {
    console.log("Data", data);

    const ctx = document.getElementById('statisticsChart').getContext('2d');

    // Lấy dữ liệu từ `data`
    const apiNames = data.data.map(item => item.api); // Lấy danh sách tên API
    const apiTotal = data.total;

    // Vẽ biểu đồ
    new Chart(ctx, {
        type: 'bar', // Loại biểu đồ là bar
        data: {
            labels: apiNames, // Dữ liệu trục x (tên API)
            datasets: [{
                label: 'API Size (in bytes)', // Tiêu đề của biểu đồ
                data: apiTotal, // Dữ liệu trục y (size của từng API)
                backgroundColor: 'rgba(153, 102, 255, 0.2)', // Màu nền của các cột
                borderColor: 'rgba(153, 102, 255, 1)', // Màu viền của các cột
                borderWidth: 1 // Độ dày viền
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true, // Bắt đầu từ 0
                    ticks: {
                        callback: function (value) {
                            return value + ' bytes'; // Hiển thị giá trị với đơn vị bytes
                        }
                    }
                }
            }
        }
    });
}
