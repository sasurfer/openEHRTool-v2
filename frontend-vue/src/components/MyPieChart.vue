<template>
  <div>
    <Pie :data="chartData" :options="chartOptions" />
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import { Pie } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement } from 'chart.js';

// Register the necessary chart.js components
ChartJS.register(Title, Tooltip, Legend, ArcElement);

export default defineComponent({
  name: 'MyPieChart',
  components: {
    Pie,
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
            position: 'right',
          },
          tooltip: {
            enabled: true,
            mode: 'index',
            callbacks: {
              label: function (tooltipItem) {
                return tooltipItem.label+ ': ' + tooltipItem.raw + '%'; // Customize the tooltip
              },
            },
          },
        },
      };
    },
  },
});
</script>
