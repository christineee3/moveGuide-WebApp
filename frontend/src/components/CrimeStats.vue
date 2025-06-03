<template>
  <div>
    <br>
    <b-row>
      <b-col cols="6">
      <h4>Categories</h4>
      <h4 v-if="!crimeData" style="color: maroon; font-style: italic;">Loading...</h4>
  
      <ChartComponent v-if="crimeCategoryData "  :chartType="'pie'" :chartData="crimeCategoryData" :chartOptions="chartOptions" class="chart-size"/>
    </b-col>
    <b-col cols="6">
        <h4>Outcomes</h4>
        <p style="font-size:10px" v-if="resolved">Percentage resolved:{{ resolved.toFixed(2) }}%</p>
        <ChartComponent v-if="crimeCategoryData" :chartType="'pie'" :chartData="outcomeCategoryData" :chartOptions="chartOptions" class="chart-size"/>
      </b-col>
</b-row>
  </div>

</template>

<script>
import axios from 'axios';
import ChartComponent from './ChartComponent.vue';

export default {
  watch:{
    latitude: 'fetch_crime_data',
    longitude: 'fetch_crime_data'

  },
  components:{
    ChartComponent
  },
  data() {
    return {
      crimeData: null,
      resolved: null,
      crimeCategoryData: null,
      outcomeCategoryData: null,
      chartOptions: {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }
    };
  },
  
  props: {
    latitude: {
      type: Number,
      required: true
    },
    longitude: {
      type: Number,
      required: true
    }
  },

  methods: {
    async fetch_crime_data() {
  try {
    
    const response = await axios.get(`${process.env.VUE_APP_BACKEND_URL}/get_crime_stats`, {
      params: { latitude: this.latitude, longitude: this.longitude }
    });

    const data = response.data;
    this.crimeData = data;

    // Save resolved percentage
    this.resolved = data.resolvedPercentage * 100;  // convert to %

    // Prepare crime category data for the pie chart
    this.crimeCategoryData = {
      labels: data.categoryCounts.map(item => item.category),
      datasets: [{
        data: data.categoryCounts.map(item => item.count),
        backgroundColor: [
          '#FF6347', '#FFD700', '#98FB98', '#00BFFF',
          '#D2691E', '#8A2BE2', '#DC143C', '#FF4500'
        ]
      }]
    };

    // Prepare outcome data for the pie chart
    this.outcomeCategoryData = {
      labels: data.outcomeCounts.map(item => item.outcome),
      datasets: [{
        data: data.outcomeCounts.map(item => item.count),
        backgroundColor: [
          '#FF6347', '#FFD700', '#98FB98', '#00BFFF',
          '#D2691E', '#8A2BE2', '#DC143C', '#FF4500'
        ]
      }]
    };

  } catch (error) {
    console.error("Error fetching crime data:", error);
  }
}

  },

  mounted() {
    this.fetch_crime_data();
  }
};
</script>
