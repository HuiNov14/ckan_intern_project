"use strict";

ckan.module('custom_chart_api', function ($) {
    return {
        initialize: function () {
            const chartApi = this.options.chart_api;
            const chartName = this.options.chart_name;
            const chartTypeSelector = document.getElementById('chartType');

            // Vẽ biểu đồ lần đầu với loại mặc định là "bar"
            let currentChartType = 'bar';
            drawCharts(chartApi, currentChartType);

            // Lắng nghe sự kiện thay đổi loại biểu đồ
            chartTypeSelector.addEventListener('change', function () {
                currentChartType = chartTypeSelector.value;
                drawCharts(chartApi, currentChartType);
            });

            function drawCharts(data, chartType) {
                console.log("Data", data);

                const totalCtx = document.getElementById('statisticsChart').getContext('2d');
                const sizeCtx = document.getElementById('sizeChart').getContext('2d');
                const resourceCtx = document.getElementById('resourceSizeChart').getContext('2d');

                const uniqueApis = [...new Set(data.data.map(item => item.api))];
                const apiTotal = Array(uniqueApis.length).fill(data.total);

                const groupedByDate = {};
                data.data.forEach(item => {
                    const dateKey = new Date(item.created).toLocaleDateString();
                    const sizeInKiB = parseSizeToKiB(item.size);
                    groupedByDate[dateKey] = (groupedByDate[dateKey] || 0) + sizeInKiB;
                });

                const groupedDates = Object.keys(groupedByDate);
                const groupedSizes = Object.values(groupedByDate);

                const groupedByResource = {};
                data.data.forEach(item => {
                    const resourceKey = item.resource_name;
                    const sizeInKiB = parseSizeToKiB(item.size);
                    groupedByResource[resourceKey] = (groupedByResource[resourceKey] || 0) + sizeInKiB;
                });

                const groupedResourceNames = Object.keys(groupedByResource);
                const groupedResourceSizes = Object.values(groupedByResource);

                const maxLabelLength = 15;
                const shortenedResourceNames = groupedResourceNames.map(name =>
                    name.length > maxLabelLength ? name.substring(0, maxLabelLength) + '...' : name
                );

                Chart.getChart('statisticsChart')?.destroy();
                Chart.getChart('sizeChart')?.destroy();
                Chart.getChart('resourceSizeChart')?.destroy();

                // Vẽ biểu đồ "Total"
                new Chart(totalCtx, {
                    type: chartType,
                    data: {
                        labels: uniqueApis,
                        datasets: [{
                            label: chartName.apiTotal,
                            data: apiTotal,
                            backgroundColor: 'rgba(153, 102, 255, 0.2)',
                            borderColor: 'rgba(153, 102, 255, 1)',
                            borderWidth: 1,
                        }],
                    },
                    options: {
                        scales: {
                            x: { title: { display: true, text: chartName.xNameApi } },
                            y: {
                                beginAtZero: true,
                                title: { display: true, text: chartName.yTotalReq },
                                ticks: { callback: value => value }
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
                            label: chartName.yNameSize,
                            data: groupedSizes,
                            backgroundColor: 'rgba(54, 162, 235, 0.2)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1,
                        }],
                    },
                    options: {
                        scales: {
                            x: { title: { display: true, text: chartName.xDate } },
                            y: {
                                beginAtZero: true,
                                title: { display: true, text: chartName.ySize },
                                ticks: { callback: value => value.toFixed(2) + ' KiB' }
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
                            label: chartName.yNameSize,
                            data: groupedResourceSizes,
                            backgroundColor: 'rgba(54, 162, 235, 0.2)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1,
                        }],
                    },
                    options: {
                        scales: {
                            x: { title: { display: true, text: chartName.resName } },
                            y: {
                                beginAtZero: true,
                                title: { display: true, text: chartName.ySize },
                                ticks: { callback: value => value.toFixed(2) + ' KiB' }
                            },
                        },
                    },
                });
            }

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
        }
    };
});