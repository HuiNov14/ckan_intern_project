"use strict";

ckan.module('custom_chart_datatypes', function ($) {
    return {
        initialize: function () {
            const trackingDatatypes = this.options.chart_datatypes;
            const chartColor = this.options.chart_color;

            if (!trackingDatatypes || trackingDatatypes.length === 0) {
                document.getElementById('noResourceMessage').style.display = 'block';
                return;
            }

            let labels = [];
            let datasets = [];
            let formatTypes = {};
            let totalAccess = 0;
            const tracking = this.options.tracking;
            processData(trackingDatatypes);

            const ctx = document.getElementById('statisticsChart').getContext('2d');
            let chart = createChart(); // Biểu đồ mặc định là hình tròn

            // Cập nhật tiêu đề ngày bắt đầu đến ngày kết thúc và tổng số access
            updateDateRangeAndTotalAccess();

            function createChart() {
                return new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: labels,
                        datasets: datasets
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: true, position: 'top' },
                            tooltip: {
                                callbacks: {
                                    label: function (context) {
                                        return `${context.label}: ${context.raw} ${tracking}`;
                                    }
                                }
                            }
                        }
                    }
                });
            }

            function processData(data) {
                labels = [];
                datasets = [];
                formatTypes = {};
                totalAccess = 0;

                data.forEach(item => {
                    item.resources.forEach(resource => {
                        const formatType = item.format_type || 'Unknown';
                        if (!formatTypes[formatType]) {
                            formatTypes[formatType] = 0;
                        }
                        formatTypes[formatType] += resource.total_access || 0;
                        totalAccess += resource.total_access || 0;
                    });
                });

                labels = Object.keys(formatTypes);
                datasets.push({
                    data: Object.values(formatTypes),
                    backgroundColor: labels.map(getColorForFormatType),
                    borderColor: 'rgba(255, 255, 255, 1)',
                    borderWidth: 2
                });
            }

            function getColorForFormatType(formatType) {
                return chartColor[formatType];
            }


        }
    };
});
