"use strict";

ckan.module('custom_chart_org', function ($) {
    return {
        initialize: function () {

            // Access some options passed to this JavaScript module by the calling
            // template.
            var chartOrg = this.options.chart_org;
            var count = this.options.count;
            var state = this.options.state;
            var publicCount = this.options.public;
            var privateCount = this.options.private;
            var name = this.options.name;
            console.log("chartOrg: ", chartOrg);

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
                                label: state,
                                data: activeCounts,
                                backgroundColor: 'rgba(153, 102, 255, 0.6)', // Màu tím
                                borderColor: 'rgba(153, 102, 255, 1)',
                                borderWidth: 1
                            },
                            {
                                label: publicCount,
                                data: publicCounts,
                                backgroundColor: 'rgba(255, 206, 86, 0.6)', // Màu vàng
                                borderColor: 'rgba(255, 206, 86, 1)',
                                borderWidth: 1
                            },
                            {
                                label: privateCount,
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
                                    text: name
                                }
                            },
                            y: {
                                title: {
                                    display: true,
                                    text: count
                                },
                                beginAtZero: true
                            }
                        },
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    title: function (tooltipItems) {
                                        // Return full name on hover
                                        const index = tooltipItems[0].dataIndex;
                                        return chartOrg[index].organization_title; // Full name of the organization
                                    }
                                }
                            }
                        }
                    }
                });
            }

            // Hàm lấy dữ liệu và xử lý tên tổ chức
            function prepareData() {
                const groupedData = {};

                chartOrg.forEach(item => {
                    const organizationName = item.organization_title; // Lấy tên tổ chức
                    if (!groupedData[organizationName]) {
                        groupedData[organizationName] = {
                            state_count: 0,
                            public_count: 0,
                            private_count: 0
                        };
                    }

                    groupedData[organizationName].state_count += item.state_count;
                    groupedData[organizationName].public_count += item.public_count;
                    groupedData[organizationName].private_count += item.private_count;
                });

                const labels = Object.keys(groupedData).map(name => truncateText(name, 15)); // Truncate organization names to 15 characters
                const activeCounts = Object.values(groupedData).map(item => item.state_count);
                const publicCounts = Object.values(groupedData).map(item => item.public_count);
                const privateCounts = Object.values(groupedData).map(item => item.private_count);

                renderChart(labels, activeCounts, publicCounts, privateCounts);
            }

            // Hàm rút ngắn tên tổ chức
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
