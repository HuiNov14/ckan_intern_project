"use strict";

ckan.module('custom_chartjs', function ($) {
  return {
    initialize: function () {
      const nameStatic = this.options.name_static;
      console.log("nameStatic: ", nameStatic);
      var chartTracking = this.options.chart_tracking;

      if (!chartTracking || chartTracking.length === 0) {
        document.getElementById('noResourceMessage').style.display = 'block';
        return;
      }
      const chartTypeSelect = document.getElementById('chartType');
      const ctx = document.getElementById('statisticsChart').getContext('2d');
      const resourceChartCtx = document.getElementById('resourceChart').getContext('2d');

      let packageChartInstance = null;
      let resourceChartInstance = null;

      function updateTitle(groupedData) {
        const labels = Object.keys(groupedData);
        if (labels.length === 0) return;

        const formattedStartDate = labels[0];
        const formattedEndDate = labels[labels.length - 1];

        const totalViews = Object.values(groupedData).reduce((total, viewCount) => total + viewCount, 0);

        const titleElement = document.getElementById('packageTitle');
        titleElement.innerHTML = `<h5>${nameStatic.from} ${formattedStartDate} ${nameStatic.to} ${formattedEndDate}<br>${nameStatic.total_package_view} ${totalViews}</h5>`;
      }

      function groupViewsByDate(data) {
        const groupedData = {};

        data.forEach(pkg => {
          const dateKey = pkg.date_time.split(' ')[0]; // Lấy ngày (YYYY-MM-DD)
          groupedData[dateKey] = (groupedData[dateKey] || 0) + pkg.package_view;
        });

        return groupedData;
      }

      function createPackageChart(displayData) {
        if (displayData.length === 0) return;

        const groupedData = groupViewsByDate(displayData);
        const labels = Object.keys(groupedData);
        const viewsData = Object.values(groupedData);

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
                label: nameStatic.package_view,
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
                  text: nameStatic.x
                }
              },
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: nameStatic.package_view
                }
              }
            }
          }
        });

        updateTitle(groupedData);
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
                  label: nameStatic.resource_download,
                  data: downloadData,
                  backgroundColor: 'rgba(153, 102, 255, 0.2)',
                  borderColor: 'rgba(153, 102, 255, 1)',
                  borderWidth: 1
                },
                {
                  label: nameStatic.resource_view,
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
                    text: nameStatic.resource_name
                  }
                },
                y: {
                  beginAtZero: true,
                  title: {
                    display: true,
                    text: nameStatic.y
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
        hideResourceChart();

        ctx.canvas.addEventListener('click', function (e) {
          const activePoints = packageChartInstance.getElementsAtEventForMode(e, 'nearest', { intersect: true }, true);
          if (activePoints.length > 0) {
            const dataIndex = activePoints[0].index;
            const selectedDate = packageChartInstance.data.labels[dataIndex];

            const resources = chartTracking
              .filter(pkg => pkg.date_time.startsWith(selectedDate))
              .flatMap(pkg => pkg.include_resources);

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
