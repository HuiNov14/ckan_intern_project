"use strict";

ckan.module('custom_chartjs', function ($) {
  return {
    initialize: function () {
      const x = this.options.x;
      const y = this.options.y;
      const from = this.options.from;
      const to = this.options.to;
      const sum = this.options.sum;
      const views = this.options.views;
      const download = this.options.download;
      const resviews = this.options.resviews;
      const resname = this.options.resname;
      var chartTracking = this.options.chart_tracking;
      console.log("chartTracking: ", chartTracking);

      const chartTypeSelect = document.getElementById('chartType');
      const ctx = document.getElementById('statisticsChart').getContext('2d');
      const resourceChartCtx = document.getElementById('resourceChart').getContext('2d');

      let packageChartInstance = null;
      let resourceChartInstance = null;

      function updateTitle() {
        const startDate = chartTracking[0]?.date_time || 'N/A';
        const endDate = chartTracking[chartTracking.length - 1]?.date_time || 'N/A';

        const startDateObj = new Date(startDate);
        const endDateObj = new Date(endDate);

        const formattedStartDate = startDateObj > endDateObj ? endDate : startDate;
        const formattedEndDate = startDateObj > endDateObj ? startDate : endDate;

        const totalViews = chartTracking.reduce((total, pkg) => total + pkg.package_view, 0);

        const titleElement = document.getElementById('packageTitle');
        titleElement.innerHTML = `<h5>${from} ${formattedStartDate} ${to} ${formattedEndDate}<br>${sum} ${totalViews}</h5>`;
      }

      function createPackageChart(displayData) {
        if (displayData.length === 0) return;

        // Kiểm tra xem tất cả dữ liệu có cùng một ngày không
        const uniqueDates = [...new Set(displayData.map(pkg => pkg.date_time.split(' ')[0]))];

        let labels, viewsData;

        if (uniqueDates.length === 1) {
          // Nếu chỉ có một ngày, gộp tổng số lượt xem
          const totalViews = displayData.reduce((total, pkg) => total + pkg.package_view, 0);
          labels = [uniqueDates[0]];
          viewsData = [totalViews];
        } else {
          // Nếu có nhiều ngày, giữ nguyên dữ liệu
          labels = displayData.map(pkg => pkg.date_time);
          viewsData = displayData.map(pkg => pkg.package_view);
        }

        if (packageChartInstance) {
          packageChartInstance.destroy();
        }

        const chartType = chartTypeSelect.value;

        packageChartInstance = new Chart(ctx, {
          type: chartType,
          data: {
            labels: labels,
            datasets: [
              {
                label: views,
                data: viewsData,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
              },
            ]
          },
          options: {
            responsive: true,
            scales: {
              x: {
                title: {
                  display: true,
                  text: x
                }
              },
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: views
                }
              }
            }
          }
        });
      }

      function showResourceChart(resources) {
        const mergedResources = mergeResources(resources);

        if (mergedResources.length > 0) {
          const resourceLabels = mergedResources.map(res => res.resource_name);
          const downloadData = mergedResources.map(res => res.download_count);
          const viewsData = mergedResources.map(res => res.resource_view);

          if (resourceChartInstance) {
            resourceChartInstance.destroy();
          }

          const chartType = chartTypeSelect.value;

          resourceChartInstance = new Chart(resourceChartCtx, {
            type: chartType,
            data: {
              labels: resourceLabels,
              datasets: [
                {
                  label: download,
                  data: downloadData,
                  backgroundColor: 'rgba(153, 102, 255, 0.2)',
                  borderColor: 'rgba(153, 102, 255, 1)',
                  borderWidth: 1
                },
                {
                  label: resviews,
                  data: viewsData,
                  backgroundColor: 'rgba(255, 159, 64, 0.2)',
                  borderColor: 'rgba(255, 159, 64, 1)',
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
                    text: resname
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

          document.getElementById('title_resource').style.display = 'block';
          document.getElementById('resourceChartContainer').style.display = 'block';
          document.getElementById('noResourceMessage').style.display = 'none';
        } else {
          hideResourceChart();
          document.getElementById('noResourceMessage').style.display = 'block';
        }
      }

      function mergeResources(resources) {
        const mergedResources = {};

        resources.forEach(res => {
          if (mergedResources[res.resource_name]) {
            mergedResources[res.resource_name].resource_view += res.resource_view;
            mergedResources[res.resource_name].download_count += res.download_count;
          } else {
            mergedResources[res.resource_name] = {
              resource_name: res.resource_name,
              resource_view: res.resource_view,
              download_count: res.download_count
            };
          }
        });

        return Object.values(mergedResources);
      }

      function hideResourceChart() {
        document.getElementById('title_resource').style.display = 'none';
        document.getElementById('resourceChartContainer').style.display = 'none';
        document.getElementById('noResourceMessage').style.display = 'none';
      }

      function updateCharts() {
        createPackageChart(chartTracking);
        updateTitle();
        hideResourceChart();

        ctx.canvas.addEventListener('click', function (e) {
          const activePoints = packageChartInstance.getElementsAtEventForMode(e, 'nearest', { intersect: true }, true);
          if (activePoints.length > 0) {
            const dataIndex = activePoints[0].index;
            const resources = chartTracking[dataIndex].include_resources;
            showResourceChart(resources);
          } else {
            hideResourceChart();
          }
        });
      }

      chartTypeSelect.addEventListener('change', updateCharts);
      updateCharts();
    }
  };
});
