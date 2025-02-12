"use strict";

ckan.module('custom_chart_new_user', function ($) {
    return {
        initialize: function () {
            const apiData = this.options.chart_new_user;
            const newuser = this.options.newuser;
            const validator = this.options.validator;
            const x = this.options.x;
            const y = this.options.y;
            apiData.days.sort((a, b) => new Date(a.date) - new Date(b.date));

            const labels = apiData.days.map(item => item.date);
            const data = apiData.days.map(item => item.user_created_count);
            let chartType = 'bar';

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
                            label: newuser,
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
                                    text: x
                                }
                            },
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: y
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
                    startDateError.textContent = validator.start_date_after_end_date;
                    endDateError.textContent = validator.end_date_before_start_date;
                    return false;
                }
                return true;
            }
        }
    };
});