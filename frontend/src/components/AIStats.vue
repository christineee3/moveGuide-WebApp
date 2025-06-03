<template>

     <br>
     <!--Labels for LSOA and LADNM -->
     <h4>LSOA: {{locationData.lsoa_name }}</h4>

     <h4>LADNM: {{locationData.ladnm }}</h4>
<!-- Bar graph -->
    <ChartComponent v-if="chartData" :chartType="'bar'" :chartData="chartData" :chartOptions="chartOptions"/>

</template>

<script>
import axios from 'axios';
import ChartComponent from './ChartComponent.vue';
export default{
    watch:{
    locationData: 'fetch_AI_data',

  },
    components:{
        ChartComponent
    },
    props:{
        locationData:{
            type: Object,
            required: true
        },
        selectedTransportType:{
            type: String,
            required: true
        },
        timings:{
            type: Array,
            required:true
        }
    },
    data(){
        return {
        
            chartOptions: {
                responsive: true,
                plugins: {
                legend: {
                    position: 'bottom'
                        },
                        },
                    scales: {
                    x: {
                        stacked: true
                    },
                    y: {
                        stacked: true
                    }
                    }},


                graphLabels: ['gp_practices', 'hospitals', 'primary_schools', 'secondary_schools', 'supermarkets', 'nearest_main_bua', 'nearest_parks'],
                colours: ['#ff80cc', '#80b3ff', '#99e699', '#ffff99', '#e60073', '#0066cc', '#006633', '#ffcc00', '#d1d1d1', '#4d4d4d'],

                chartData:{labels: [], datasets:[]}
    }},

    methods:{
        // function to fetch AI data from PostgreSQL
        async fetch_AI_data(){
            try{
                const response = await axios.get(`${process.env.VUE_APP_BACKEND_URL}/get_AI_stats`,
                {params:{
                        lsoa: this.locationData.lsoa,
                        transportType: this.selectedTransportType,
                        timings:this.timings
                    }
                });
                this.AIdata = response.data;
                this.prepareData(this.AIdata)
                
                console.log(this.AIdata);

            }
            catch(error) { console.log(error);

        }

    },

    // Prepares the AI data to be displayed using chart,js datasets
    prepareData(data){
        const {lsoaAIStats, ladnmAIStats,} = data;
        let datasets =[],
        timings =this.timings;
        
        timings.forEach((time, index)=> {
            let data = this.graphLabels.map(label=>{
                if (label==='nearest_main_bua' || label==='nearest_parks'){
                    return 0;
                }
                return lsoaAIStats[label][time] || 0
            })
        
        datasets.push({
            label:`lsoa ${time}`,
            data:data,
            backgroundColor: this.colours[index],
            stack:'Stack 0'
        })
        });
        timings.forEach((time, index) => {
            let data = this.graphLabels.map(label =>{
                if (label ==='nearest_main_bua' || label==='nearest_parks'){
                    return 0
                }
                let key =`${label}_${time}`;
                return parseFloat(ladnmAIStats[key].avg) || 0;
            })
            datasets.push({
                label: `lad ${time}`,
                data: data,
                backgroundColor: this.colours[index +4],
                stack: 'Stack 1'
            })
        })
        datasets.push({
                label: 'Nearest Urban Centre',
                data: this.graphLabels.map(label =>
  label === 'nearest_main_bua'
    ? lsoaAIStats.nearest_main_bua === null 
      ? 1 
      : lsoaAIStats.nearest_main_bua
    : 0
)
,
                backgroundColor: this.colours[8],
                stack: 'Stack 0'
            })
            datasets.push({
                label: 'Nearest Park',
                data:this.graphLabels.map(label =>(label === 'nearest_parks'? lsoaAIStats.nearest_parks === 0 ? 1:lsoaAIStats.nearest_parks || 0 :0)),
                backgroundColor: this.colours[9],
                stack: 'Stack 0'
            })

            this.chartData = {
        labels: this.graphLabels,
        datasets: datasets,
      };
    
}},
mounted() {
    this.fetch_AI_data();
  }
}
</script>
