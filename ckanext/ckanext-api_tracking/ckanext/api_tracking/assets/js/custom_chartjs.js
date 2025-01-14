"use strict";

ckan.module('custom_chartjs', function ($) {
  return {
    initialize: function () {

      // Access some options passed to this JavaScript module by the calling
      // template.
      var chartTracking = this.options.chart_tracking;
      console.log("chartTracking: ", chartTracking);

      const chartTypeSelect = document.getElementById('chartType'); // Phần tử select cho kiểu biểu đồ
      const ctx = document.getElementById('statisticsChart').getContext('2d');
      const resourceChartCtx = document.getElementById('resourceChart').getContext('2d');

      let packageChartInstance = null;
      let resourceChartInstance = null;

      // Function to calculate the date range and total package views
      function updateTitle() {
        // Get start and end dates from all data
        const startDate = chartTracking[0]?.date_time || 'N/A';
        const endDate = chartTracking[chartTracking.length - 1]?.date_time || 'N/A';

        // Parse the start and end dates to ensure correct order
        const startDateObj = new Date(startDate);
        const endDateObj = new Date(endDate);

        // Swap dates if startDate is after endDate
        const formattedStartDate = startDateObj > endDateObj ? endDate : startDate;
        const formattedEndDate = startDateObj > endDateObj ? startDate : endDate;

        // Calculate total views for all data
        const totalViews = chartTracking.reduce((total, pkg) => total + pkg.package_view, 0);

        // Update the title with the date range and total views
        const titleElement = document.getElementById('packageTitle');
        titleElement.innerHTML = `From <strong>${formattedStartDate}</strong> to <strong>${formattedEndDate}</strong><br>Total Package Views: <strong>${totalViews}</strong>`;
      }

      // Create Package Chart
      function createPackageChart(displayData) {
        const labels = displayData.map(pkg => pkg.date_time);
        const viewsData = displayData.map(pkg => pkg.package_view);

        if (packageChartInstance) {
          packageChartInstance.destroy();
        }

        // Get the selected chart type from the dropdown
        const chartType = chartTypeSelect.value;

        packageChartInstance = new Chart(ctx, {
          type: chartType,  // Use the selected chart type
          data: {
            labels: labels,
            datasets: [
              {
                label: 'Package Views',
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
              y: {
                beginAtZero: true
              }
            }
          }
        });
      }

      // Show Resource Chart
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
                  label: 'Resource Downloads',
                  data: downloadData,
                  backgroundColor: 'rgba(153, 102, 255, 0.2)',
                  borderColor: 'rgba(153, 102, 255, 1)',
                  borderWidth: 1
                },
                {
                  label: 'Resource Views',
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
                y: {
                  beginAtZero: true
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

      // Merge resources with the same name
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

      // Hide Resource Chart
      function hideResourceChart() {
        document.getElementById('title_resource').style.display = 'none';
        document.getElementById('resourceChartContainer').style.display = 'none';
        document.getElementById('noResourceMessage').style.display = 'none';
      }

      // Update charts based on input
      function updateCharts() {
        // Create package chart
        createPackageChart(chartTracking);

        // Update the title with the date range and total views
        updateTitle();

        // Hide resource chart initially
        hideResourceChart();

        // Show the resource chart for the first package if clicked
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

      // Listen to the chart type change and update charts accordingly
      chartTypeSelect.addEventListener('change', updateCharts);

      // Initial update
      updateCharts();

    }
  };
});