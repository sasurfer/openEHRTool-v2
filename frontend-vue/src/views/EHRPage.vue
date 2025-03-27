<template>
  <div id="app">
    <!-- You can have a global navbar, footer, or other common layout elements here -->
    <Sidebar @open-user-info="openUserInfo" />
    <rsidebar @open-ehr-info="openEHRInfo" @open-template-info="openTemplateInfo"
      @open-composition-info="openCompositionInfo" @open-aql-info="openAQLInfo" />
    <UserInfoModal v-if="isUserInfoVisible" :isVisible="isUserInfoVisible" :user="user" @close-modal="closeModal"
      @logout="logout" />

      <div class="method-selection-zone">
        <h3><i>EHR Methods</i></h3>
      <!-- Only show methods if it's not the Home page -->
      <!-- <div v-if="!isHomePage"> -->
        <div v-for="(method, index) in currentMethods" :key="index" class="method-item" :style="getMethodStyle(index)">
          <button @click="selectMethod(index)">{{ method.label }}</button>
        </div>
      <!-- </div> -->
    </div>


    <div class="main-content">
      <!-- Your main content goes here -->
 
      <!-- Method Actions Section -->
      <div v-if="selectedMethod !== null" class="actions">
        <div class="method-title">
          <h2>{{ currentMethods[selectedMethod].label }}</h2>
        </div>"


      <!-- Parameter Form Zone -->
      <div class="parameter-form">
        <div class="parameters-title">
        <h3>Input Parameters</h3>
        </div>
        <form @submit.prevent="submitForm">
          <div v-for="(param, index) in currentParams" :key="index" class="form-group">
            <label>{{ param.label }}:</label>
            <input v-model="param.value" :type="param.type" :placeholder="param.placeholder" />
          </div>

          <div v-if="currentFile" class="file-input">
            <label>Upload File:</label>
            <input type="file" @change="handleFileUpload" />
          </div>
        
          <div class="action-group">
            <div v-for="(action, index) in methodActions" :key="index" class="action-button">
                <!-- <button type="submit">{{ action.label }}</button> -->
          <button @click="executeAction(action.action)">{{ action.label }}</button>
             </div>
          </div>
        </form>
      </div>

     <!-- Separator Line between Top and Results -->
     <div class="separator"></div>

      <!-- Results Section -->
      <div class="results-section">
        <h3>Results</h3>
        <div class="results-container">
        <div class="results-content">
          <pre>{{ results }}</pre>
        </div>
              <div v-if="isLoading" class="flex justify-center items-center ehr-spinner">
                <Circle4Spinner  :size="'50px'" :background="'#48f791'"></Circle4Spinner>
              </div>
      </div>
      </div>
    </div>
    <div v-else class="no-method">
      <svg width="40" height="40" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg" transform="translate(0, 5)">
        <path d="M40 25H10m0 0l7-7m-7 7l7 7" stroke="black" stroke-width="3" fill="none"/>
      </svg>
      <p>Please select a method from the left methods menu.</p>

    </div>
    </div>
 
    
    <EHRInfoModal v-if="isEHRInfoVisible" :isVisible="isEHRInfoVisible" :ehrData="ehrData"
      @close-ehr-modal="closeEHRInfo" :isLoading="isLoadingEHR" />
    <TemplateInfoModal v-if="isTemplateInfoVisible" :isVisible="isTemplateInfoVisible" :templateData="templateData"
      @close-template-modal="closeTemplateInfo" 
      :isLoading="isLoadingTemplate" />
    <CompositionInfoModal v-if="isCompositionInfoVisible" :isVisible="isCompositionInfoVisible"
      :compositionData="compositionData" @close-composition-modal="closeCompositionInfo" 
      :isLoading="isLoadingComposition" />
    <AQLInfoModal v-if="isAQLInfoVisible" :isVisible="isAQLInfoVisible" :aqlData="aqlData"
      @close-aql-modal="closeAQLInfo" 
      :isLoading="isLoadingAQL" />
  </div>
</template>


<script>
import Sidebar from '@/components/LeftSidebar.vue';
import UserInfoModal from '@/components/UserInfoModal.vue';
import rsidebar from '@/components/RightSidebar.vue';
import EHRInfoModal from '@/components/EHRInfoModal.vue';
import TemplateInfoModal from '@/components/TemplateInfoModal.vue';
import CompositionInfoModal from '@/components/CompositionInfoModal.vue';
import AQLInfoModal from '@/components/AQLInfoModal.vue';
import { defineComponent } from "vue";
import axios from 'axios';  // Import axios for making HTTP requests
import Circle4Spinner from '@/components/ui/Circle4Spinner.vue';


export default defineComponent({
  name: 'EHRPage',
  components: {
    Sidebar,
    UserInfoModal,
    rsidebar,
    EHRInfoModal,
    TemplateInfoModal,
    CompositionInfoModal,
    AQLInfoModal,
    Circle4Spinner,
  },
  data() {
    return {
      //for user info modal
      isLoading:false,
      isUserInfoVisible: false,
      user: {
        name: localStorage.getItem("username") || "Can not find user",
      },
      //for ehr info modal
      isEHRInfoVisible: false,
      ehrData: [],
      //for template info modal
      isTemplateInfoVisible: false,
      templateData: [],
      //for composition info modal
      isCompositionInfoVisible: false,
      compositionData: [],
      //for aql info modal
      isAQLInfoVisible: false,
      aqlData: [],
      selectedMethod: null,
      methodActions: [],
      currentMethods: [],
      currentParams: [],
      currentFile: false,
      results: null,      
      isLoadingEHR: false,
      isLoadingTemplate: false,
      isLoadingComposition: false,
      isLoadingAQL: false,  
      ehrid : '',
      subjectid : '',
      subjectnamespace : '',
    };
  },
  mounted() {
    // Fetch data when the component is first mounted
    this.fetchEHRdata();
    this.fetchTemplateData();
    this.fetchCompositionData();
    this.fetchAQLData();
    this.currentMethods=this.getMethodsForEHR();
  },
  watch: {
    '$route'() {
      // Fetch data when the route changes
      this.fetchEHRdata();
      this.fetchTemplateData();
      this.fetchCompositionData();
      this.fetchAQLData();
    },
  },
  methods: {
    // Get dynamic styles for the method
    getMethodStyle(index) {
      return index === this.selectedMethod
        ? { backgroundColor: '#bad489', color: 'white' } : {};
    },
    selectMethod(index) {
      this.selectedMethod = index;
      this.methodActions = this.getActionsForMethod(index);
      this.currentParams = this.getParamsForMethod(index);
      this.results = null; // Reset results
    },
    getMethodsForEHR() {
      const methods = {
        'methods':[
          { label: 'Get EHR by EHRid' },
          { label: 'Get EHR by SubjectId, SubjectNameSpace' },
          { label: 'Post EHR with/without EHRid specified' },
          { label: 'Post EHR with SubjectId, SubjectNameSpace specified' },
        ]
      };
      return methods['methods'] || [];
    },

    // Get actions associated with the selected method
    getActionsForMethod(index) {
      const actions = [
        [{label : 'Clear Input',action: 'clear_ehrid'},{ label: 'Submit',action:'submit_ehrid' }],
        [{label : 'Clear Input',action: 'clear_sid_sns'},{ label: 'Submit',action: 'submit_sid_sns' }],
        [{ label: 'Clear Input',action : 'clear_ehrid'}, { label: 'Submit', action: 'submit_ehrid_post' }],
      ];
      return actions[index] || [];
    },
    // Get input parameters for the selected method
    getParamsForMethod(index) {
      const params = [
        [
          { label: 'EHRid', value: '', type: 'text', placeholder : "56e46cce-d8c9-4db8-940b-ee3db170a646" },
        ],
        [
          { label: 'SubjectId', value: '', type: 'text' , placeholder : "Patient1234"},
          { label: 'SubjectNameSpace', value: '', type: 'text', placeholder : "Acme" },
        ],
        [
          { label: 'EHRid (optional)', value: '', type: 'text', placeholder : "56e46cce-d8c9-4db8-940b-ee3db170a646" },
        ],
      ];
      return params[index] || [];
    },

    // Handle action button click
    async executeAction(action) {
      this.results=null
      if (action=='submit_ehrid') //get ehr by ehrid
      {
        const ehrid= this.currentParams.find(p => p.label === 'EHRid');
        console.log(ehrid);
        if (ehrid.value) 
        {         
          console.log('ehrid is',ehrid.value);
          try {
          const ehrResults= await this.getehrbyehrid(ehrid.value);
          console.log('results',ehrResults);
          this.results=JSON.stringify(ehrResults,null,2);
          }
          catch (error) {
          console.error("Error in executeAction:", error);
          this.results = `Error: ${error.message}`;
          }
        }else{
          this.results='EHRid is required';
        }  
      } else if (action=='submit_sid_sns')//get ehr by subjectid and subjectnamespace
      {
        const subjectid= this.currentParams.find(p => p.label === 'SubjectId');
        const subjectnamespace= this.currentParams.find(p => p.label === 'SubjectNameSpace');
        if (subjectid.value && subjectnamespace.value) 
        { 
          try{
          const ehrResults= await this.getehrbysidandsns(subjectid.value,subjectnamespace.value);
          console.log('results',ehrResults);
          this.results=JSON.stringify(ehrResults,null,2);
          }
          catch (error) {
            console.error("Error in executeAction:", error);
            this.results = `Error: ${error.message}`;
          }
        }  else{
          this.results='SubjectId and SubjectNameSpace are required';
        } 
      } else if (action=='clear_ehrid' || action=='clear_sid_sns'){
        this.currentParams.forEach(param => {param.value = '';});
        this.results=null;
      } else if (action == 'submit_ehrid_post') {
        const ehrid= this.currentParams.find(p => p.label === 'EHRid (optional)');
        console.log('ehrid is',ehrid?.value);
        this.ehrid= ehrid?.value || "";
        console.log('ehrid is',this.ehrid);
        try {
        const ehrResults= await this.postehrbyehrid(this.ehrid);
        console.log('results',ehrResults);
        this.results=JSON.stringify(ehrResults,null,2);
        }
        catch (error) {
        console.error("Error in executeAction:", error);
        this.results = `Error: ${error.message}`;
        }
        
      }
      // } else if (index==2){
      //   this.results = `Result for ${this.methodActions[index].label} will appear here.`;
      // } else if (index==3){
      //   this.results = `Result for ${this.methodActions[index].label} will appear here.`;
      // } else if (index==4){
      //   this.results = `Result for ${this.methodActions[index].label} will appear here.`;
        else{
        this.results =null;
      }
      
    },

    // Submit form with parameter values
    // submitForm() {
    //   console.log("Form submitted");
    //   this.executeAction(this.selectedMethod);
    // },

    // Handle file upload
    handleFileUpload(event) {
      const file = event.target.files[0];
      console.log('File selected:', file);
      this.currentFile = file.name;
    },

    //for user info modal
    openUserInfo() {
      this.isUserInfoVisible = true;
    },
    closeModal() {
      this.isUserInfoVisible = false;
    },
    logout() {
      this.isUserInfoVisible = false;
      localStorage.removeItem("authToken"); // Remove stored token
      localStorage.removeItem("username"); // Remove stored username
      localStorage.removeItem("isAuthenticated"); // Remove authentication flag
      localStorage.clear(); // Clear local storage
      sessionStorage.clear(); // Clear session storage
      this.$router.push("/login"); // Redirect to login page
    },
    //for ehr info modal
    async fetchEHRdata() {
      try {
        this.isLoadingEHR = true;
        const response = await axios.get('http://127.0.0.1:5000/rsidebar/ehrs',
          { method: 'GET', headers: { 'Authorization': `Bearer ${localStorage.getItem("authToken")}` }, },
          { timeout: 2000000 }); 
        if (response.status === 401) {
          console.error("Unauthorized access. Please login again.");
          this.logout();
          return
        }
        if (response.status != 200) {
          console.error("Error fetching data:", response);
          return;
        }
        console.log(response)
        const ehrData = response.data.ehrs;
        this.ehrData = ehrData;
        console.log('this.ehrData', this.ehrData);
      } catch (error) {
        console.error("Error fetching data:", error);
        if (error?.response?.status) {
          if (error.response.status === 401) {
            console.error("Unauthorized access. Please login again.");
            this.logout();
            return
          }
        }
      }
      finally {
        this.isLoadingEHR = false;
      }
      // this.ehrData = ['ehr1', 'ehr2', 'ehr3', 'ehr4', 'ehr5', 'ehr6', 'ehr7', 'ehr8', 'ehr9', 'ehr10'];
      return this.ehrData;
    },
    toggleEHRInfoModal() {
      this.isEHRInfoVisible = !this.isEHRInfoVisible;
    },
    async openEHRInfo() {
      this.toggleEHRInfoModal()
      //this.isEHRInfoVisible = true;
      this.ehrData = await this.fetchEHRdata();
    },
    closeEHRInfo() {
      this.isEHRInfoVisible = false;
    },
    //for template info modal
    async fetchTemplateData() {
      try {
        this.isLoadingTemplate = true;
        const response = await axios.get('http://127.0.0.1:5000/rsidebar/templates',
          { method: 'GET', headers: { 'Authorization': `Bearer ${localStorage.getItem("authToken")}` }, },
          { timeout: 2000000 }); 
        if (response.status === 401) {
          console.error("Unauthorized access. Please login again.");
          this.logout();
          return
        }
        if (response.status != 200) {
          console.error("Error fetching templates:", response);
          return;
        }
        // Assuming the backend returns data in this structure
        console.log(response)
        const templateData = response.data.templates;
        this.templateData = templateData;
        console.log('this.templateData', this.templateData); 
      } catch (error) {
        console.error("Error fetching templates:", error);
        if (error?.response?.status) {
          if (error.response.status === 401) {
            console.error("Unauthorized access. Please login again.");
            this.logout();
            return
          }
        }
      }
      finally {
        this.isLoadingTemplate = false;
      }
      //       this.templateData = [{ 'template_id': 'template1', 'concept': 'template1', 'archetype_id': 'openEHR-EHR-COMPOSITION.report.v1', 'created_timestamp': '2024-12-19T11:06:33.781Z' },
      // { 'template_id': 'template2', 'concept': 'template2', 'archetype_id': 'openEHR-EHR-COMPOSITION.report.v1', 'created_timestamp': '2024-12-19T11:06:33.781Z' },
      // { 'template_id': 'template3', 'concept': 'template3', 'archetype_id': 'openEHR-EHR-COMPOSITION.report.v1', 'created_timestamp': '2024-12-19T11:06:33.781Z' },
      // { 'template_id': 'template4', 'concept': 'template4', 'archetype_id': 'openEHR-EHR-COMPOSITION.report.v1', 'created_timestamp': '2024-12-19T11:06:33.781Z' },
      // { 'template_id': 'template5', 'concept': 'template5', 'archetype_id': 'openEHR-EHR-COMPOSITION.report.v1', 'created_timestamp': '2024-12-19T11:06:33.781Z' },
      // { 'template_id': 'template6', 'concept': 'template6', 'archetype_id': 'openEHR-EHR-COMPOSITION.report.v1', 'created_timestamp': '2024-12-19T11:06:33.781Z' },
      // { 'template_id': 'template7', 'concept': 'template7', 'archetype_id': 'openEHR-EHR-COMPOSITION.report.v1', 'created_timestamp': '2024-12-19T11:06:33.781Z' },
      // { 'template_id': 'template8', 'concept': 'template8', 'archetype_id': 'openEHR-EHR-COMPOSITION.report.v1', 'created_timestamp': '2024-12-19T11:06:33.781Z' },
      // { 'template_id': 'template9', 'concept': 'template9', 'archetype_id': 'openEHR-EHR-COMPOSITION.report.v1', 'created_timestamp': '2024-12-19T11:06:33.781Z' },
      // { 'template_id': 'template10', 'concept': 'template10', 'archetype_id': 'openEHR-EHR-COMPOSITION.report.v1', 'created_timestamp': '2024-12-19T11:06:33.781Z' }];
      return this.templateData;
    },
    toggleTemplateInfoModal() {
      this.isTemplateInfoVisible = !this.isTemplateInfoVisible;
    },
    async openTemplateInfo() {
      this.toggleTemplateInfoModal()
      //this.isTemplateInfoVisible = true;
      this.templateData = await this.fetchTemplateData();
    },
    closeTemplateInfo() {
      this.isTemplateInfoVisible = false;
    },
    //for composition info modal
    toggleCompositionInfoModal() {
      this.isCompositionInfoVisible = !this.isCompositionInfoVisible;
    },
    
      // Fetch composition data here
    async fetchCompositionData() {
      try {
        this.isLoadingComposition = true;
        const response = await axios.get('http://127.0.0.1:5000/rsidebar/compositions',
          { method: 'GET', headers: { 'Authorization': `Bearer ${localStorage.getItem("authToken")}` }, },
          { timeout: 2000000 }); 
        if (response.status === 401) {
          console.error("Unauthorized access. Please login again.");
          this.logout();
          return
        }
        if (response.status != 200) {
          console.error("Error fetching compositions:", response);
          return;
        }
        console.log(response)
        const compositionData = response.data.compositions;
        this.compositionData = compositionData;
        console.log('this.compositionData', this.compositionData); 
      } catch (error) {
        console.error("Error fetching compositions:", error);
        if (error?.response?.status) {
          if (error.response.status === 401) {
            console.error("Unauthorized access. Please login again.");
            this.logout();
            return
          }
        }
      } finally {
        this.isLoadingComposition = false;
      }        
//      this.compositionData = ['composition1', 'composition2', 'composition3', 'composition4', 'composition5', 'composition6', 'composition7', 'composition8', 'composition9', 'composition10'];
      return this.compositionData;
    },
    async openCompositionInfo() {
      this.toggleCompositionInfoModal()
      //this.isCompositionInfoVisible = true;
      this.compositionData = await this.fetchCompositionData();
    },
    closeCompositionInfo() {
      this.isCompositionInfoVisible = false;
    },
    //for aql info modal
    toggleAQLInfoModal() {
      this.isAQLInfoVisible = !this.isAQLInfoVisible;
    },
    async fetchAQLData() {
      // Fetch AQL data here
      try {
        this.isLoadingAQL = true;
        const response = await axios.get('http://127.0.0.1:5000/rsidebar/queries',
          { method: 'GET', headers: { 'Authorization': `Bearer ${localStorage.getItem("authToken")}` }, },
          { timeout: 2000000 }); 
        if (response.status === 401) {
          console.error("Unauthorized access. Please login again.");
          this.logout();
          return
        }
        if (response.status != 200) {
          console.error("Error fetching queries:", response);
          return;
        }
        const aqlData = response.data.queries;
        this.aqlData = aqlData;
        console.log('this.aqlData', this.aqlData); 
      } catch (error) {
        console.error("Error fetching queries:", error);
        if (error?.response?.status) {
          if (error.response.status === 401) {
            console.error("Unauthorized access. Please login again.");
            this.logout();
            return
          }
        }
      }    
      finally {
        this.isLoadingAQL = false;
      }   
      // this.aqlData = [{ 'name': 'org.ehrbase.local:aql1', 'version': '1.0.0', 'saved': '2025-01-08T12:25:24.138234Z' },
      // { 'name': 'org.ehrbase.local:aql2', 'version': '1.0.0', 'saved': '2025-01-08T12:25:24.138234Z' },
      // { 'name': 'org.ehrbase.local:aql3', 'version': '1.0.0', 'saved': '2025-01-08T12:25:24.138234Z' },
      // { 'name': 'org.ehrbase.local:aql4', 'version': '1.0.0', 'saved': '2025-01-08T12:25:24.138234Z' },
      // { 'name': 'org.ehrbase.local:aql5', 'version': '1.0.0', 'saved': '2025-01-08T12:25:24.138234Z' },
      // { 'name': 'org.ehrbase.local:aql6', 'version': '1.0.0', 'saved': '2025-01-08T12:25:24.138234Z' },
      // { 'name': 'org.ehrbase.local:aql7', 'version': '1.0.0', 'saved': '2025-01-08T12:25:24.138234Z' },
      // { 'name': 'org.ehrbase.local:aql8', 'version': '1.0.0', 'saved': '2025-01-08T12:25:24.138234Z' },
      // { 'name': 'org.ehrbase.local:aql9', 'version': '1.0.0', 'saved': '2025-01-08T12:25:24.138234Z' },
      // { 'name': 'org.ehrbase.local:aql10', 'version': '1.0.0', 'saved': '2025-01-08T12:25:24.138234Z' }
      // ];
      return this.aqlData;
    },
    async openAQLInfo() {
      this.toggleAQLInfoModal()
      //this.isAQLInfoVisible = true;
      this.aqlData = await this.fetchAQLData();
    },
    closeAQLInfo() {
      this.isAQLInfoVisible = false;
    },
    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    },
    async getehrbyehrid(ehrid) {
      console.log('inside getehrbyehrid')
      console.log(ehrid)
      console.log(localStorage.getItem("authToken"))
      this.isLoading=true;
      // await this.sleep(5000);
      try {
        console.log('before get')
        const response = await axios.get(`http://127.0.0.1:5000/ehr/${ehrid}`,
        {
          headers :  { 'Authorization': `Bearer ${localStorage.getItem("authToken")}`
           },
          timeout: 2000000,
          });
          return response.data.ehr;
        } 
      catch (error) {
        console.error("Error in getehrbyehrid:", error);
        if (error?.response?.status) {
          if (error.response.status === 401) {
            console.error("Unauthorized access. Please login again.");
            this.logout();
            return
          }      
          if (error.response.status == 404) {
            return error.response.data;
          }    
        
          if (error.response.status === 500) {
            return error.response.data;
        // throw { status: 500, message: "Server error" };
          }
          throw { status: 500, message: `An unexpected error occurred ${error.response.status}` };
        }
      } finally {
        this.isLoading=false;
      }
    }, 
    async getehrbysidandsns(subjectid,subjectnamespace) {
      console.log('inside getehrbysidandsns')
      console.log(localStorage.getItem("authToken"))
      console.log(subjectid)
      console.log(subjectnamespace)
      this.isLoading=true;
      // await this.sleep(5000);
      try {
        console.log('before get')
        const response = await axios.get(`http://127.0.0.1:5000/ehr/subjectid/${subjectid}/subjectnamespace/${subjectnamespace}`,
        {
          headers :  { 'Authorization': `Bearer ${localStorage.getItem("authToken")}`
           },
          timeout: 2000000,
          });
          return response.data.ehr;
        } 
      catch (error) {
        console.error("Error in getehrbysidandsns:", error);
        if (error?.response?.status) {
          if (error.response.status === 401) {
            console.error("Unauthorized access. Please login again.");
            this.logout();
            return
          }      
          if (error.response.status == 404) {
            return error.response.data;
          }    
        
          if (error.response.status === 500) {
            return error.response.data;
        // throw { status: 500, message: "Server error" };
          }
          throw { status: 500, message: `An unexpected error occurred ${error.response.status}` };
        }
      } finally {
        this.isLoading=false;
      }
    },    
    async postehrbyehrid(ehrid) {
      console.log('inside postehrbyehrid')
      console.log('ehrid=',ehrid)
      console.log(localStorage.getItem("authToken"))
      this.isLoading=true;
      // await this.sleep(5000);
      try {
        console.log('before post')
        const response = await axios.post(`http://127.0.0.1:5000/ehr/${ehrid}`,
        {},
        {
          headers :  { 'Authorization': `Bearer ${localStorage.getItem("authToken")}`
           },
          timeout: 2000000,
          });
          return response.data.ehr;
        } 
      catch (error) {
        console.error("Error in postehrbyehrid:", error);
        if (error?.response?.status) {
          if (error.response.status === 401) {
            console.error("Unauthorized access. Please login again.");
            this.logout();
            return
          }      
          if (error.response.status == 404) {
            return error.response.data;
          }    
        
          if (error.response.status === 500) {
            return error.response.data;
        // throw { status: 500, message: "Server error" };
          }
          throw { status: 500, message: `An unexpected error occurred ${error.response.status}` };
        }
      } finally {
        this.isLoading=false;
      }
    }
  },
});
</script>


<style scoped>
#app {
  display: flex;
  margin-top: 0px;
}



h1 {
  margin-top: 0;
  /* Ensure the title has no space from the top */
  color: #333;
  font-size: 32px;
  font-weight: bold;
  text-align: center;
  padding-top: 0px;
  /* Add some padding on top if needed */
}

.main-content {
  /* padding-top: 0px;
  padding-left: 60px;
  padding-right: 60px;
  margin-top: 0px;
  margin-left: 20px;
  margin-right: 20px; */
  flex: 1;
  padding: 40px;
  padding-top: 0px;
  display: flex;
  flex-direction: column;
  margin-top:0px;
  margin-bottom:100px;
  margin-right: 30px;
  margin-left: 220px;
  position: relative;
  z-index: 0;
}

.method-selection-zone {
  /* margin-top: 0px;
  margin-left: 60px;
  width: 150px;
  background: #f4f4f4;
  padding: 20px;
  display: flex;
  flex-direction: column; */
  position: fixed; /* Fix the method selection on the left */
  top: 0;
  left: 60px;
  width: 150px; /* You can adjust this width as needed */
  height: 100%; /* Take up the full height */
  background: #f4f4f4;
  padding: 20px;
  overflow-y: auto; /* Allow vertical scrolling within the method section */
  /* z-index: 10; Ensure it's on top */
  z-index: 10;
}

.method-item {
  margin-bottom: 15px;
  padding: 10px 10px;
  border: 2px solid #ddd;
}

.method-item button {
  width: 100%;
}
method-actions {
  margin-bottom: 0px;
}

.parameter-form {
  /* background-color: #a0a0a0; */
  background-color: #f0f0f0;
  padding: 20px;
  margin-bottom: 20px;
  flex: 1;
  border-radius: 8px;
}

.parameters-title {
  background-color: #f0f0f0;
}

.parameter-form .form-group {
  background-color: #f0f0f0;
  margin-bottom: 10px;
}

.parameter-form .form-group input {
  width: 255px;
}
.parameter-form label {
  display: block;
  margin-bottom: 5px;
}

.parameter-form .action-button {
  background-color: #a5a5a5;
}

.results-section {
  flex: 1;
  background-color: #fff;
  padding: 20px;
  background-color: #fff;
  overflow-x: auto;  /* Add horizontal scroll to results section */
  overflow-y: hidden;  /* Disable vertical scroll */
  white-space: nowrap; /* Prevent text wrapping */
}

.results-section pre {
  font-size: 14px;
  text-align: left;
}

.separator {
  height: 1px;
  background-color: #ccc;
  margin: 20px 0;
}
.results-container {
  width: 100%;
  overflow-x: auto; /* Enable horizontal scrolling */
  overflow-y: hidden; /* Disable vertical scrolling */
  white-space: nowrap; /* Prevent text wrapping */
  padding: 10px; /* Add some padding */
  border: 1px solid #ccc;
  margin-bottom: 10px;
}

.result-content {
  width: fit-content;
}

.no-method {
  display: flex;
  justify-content: left;
  align-items: left;
  height: 100px;
}

.action-group {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.method-title {
  background: #bad489
}
</style>
