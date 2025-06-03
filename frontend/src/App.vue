<template>
  
<b-container fluid>
  <h1>MoveGuide</h1>
   <!-- Form -->
  <EntryForm @data_fetched="handle_data" @data_fetched2="handle_data2"/>
</b-container>
<!-- Container if second location is entered -->
<b-container fluid v-if='locationData2'>
  <b-row >
    <b-col>
    <b-card :header=locationData.parliamentary_constituency border-variant="primary" header-class="header"> 
    <b-tabs fill >

      <b-tab title = "Accessiblity Indicators">
        <AIStats v-if="locationData" :locationData="locationData" :selectedTransportType="AISelectionsData.transportType" :timings="AISelectionsData.timings"></AIStats>
      </b-tab> 
      <b-tab title = "Schools" >
        <SchoolStats v-if='locationData' :lsoa='locationData.lsoa' :selectedSchoolTypes="schoolsData"/>  </b-tab>
      <b-tab title = "Crime" >
       <CrimeStats v-if='locationData' :latitude="locationData.latitude" :longitude="locationData.longitude"/>
      </b-tab>
      </b-tabs>
    </b-card>
  </b-col>
  <b-col>
    <b-card :header=locationData2.parliamentary_constituency border-variant="primary" header-class="header">
    <b-tabs fill >
     
      <b-tab title = "Accessiblity Indicators">
        <AIStats v-if="locationData2" :locationData="locationData2" :selectedTransportType="AISelectionsData.transportType" :timings="AISelectionsData.timings"></AIStats>
      </b-tab> 
      <b-tab title = "Schools" >
        <SchoolStats v-if='locationData2' :lsoa='locationData2.lsoa' :selectedSchoolTypes="schoolsData"/>  </b-tab>
      <b-tab title = "Crime" >
       <CrimeStats v-if='locationData2' :latitude="locationData2.latitude" :longitude="locationData2.longitude"/>
      </b-tab>
    </b-tabs>
    </b-card>
  </b-col>
  </b-row>
  <b-card header="Price prediction comparison" border-variant="primary" header-class="header" >
      <PricePrediction :locationData ="locationData" :locationData2 ="locationData2"  :propertySelections="propertySelectionsData" :date="dateData"></PricePrediction>
  </b-card>
  <b-row>
  </b-row>
</b-container>
<!-- Container if only first location is entered -->

<b-container v-else-if="locationData">
<b-row >
  <b-col>
    <b-card header="Price prediction" border-variant="primary" header-class="header" >
      <PricePrediction :locationData ="locationData" :propertySelections="propertySelectionsData" :date="dateData"></PricePrediction>
  </b-card>
  </b-col>

  <b-col>
    <b-card :header="`Statistics - ${locationData.parliamentary_constituency}`" border-variant="primary" header-class="header">

    <b-tabs fill >
      <b-tab title = "Accessiblity Indicators">
        <AIStats v-if="locationData" :locationData="locationData" :selectedTransportType="AISelectionsData.transportType" :timings="AISelectionsData.timings"></AIStats>
      </b-tab> 
    
      <b-tab title = "Schools" >
        <SchoolStats v-if='locationData' :lsoa='locationData.lsoa' :selectedSchoolTypes="schoolsData"/>  </b-tab>
      <b-tab title = "Crime" >
       <CrimeStats v-if='locationData' :latitude="locationData.latitude" :longitude="locationData.longitude"/>
      </b-tab>
    </b-tabs>
    </b-card>
  </b-col>
</b-row>
</b-container>

</template>

<script>
import AIStats from './components/AIStats.vue';
import CrimeStats from './components/CrimeStats.vue';
import EntryForm from './components/EntryForm.vue';
import SchoolStats from './components/SchoolStats.vue'
import PricePrediction from './components/PricePrediction.vue';


export default{
  components:{
    SchoolStats,
    AIStats,
    CrimeStats,
    EntryForm,
    PricePrediction,
  },
    data(){
        return {
            locationData: null,
            locationData2: null,
            propertySelectionsData: null,
            schoolsData: null,
            AISelectionsData: null,
            dateData: null,
        }
    },
    methods:{
        handle_data(location, propertySelections, schoolSelections, AISelections, date){
            this.locationData = location;
            this.propertySelectionsData = propertySelections;
            this.schoolsData = schoolSelections;
            this.AISelectionsData = AISelections;
            this.dateData = date;
            console.log(this.locationData, this.propertySelectionsData, this.schoolsData, this.AISelectionsData, this.date);
        },
        handle_data2(location2){
            this.locationData2 = location2;
            
        }
    }
}
</script>
<style>
h1 {
  font-size: 35px !important;
  font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif !important;
  margin-top: 15px !important;
  margin-bottom: 15px !important;
  font-weight: bold !important;
  color: #3451df !important;
 
}
h3 {
  font-size: 20px !important;
}

h4 {
  font-size: 15px !important;
}
body {
  background-color: #BDE6FF
  !important;
  font-family:'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif !important;
}




.container-fluid{
  padding: 10px !important;
}

.card{
 border-width: 3px !important;
}


.card .header{
  font-weight: bold !important;
}

</style>
