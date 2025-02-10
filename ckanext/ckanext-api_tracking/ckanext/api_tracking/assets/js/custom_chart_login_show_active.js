"use strict";

ckan.module('custom_chart_login_activity', function ($) {
    return {
        initialize: function () {
            const apiData = this.options.chart_login_activity;
            const dateList = this.options.chart_date_list;
            let chartType = 'bar';

            if (Array.isArray(dateList) && dateList.length > 0) {
                document.getElementById("start-date").value = dateList[0];
                document.getElementById("end-date").value = dateList[dateList.length - 1];
            }

            const loginData = {};
            dateList.forEach(date => {
                loginData[date] = apiData[date] || 0;
            });

            const labels = Object.keys(loginData);
            const data = Object.values(loginData);

            const lineCtx = document.getElementById('statisticsChart').getContext('2d');
            let chart = createChart(chartType);

            document.getElementById('chartType').addEventListener('change', function () {
                chartType = this.value;
                chart.destroy(); // Hủy biểu đồ cũ
                chart = createChart(chartType); // Tạo biểu đồ mới
            });
            function createChart(type) {
                return new Chart(lineCtx, {
                    type: type,
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Number of logins',
                            data: data,
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.2,
                        }]
                    },
                    options: {
                        responsive: true,
                        aspectRatio: 2,
                        scales: {
                            x: {
                                ticks: {
                                    autoSkip: false,
                                    maxRotation: 45,
                                    minRotation: 0
                                },
                                title: {
                                    display: true,
                                    text: 'Date'
                                }
                            },
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: 'Number of logins'
                                }
                            }
                        }
                    }
                });
            }
            document.getElementById('date-form').addEventListener('submit', function (event) {
                if (!validateDates()) {
                    event.preventDefault();
                }
            });

            document.getElementById('start-date').addEventListener('change', validateDates);
            document.getElementById('end-date').addEventListener('change', validateDates);

            function validateDates() {
                const startDate = document.getElementById('start-date').value;
                const endDate = document.getElementById('end-date').value;

                const startDateError = document.getElementById('start-date-error');
                const endDateError = document.getElementById('end-date-error');

                startDateError.textContent = '';
                endDateError.textContent = '';

                const start = new Date(startDate);
                const end = new Date(endDate);

                if (start > end) {
                    startDateError.textContent = 'The start date must be before the end date.';
                    endDateError.textContent = 'The end date must be after the start date.';
                    return false;
                }

                const diffTime = Math.abs(end - start);
                const diffDays = diffTime / (1000 * 60 * 60 * 24);
                if (diffDays > 30) {
                    startDateError.textContent = 'The filter date range limit cannot exceed 30 days.';
                    endDateError.textContent = 'Please select a smaller filter date range.';
                    return false;
                }

                return true;
            }
        }
    };
});
