document.addEventListener('DOMContentLoaded', function () {
    console.log("===================>", window.trackingData);

    const chartTypeSelector = document.getElementById('chartType');

    // Vẽ biểu đồ lần đầu với loại mặc định là "bar"
    let currentChartType = 'bar';
    drawCharts(window.trackingData, currentChartType);

    // Lắng nghe sự kiện thay đổi loại biểu đồ
    chartTypeSelector.addEventListener('change', function () {
        currentChartType = chartTypeSelector.value;
        drawCharts(window.trackingData, currentChartType);
    });
});

function drawCharts(data, chartType) {
    console.log("Data", data);

    // Lấy các ngữ cảnh canvas
    const totalCtx = document.getElementById('statisticsChart').getContext('2d');
    const sizeCtx = document.getElementById('sizeChart').getContext('2d');
    const resourceCtx = document.getElementById('resourceSizeChart').getContext('2d');

    // Lọc danh sách API để lấy tên duy nhất
    const uniqueApis = [...new Set(data.data.map(item => item.api))]; // Lấy danh sách API duy nhất
    const apiTotal = Array(uniqueApis.length).fill(data.total); // Gán giá trị `total` cho mỗi API duy nhất

    // Gộp dữ liệu theo ngày và tính tổng size (chuyển sang KiB)
    const groupedByDate = {};
    data.data.forEach(item => {
        const dateKey = new Date(item.created).toLocaleDateString(); // Chuyển ngày về định dạng ngắn gọn
        const sizeInKiB = parseSizeToKiB(item.size); // Chuyển đổi size về KiB
        if (groupedByDate[dateKey]) {
            groupedByDate[dateKey] += sizeInKiB; // Cộng thêm size nếu đã tồn tại ngày
        } else {
            groupedByDate[dateKey] = sizeInKiB; // Khởi tạo ngày nếu chưa tồn tại
        }
    });
    const groupedDates = Object.keys(groupedByDate);
    const groupedSizes = Object.values(groupedByDate);

    // Gộp dữ liệu theo `resource_name` và tính tổng size (chuyển sang KiB)
    const groupedByResource = {};
    data.data.forEach(item => {
        const resourceKey = item.resource_name;
        const sizeInKiB = parseSizeToKiB(item.size);
        if (groupedByResource[resourceKey]) {
            groupedByResource[resourceKey] += sizeInKiB;
        } else {
            groupedByResource[resourceKey] = sizeInKiB;
        }
    });
    const groupedResourceNames = Object.keys(groupedByResource);
    const groupedResourceSizes = Object.values(groupedByResource);

    const maxLabelLength = 15;
    const shortenedResourceNames = groupedResourceNames.map(name =>
        name.length > maxLabelLength ? name.substring(0, maxLabelLength) + '...' : name
    );

    // Xóa biểu đồ cũ nếu có
    Chart.getChart('statisticsChart')?.destroy();
    Chart.getChart('sizeChart')?.destroy();
    Chart.getChart('resourceSizeChart')?.destroy();

    // Vẽ biểu đồ "Total"
    new Chart(totalCtx, {
        type: chartType,
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

    // Vẽ biểu đồ "Size" theo ngày
    new Chart(sizeCtx, {
        type: chartType,
        data: {
            labels: groupedDates,
            datasets: [{
                label: 'Total Resource Size (in KiB)',
                data: groupedSizes,
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
                        callback: value => value.toFixed(2) + ' KiB',
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

    // Vẽ biểu đồ "Resource Size"
    new Chart(resourceCtx, {
        type: chartType,
        data: {
            labels: shortenedResourceNames,
            datasets: [{
                label: 'Total Resource Size (in KiB)',
                data: groupedResourceSizes,
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
                        callback: value => value.toFixed(2) + ' KiB',
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

// Hàm chuyển đổi size từ bytes sang KiB
function parseSizeToKiB(sizeString) {
    const sizeLower = sizeString.toLowerCase();
    if (sizeLower.includes('kib')) {
        return parseFloat(sizeLower.replace(' kib', '').replace(',', '.'));
    } else if (sizeLower.includes('bytes')) {
        return parseInt(sizeLower.replace(' bytes', '').replace(',', '')) / 1024;
    } else {
        return 0;
    }
}
