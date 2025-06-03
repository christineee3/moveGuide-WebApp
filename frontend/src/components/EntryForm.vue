<template>
    <div>
        <b-form @submit.prevent = "onSubmit" @reset="onReset"  class="p-0 mx-1 my-0 b-form">
            <b-form-row class=' b-form py-0'>
            <b-col><b-form-group id="postcode-group" label="Enter Postcode:" label-for="postcode"    label-class="font-weight-bold pt-0" label-size="sm">
                <b-form-input id="postcode" v-model="postcode" class="form-input-sm sm" required ></b-form-input>
                <p v-if="errorMessage" class="text-danger font-weight-bold mt-2">{{ errorMessage }}</p>

            </b-form-group></b-col>
            <b-col><b-form-group id="date-group" label="Enter date:" label-for="date" label-class="font-weight-bold pt-0" label-size="sm">
                <b-form-input type="date" id="date" v-model="date" class="form-input-sm sm" required></b-form-input>
                </b-form-group></b-col>
            <b-col>
                <b-form @submit.prevent = "onSubmit2">
                <b-form-group v-if='locationData' id="postcode2-group" label="Enter second postcode:" label-for="postcode2" label-class="font-weight-bold pt-0" label-size="sm">
                <b-form-input id="postcode2" v-model="postcode2" class="form-input-sm sm" ></b-form-input>
                <p v-if="errorMessage2" class="text-danger font-weight-bold mt-2">{{ errorMessage2 }}</p>
                <br>
                <b-button variant="primary"  type='submit'>Enter</b-button>
            </b-form-group>
        </b-form>
            </b-col>
        </b-form-row>
            
            <b-form-row class=' b-form py-0'>
            <b-col sm="auto"><b-form-group id="property-type-group" label="Property type:" label-for="property-type"  label-size="sm" class=" py-0">
                <b-form-select id="property-type" v-model="propertyForm.type" :options="propertyTypes" class="form-select-sm" required></b-form-select>
            </b-form-group></b-col>
            <b-col sm="auto" class="px-3"  ><b-form-group id="bedrooms-group" label="No. Bedrooms:" label-for="bedrooms" label-size="sm" >
                <b-form-select id="bedrooms" v-model="propertyForm.bedrooms" :options="[0,1,2,3,4,5,6]" class="form-select-sm" required></b-form-select>
            </b-form-group></b-col>

            <b-col sm="auto" class="px-3" ><b-form-group id="bathrooms-group" label="No. Bathrooms:" label-for="bathrooms" label-size="sm" >
                <b-form-select id="bathrooms" v-model="propertyForm.bathrooms" :options="[0,1,2,3,4,5,6]" class="form-select-sm" required></b-form-select>
            </b-form-group></b-col>

            <b-col sm="auto" class="px-3" ><b-form-group id="receptions-group" label="No. Receptions:" label-for="receptions"  label-size="sm">
                <b-form-select id="receptions" v-model="propertyForm.receptions" :options="[0,1,2,3,4]" class="form-select-sm" required></b-form-select>
            </b-form-group></b-col>
            </b-form-row>
            <b-form-group label="Pick amenities:" class="mb-0">
                <b-form-checkbox-group id="amenities" v-model="propertyForm.amenities" :options="amenityOptions" ></b-form-checkbox-group>
            </b-form-group>
            <b-form-group label="Select school type:">
                <b-form-checkbox-group id="schools" v-model="schoolTypes" :options="schoolOptions" ></b-form-checkbox-group>
            </b-form-group>
            <b-form-row>
                <b-col sm="auto"><b-form-group id="transport-type" label="Select transport type:" label-for="transport-type" label-size="sm" class=" py-0">
                <b-form-select id="transport-type" v-model="AIForm.transportType" :options="transportOptions" class="form-select-sm" required></b-form-select>
            </b-form-group></b-col>
            <b-col sm="auto"><b-form-group id="timings-group" label="Select time frames:" label-for="timings" label-size="sm" class=" py-0">
                <b-form-checkbox-group id="timings" v-model="AIForm.timings" :options="timingOptions" ></b-form-checkbox-group>
            </b-form-group></b-col>
            </b-form-row>
            <b-button variant="primary"  type='submit' :disabled="schoolTypes.length === 0 || AIForm.timings.length === 0">Submit</b-button>
            <b-button type ='reset'  >Reset</b-button>
        </b-form>
    </div>
</template>

<script>
import axios from 'axios';
export default{
    name: 'EntryForm',
    data(){
        return {
            errorMessage: '',
            errorMessage2: '',
            postcode2: null,
            locationData2:null,
            postcode: null,
            date:null,
            locationData: null,
            propertyForm: {
                type: null,
                bedrooms: null,
                bathrooms: null,
                receptions: null,
                amenities: []
            },
            schoolTypes:[],
            AIForm:{
                transportType:null,
                timings:[]
            },
            propertyTypes: ["Detached house", "Terraced house", "Bungalow","Detached bungalow","Flat","Maisonette"],
            amenityOptions:['Conservatory','Off street parking','Driveway','Swimming pool','Garage'] ,
            schoolOptions: ["Nursery", "Primary", "Secondary","Special"],
            transportOptions:[{text:"bicycle", value:'bicycle'},{text:'walk', value:"walk"},{text:'public transport', value:"pt"}],
            timingOptions:[{text:"15 mins", value:15},{text:'30 mins', value:30},{text:'45 mins', value:45}, {text:'60 mins', value:60}],

        }
    },
    methods:{
        async onSubmit(){
            try{
                this.errorMessage=""
                const response = await axios.get(`${process.env.VUE_APP_BACKEND_URL}/get_location?postcode=${this.postcode}`)
                this.locationData = response.data;
                this.$emit("data_fetched",this.locationData, this.propertyForm, this.schoolTypes, this.AIForm,this.date)
            }
            catch(error) { 
            this.errorMessage="Invalid postcode, please try again",
            console.log(error);
        }
    },
    async onSubmit2(){
        
        try{
            this.errorMessage2=""
            const response = await axios.get(`${process.env.VUE_APP_BACKEND_URL}/get_location?postcode=${this.postcode2}`)
            this.locationData2 = response.data;
            console.log(this.locationData2, this.propertyForm, this.schoolTypes, this.AIForm)
            this.$emit("data_fetched2",this.locationData2, this.propertyForm, this.schoolTypes, this.AIForm)
        }
        catch(error) {
            this.errorMessage2="Invalid postcode, please try again",
            console.log(error);
    }
    },
    onReset(){
            try{
                this.postcode2 = null
                this.locationData2 = null
                this.postcode = null
                this.locationData = null
                this.propertyForm = {
                    type: null,
                bedrooms: 0,
                bathrooms: 0,
                receptions: 0,
                amenities: []
                }
                this.schoolTypes=[],
                this.transportType=null
                this.AIForm = {
                    transportType:null,
                    timings:[]
                },
                this.date = null 
            }
            catch(error) { console.log(error);
        }
    }
}}
</script>
<style>

.b-form{
    font-size: 12px !important;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    padding-top: 2px !important;
    padding-bottom: 0 !important;
    font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif !important;
}

.form-input-sm{
    width: 200px !important;
    height:25px;

}
.form-select-sm{
    height:25px;
    width: 200px;
    font-size: 12px !important;

}
.form-select-num{
    height:25px;
    width: 120px !important;
    font-size: 12px !important;
}



.b-form .btn{
    padding: 5px !important;
    width: 90px !important;
    font-size: 12px !important;
}

</style>