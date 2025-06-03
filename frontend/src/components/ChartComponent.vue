<template>
  <!-- Plots a the specified chart type -->
    <div>
      <BarChart v-if="chartType === 'bar'" :data="chartData" :options="chartOptions" />
      <DoughnutChart v-if="chartType === 'doughnut'" :data="chartData" :options="computedOptions" />
      <PieChart v-if="chartType === 'pie'" :data="chartData" :options="computedOptions" />
      <LineChart v-if="chartType === 'line'" :data="chartData" :options="chartOptions" />
    </div>
  </template>
  
  <script>
  import { Bar, Doughnut, Pie, Line } from 'vue-chartjs';
  import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, ArcElement, LineElement, CategoryScale, LinearScale,PointElement,  } from 'chart.js';
  
  ChartJS.register(Title, Tooltip, Legend, BarElement, ArcElement, LineElement, CategoryScale, LinearScale,PointElement, );
  
  export default {
    name: 'ChartComponent',
    components: {
      BarChart: Bar,
      DoughnutChart: Doughnut,
      PieChart: Pie,
      LineChart: Line
    },
    props: {
      chartType: {
        type: String,
        required: true
      },
      chartData: {
        type: Object,
        required: true
      },
      chartOptions: 
      {
        type: Object,
        default: () => {}
      }
    },
  computed: {
    computedOptions() {
    if (this.chartType === 'pie' || this.chartType === 'doughnut') {
        return {
          responsive: true,
          plugins: {
            legend: {
              position: 'bottom'
            },
            tooltip: {
              callbacks: {
                label: function (context) {
                  const label = context.label || '';
                  const value = context.parsed;
                  const data = context.dataset.data;
                  const total = data.reduce((sum, val) => sum + val, 0);
                  const percentage = ((value / total) * 100).toFixed(1);
                  return `${label}: ${value} (${percentage}%)`;
                }
              }
            }
          }
        };
      }
      // fallback to prop options
      return this.chartOptions;
    }
  }
}
  </script>

<style>
.chart-size {
    max-width: 400px;
    max-height: 400px;
    margin: 0 auto;
  }

.linechart-size {
    max-width: 700px;
    max-height: 700px;
    margin: 0 auto;
  }
  
  </style>