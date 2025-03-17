<template>
  <div>
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';

// Register the necessary chart.js components
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

export default defineComponent({
  name: 'MyBarChart',
  components: {
    Bar,
  },
  props: {
    data: Object, // Accept the data as a prop
  },
  computed: {
    chartData() {
      return this.data || {}; // Return the data passed as a prop
    },
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          },
          tooltip:{
            enabled: true,
            mode: 'index',
            callbacks: {
              label: function (tooltipItem) {
                return tooltipItem.label + ': ' + tooltipItem.raw; // Customize the tooltip
              },
            },
          }          
        },
        scales: {
          x: {
            title: {
              display: true,
              text: '#Compositions', // Label for X-axis
            },
            beginAtZero: true 
          },
          y: {
            title: {
              display: true,
              text: '#EHRs', // Label for Y-axis
            },
            beginAtZero: true, // Start Y-axis at zero
          },
        },
      };
    },
  },
});
</script>
