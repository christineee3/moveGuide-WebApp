<template>
    <div class="container">
    <!-- <h3>School Statistics</h3> -->
    <br>

    <b-row>
      <b-col>
      <h4>Local authority district: {{ localLocation }}</h4>
      <ChartComponent v-if='localData' :chartType="'doughnut'" :chartData="localData" :chartOptions="chartOptions" class="chart-size"/>
    </b-col>
    <b-col>
        <h4> Region: {{ regionalLocation }}</h4>
        <ChartComponent v-if='regionalData' :chartType="'doughnut'" :chartData="regionalData" :chartOptions="chartOptions" class="chart-size"/>
      </b-col>
</b-row>
  </div>

    
</template>
<script>
import axios from 'axios';
import ChartComponent from './ChartComponent.vue';

export default {
  watch: {
    lsoa: 'fetch_school_data',
    selectedSchoolTypes: 'fetch_school_data'
  },
  components: {
    ChartComponent
  },
  props: {
    lsoa: {
      type: String,
      required: true
    },
    selectedSchoolTypes: {
      type: Array,
      required: true
    }
  },
 
  data() {
    return {
      schoolData: null,
      localData: null,
      regionalData: null,
      localLocation: null,
      regionalLocation: null,
      graphColours:['#32CD32', '#FFD700','#FFA500', '#FF0000'],
      graphLabels:['Outstanding','Good','Requires improvement','Inadequate'],
      chartOptions: {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom'
          }
        },
        cutoutPercentage: 70 
      }
    };
  },
  methods: {
  async fetch_school_data() {
    try {
      // Fetch data from the API
      const response = await axios.get(`${process.env.VUE_APP_BACKEND_URL}/get_school_stats`, {
        params: {
          lsoa: this.lsoa,
          schoolTypes: this.selectedSchoolTypes
        }
      });
      console.log(response)

      this.schoolData = response.data;

      // Dynamically get school types
      const schoolTypes = Object.keys(this.schoolData);

      // Prepare chart data for local and regional stats
      this.localData = {
        labels: this.graphLabels,
        datasets: []
      };

      this.regionalData = {
        labels: this.graphLabels,
        datasets: []
      };

      // Iterate over each school type and prepare datasets
      schoolTypes.forEach(schoolType => {
        const stats = this.schoolData[schoolType];

        // Process local authority stats
        this.localData.datasets.push({
          label: `${schoolType} Local Authority`,
          data: stats.ladnmSchoolStats.slice(1), // Skip the location name (first element)
          backgroundColor: this.graphColours,
          borderColor: 'white',
          borderWidth: 2
        });

        // Process regional stats
        this.regionalData.datasets.push({
          label: `${schoolType} Region`,
          data: stats.regionSchoolStats.slice(1),
          backgroundColor: this.graphColours,
          borderColor: 'white',
          borderWidth: 2
        });
      });

      // Set the location names for the labels
      const firstSchoolType = schoolTypes[0];
      this.localLocation = this.schoolData[firstSchoolType].ladnmSchoolStats[0];
      this.regionalLocation = this.schoolData[firstSchoolType].regionSchoolStats[0];

    } catch (error) {
      console.error('Error fetching school data:', error);
    }
  }
  
},

  mounted() {
    this.fetch_school_data();
  }
};
</script>




