"use strict";

ckan.module('custom_chart_field', function ($) {
    return {
        initialize: function () {

            // Access some options passed to this JavaScript module by the calling
            // template.
            var chartFiled = this.options.chart_field;
            console.log("chartFiled: ", chartFiled);

            const ctx = document.getElementById('statisticsChart').getContext('2d');
            let chart; // Biến lưu trữ biểu đồ để có thể cập nhật lại

            // Hàm vẽ biểu đồ
            function renderChart(labels, activeCounts, publicCounts, privateCounts, chartType = 'bar') {
                if (chart) chart.destroy(); // Xóa biểu đồ cũ nếu đã tồn tại
                chart = new Chart(ctx, {
                    type: chartType,
                    data: {
                        labels: labels,
                        datasets: [
                            {
                                label: 'State Count',
                                data: activeCounts,
                                backgroundColor: 'rgba(153, 102, 255, 0.6)', // Màu tím
                                borderColor: 'rgba(153, 102, 255, 1)',
                                borderWidth: 1
                            },
                            {
                                label: 'Public Count',
                                data: publicCounts,
                                backgroundColor: 'rgba(255, 206, 86, 0.6)', // Màu vàng
                                borderColor: 'rgba(255, 206, 86, 1)',
                                borderWidth: 1
                            },
                            {
                                label: 'Private Count',
                                data: privateCounts,
                                backgroundColor: 'rgba(255, 99, 132, 0.6)', // Màu đỏ
                                borderColor: 'rgba(255, 99, 132, 1)',
                                borderWidth: 1
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: {
                                title: {
                                    display: true,
                                    text: 'Group Name'
                                }
                            },
                            y: {
                                title: {
                                    display: true,
                                    text: 'Count'
                                },
                                beginAtZero: true
                            }
                        },
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    title: function (tooltipItems) {
                                        // Return full field name on hover
                                        const index = tooltipItems[0].dataIndex;
                                        return chartFiled[index].field_name; // Full field name
                                    }
                                }
                            }
                        }
                    }
                });
            }

            // Hàm lấy dữ liệu và xử lý tên trường
            function prepareData() {
                const groupedData = {};

                chartFiled.forEach(item => {
                    const fieldName = item.field_name; // Lấy tên trường
                    if (!groupedData[fieldName]) {
                        groupedData[fieldName] = {
                            state_count: 0,
                            public_count: 0,
                            private_count: 0
                        };
                    }

                    groupedData[fieldName].state_count += item.state_count;
                    groupedData[fieldName].public_count += item.public_count;
                    groupedData[fieldName].private_count += item.private_count;
                });

                const labels = Object.keys(groupedData).map(name => truncateText(name, 15)); // Truncate field names to 15 characters
                const activeCounts = Object.values(groupedData).map(item => item.state_count);
                const publicCounts = Object.values(groupedData).map(item => item.public_count);
                const privateCounts = Object.values(groupedData).map(item => item.private_count);

                renderChart(labels, activeCounts, publicCounts, privateCounts);
            }

            // Hàm rút ngắn tên trường
            function truncateText(text, maxLength) {
                if (text.length > maxLength) {
                    return text.substring(0, maxLength) + '...'; // Truncate and add ellipses
                }
                return text;
            }

            // Gọi hàm chuẩn bị dữ liệu và vẽ biểu đồ lần đầu
            prepareData();

            // Thêm sự kiện cho loại biểu đồ
            document.getElementById('chartType').addEventListener('change', function () {
                const chartType = this.value;
                prepareData();
                chart.config.type = chartType;
                chart.update();
            });
        }
    };
});
