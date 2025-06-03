<template>
    <h4>{{ formattedDate }}</h4>
    <p v-if="predictionError" style="color: red; font-size: 12px;"> {{ predictionError }}</p>

    <h4 v-if="!loc1Price && !loc2Price" style="color: maroon; font-style: italic;">Loading...</h4>
    <h4 v-if="loc1Price"> {{locationData.postcode }}: {{ loc1Price }}</h4>
    <h4 v-if="loc2Price"> {{locationData2.postcode}}: {{ loc2Price }}</h4>
    <ChartComponent v-if="chartData" :chartType="'line'" :chartData="chartData" :chartOptions="chartOptions" class="linechart-size" />
</template>

<script>
import axios from 'axios';
import ChartComponent from './ChartComponent.vue';
export default{
    watch:{
        locationData:'fetch_chart_data',
        locationData2:'fetch_chart_data',
        propertySelections:'fetch_chart_data',
        date: 'fetch_chart_data'

    },
    components:{
        ChartComponent
    },
    props:{
        locationData:{
            type:Object,
            required:true
        },
        locationData2:{
            type:Object,
            required:false
        },
        propertySelections:{
            type:Object,
            required:true
        },
        date:{
            type:String,
            required:true
        }
    },
    data(){
        return {
            predictions: null,
            error:null,
            predictionError:null,

            chartData:null,
            chartOptions: {
                responsive: true,
                scales: {
                y: {
                    beginAtZero: false,
                    title: {
                    display: true,
                    text: 'Price (£)'},
                    ticks: {
                        stepSize: 15000,
                    }
                },
                x: {
                    title: {
                    display: true,
                    text: 'Date',
                    },
                    },
                    },
                    },
            formatedDate:null,
            loc1Price:null,
            loc2Price:null,
    };
    },
    computed:{
        formattedDate(){
            const date = new Date(this.date)
            const dateFormatter = new Intl.DateTimeFormat('en-GB',{year:'numeric',month:'long',day:'numeric'})
            return dateFormatter.format(date)
        }
    },
    methods:{
        async get_prediction(locationData){
            try{
                console.log("HRE:",this.locationData, this.propertySelectionsData)
                const response = await axios.get(`${process.env.VUE_APP_BACKEND_URL}/get_price_prediction`, {
                    params:{
                        postcode: locationData.postcode,
                        latitude: locationData.latitude,
                        longitude: locationData.longitude,
                        lsoa: locationData.lsoa,
                        propertySelections: this.propertySelections,
                        date: this.date
                    }
                });
                console.log("RESPONSE:",response.data)
                if (response.data.error){return { error: response.data.error };
                }
                else return { predictions: response.data.predictions }
            }
            catch (error) {
            console.error("Prediction fetch error:", error);
            return { error: "Insufficient data for chosen postcode to generate prediction"}}
            },
            async fetch_chart_data() {
                this.loc1Price=null;
                this.loc2Price=null;
                const promises = [];
                if (this.locationData) promises.push(this.get_prediction(this.locationData));
                if (this.locationData2) promises.push(this.get_prediction(this.locationData2));
                const results = await Promise.all(promises);
                const errorResult = results.find((r) => r.error);
                if (errorResult) {
                this.predictionError = errorResult.error;
                return; }

                const labels = results[0].predictions.map(p => new Date(p.date).toISOString().split('T')[0])
                const datasets = [];
                if (this.locationData) {
                    this.loc1Price = "£" + Math.round(results[0].predictions[2].predicted_price).toLocaleString();

                    datasets.push({
                        label: this.locationData.postcode,
                        data: results[0].predictions.map((prediction) => prediction.predicted_price),
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.2,
                    });}

                if (this.locationData2){
                    this.loc2Price ="£" + Math.round(results[1].predictions[2].predicted_price).toLocaleString();


                    datasets.push({
                        label: this.locationData2.postcode,
                        data: results[1].predictions.map((prediction)=> prediction.predicted_price),
                        borderColor:'rgb(245, 209, 66)',
                        tension:0.2

                })}

                    this.chartData={
                        labels,
                        datasets
                    }
    }
    
},
    mounted(){
        this.fetch_chart_data();
    },
  
}


</script>
