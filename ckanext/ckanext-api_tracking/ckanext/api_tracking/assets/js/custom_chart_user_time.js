"use strict";

ckan.module('custom_chart_user_time', function ($) {
    return {
        initialize: function () {
            document.getElementById('statisticsChart').style.height = '450px';
            let listUserTime = this.options.chart_user_time;

            let labels = listUserTime.days.map(item => item.date);
            let userCounts = listUserTime.days.map(item => item.active_user_count);
            let chartType = 'bar';

            // Hiển thị tổng số user và khoảng ngày
            const totalUserCount = listUserTime.total_user_count; // Tổng số user
            const endDate = listUserTime.days[0].date; // Ngày bắt đầu
            const startDate = listUserTime.days[listUserTime.days.length - 1].date; // Ngày kết thúc


            // Cập nhật thông tin khoảng ngày và tổng số user
            const dateRangeTitle = document.getElementById('dateRangeTitle');
            const totalAccessTitle = document.getElementById('totalAccessTitle');

            // Cập nhật thông tin vào các phần tử nếu cần hiển thị
            dateRangeTitle.innerHTML = `<h5>Khoảng ngày: Từ ${startDate} đến ${endDate}</h5>`;
            totalAccessTitle.innerHTML = `<h5>Tổng số người dùng: ${totalUserCount}</h5>`;

            // Lấy giá trị từ dropdown 'include_user_info_detail'
            const selectIncludeUserInfo = document.querySelector('select[name="include_user_info_detail"]');

            // Hàm kiểm tra giá trị và hiển thị/ẩn các phần tử
            function toggleVisibility() {
                if (selectIncludeUserInfo.value === 'true') {
                    // Hiển thị các phần tử
                    dateRangeTitle.style.display = 'block';
                    totalAccessTitle.style.display = 'block';
                } else {
                    // Ẩn các phần tử
                    dateRangeTitle.style.display = 'none';
                    totalAccessTitle.style.display = 'none';
                }
            }

            // Gọi hàm toggleVisibility khi trang được tải xong
            toggleVisibility();

            // Lắng nghe sự kiện thay đổi giá trị của dropdown
            selectIncludeUserInfo.addEventListener('change', function () {
                toggleVisibility(); // Cập nhật hiển thị dựa trên giá trị mới
            });

            // Cấu hình biểu đồ
            const ctx = document.getElementById('statisticsChart').getContext('2d');
            let chart = createChart(chartType);

            document.getElementById('chartType').addEventListener('change', function () {
                chartType = this.value;
                chart.destroy(); // Hủy biểu đồ cũ
                chart = createChart(chartType); // Tạo biểu đồ mới
                document.getElementById('statisticsChart').style.height = '450px';
            });

            function createChart(type) {
                return new Chart(ctx, {
                    type: type,
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Số lượng người dùng',
                            data: userCounts,
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
                                    text: 'Ngày'
                                },
                                ticks: {
                                    autoSkip: true,
                                    maxTicksLimit: 10
                                }
                            },
                            y: {
                                title: {
                                    display: true,
                                    text: 'Số lượng người dùng'
                                },
                                beginAtZero: true
                            }
                        },
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    label: function (tooltipItem) {
                                        return 'Người dùng: ' + tooltipItem.raw;
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
