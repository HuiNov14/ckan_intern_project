document.addEventListener('DOMContentLoaded', function () {
    console.log("===================>", window.trackingData);

    drawCharts(window.trackingData);
});

function drawCharts(data) {
    console.log("Data", data);

    const totalCtx = document.getElementById('statisticsChart').getContext('2d');
    const sizeCtx = document.getElementById('sizeChart').getContext('2d');
    const resourceCtx = document.getElementById('resourceSizeChart').getContext('2d');

    // Lọc danh sách API để lấy tên duy nhất
    const uniqueApis = [...new Set(data.data.map(item => item.api))]; // Lấy danh sách API duy nhất

    // Tạo dữ liệu tổng (total) tương ứng
    const apiTotal = Array(uniqueApis.length).fill(data.total); // Gán giá trị `total` cho mỗi API duy nhất

    // Gộp dữ liệu theo ngày và tính tổng size
    const groupedByDate = {};
    data.data.forEach(item => {
        const dateKey = new Date(item.created).toLocaleDateString(); // Chuyển ngày về định dạng ngắn gọn
        const sizeInBytes = parseSizeToBytes(item.size); // Chuyển đổi size về bytes
        if (groupedByDate[dateKey]) {
            groupedByDate[dateKey] += sizeInBytes; // Cộng thêm size nếu đã tồn tại ngày
        } else {
            groupedByDate[dateKey] = sizeInBytes; // Khởi tạo ngày nếu chưa tồn tại
        }
    });

    // Chuyển groupedByDate thành mảng để vẽ biểu đồ
    const groupedDates = Object.keys(groupedByDate); // Các ngày đã gộp
    const groupedSizes = Object.values(groupedByDate); // Tổng size tương ứng với từng ngày

    // Gộp dữ liệu theo `resource_name` và tính tổng size
    const groupedByResource = {};
    data.data.forEach(item => {
        const resourceKey = item.resource_name; // Tên tài nguyên
        const sizeInBytes = parseSizeToBytes(item.size); // Chuyển đổi size về bytes
        if (groupedByResource[resourceKey]) {
            groupedByResource[resourceKey] += sizeInBytes; // Cộng thêm size nếu đã tồn tại tài nguyên
        } else {
            groupedByResource[resourceKey] = sizeInBytes; // Khởi tạo tài nguyên nếu chưa tồn tại
        }
    });

    // Chuyển groupedByResource thành mảng để vẽ biểu đồ
    const groupedResourceNames = Object.keys(groupedByResource); // Tên tài nguyên đã gộp
    const groupedResourceSizes = Object.values(groupedByResource); // Tổng size tương ứng với từng tài nguyên

    // Thu hẹp tên tài nguyên nếu quá dài
    const maxLabelLength = 15;
    const shortenedResourceNames = groupedResourceNames.map(name =>
        name.length > maxLabelLength ? name.substring(0, maxLabelLength) + '...' : name
    );

    // Vẽ biểu đồ "Total"
    new Chart(totalCtx, {
        type: 'bar',
        data: {
            labels: uniqueApis,
            datasets: [{
                label: 'API Total',
                data: apiTotal,
                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                borderColor: 'rgba(153, 102, 255, 1)',
                borderWidth: 1,
            }],
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => value + ' total',
                    },
                },
            },
        },
    });

    // Vẽ biểu đồ "Size" theo ngày đã gộp
    new Chart(sizeCtx, {
        type: 'bar',
        data: {
            labels: groupedDates, // Các ngày đã gộp
            datasets: [{
                label: 'Total Resource Size (in bytes)',
                data: groupedSizes, // Tổng kích thước đã gộp
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
            }],
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => value + ' bytes',
                    },
                },
                x: {
                    ticks: {
                        callback: function (value, index) {
                            return this.getLabelForValue(index);
                        },
                    },
                },
            },
        },
    });

    // Vẽ biểu đồ "Resource Size" theo tên tài nguyên đã gộp
    new Chart(resourceCtx, {
        type: 'bar',
        data: {
            labels: shortenedResourceNames, // Tên tài nguyên đã gộp và thu gọn
            datasets: [{
                label: 'Total Resource Size (in bytes)',
                data: groupedResourceSizes, // Tổng size đã gộp
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
            }],
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => value + ' bytes',
                    },
                },
                x: {
                    ticks: {
                        callback: function (value, index) {
                            return this.getLabelForValue(index);
                        },
                    },
                },
            },
        },
    });
}

// Hàm chuyển đổi size về bytes
function parseSizeToBytes(sizeString) {
    const sizeLower = sizeString.toLowerCase(); // Chuyển về chữ thường để kiểm tra đơn vị
    if (sizeLower.includes('kib')) {
        // Nếu đơn vị là KiB, chuyển sang bytes
        return parseFloat(sizeLower.replace(' kib', '').replace(',', '.')) * 1024;
    } else if (sizeLower.includes('bytes')) {
        // Nếu đơn vị là bytes, giữ nguyên
        return parseInt(sizeLower.replace(' bytes', '').replace(',', ''));
    } else {
        // Mặc định trả về 0 nếu không xác định được đơn vị
        return 0;
    }
}
