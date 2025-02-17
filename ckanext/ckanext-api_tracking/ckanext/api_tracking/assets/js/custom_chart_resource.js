"use strict";

ckan.module('custom_chart_resource', function ($) {
    return {
        initialize: function () {
            const chartRes = this.options.chart_resource;
            const x = this.options.x;
            const y = this.options.y;
            // const totalRes = chartRes.total_resources;
            const countByDate = {};
            chartRes.result.forEach(item => {
                const date = item.created_date;
                countByDate[date] = (countByDate[date] || 0) + 1;
            });

            // Chuyển dữ liệu thành mảng để vẽ biểu đồ
            const labels = Object.keys(countByDate).sort();
            const data = labels.map(date => countByDate[date]);
            // Khởi tạo canvas cho biểu đồ
            const ctx = document.getElementById('statisticsChart').getContext('2d');
            let chartType = 'bar'; // 
            let chart = createChart(chartType);

            document.getElementById('statisticsChart').style.height = '450px';

            // Lắng nghe sự thay đổi loại biểu đồ
            document.getElementById('chartType').addEventListener('change', function () {
                chartType = this.value; // Lấy giá trị loại biểu đồ đã chọn
                chart.destroy(); // Hủy biểu đồ cũ
                chart = createChart(chartType); // Tạo biểu đồ mới
                document.getElementById('statisticsChart').style.height = '450px';
            });

            // Hàm tạo biểu đồ với loại đã chọn
            function createChart(type) {
                return new Chart(ctx, {
                    type: type, // Loại biểu đồ sẽ được truyền vào
                    data: {
                        labels: labels, // Các nhãn (ngày tháng)
                        datasets: [{
                            label: "Số lượng tài nguyên",
                            data: data, // Dữ liệu số lượng tài nguyên
                            borderColor: 'rgb(54, 162, 235)',
                            backgroundColor: 'rgba(54, 162, 235, 0.2)',
                            borderWidth: 2,
                            tension: 0.3,
                            pointRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            x: {
                                title: {
                                    display: true,
                                    text: x
                                },
                                ticks: {
                                    autoSkip: true,
                                    maxTicksLimit: 90
                                }
                            },
                            y: {
                                title: {
                                    display: true,
                                    text: y
                                },
                                beginAtZero: true
                            }
                        },
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    label: function (tooltipItem) {
                                        return y + ":" + tooltipItem.raw;
                                    }
                                }
                            }
                        }
                    }
                });
            }
        }
    };
});
