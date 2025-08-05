<template>
  <div id="app">
    <!-- You can have a global navbar, footer, or other common layout elements here -->
    <Sidebar @open-user-info="openUserInfo" />
    <rsidebar @open-ehr-info="openEHRInfo" @open-template-info="openTemplateInfo"
      @open-composition-info="openCompositionInfo" @open-aql-info="openAQLInfo" />
    <UserInfoModal v-if="isUserInfoVisible" :isVisible="isUserInfoVisible" :user="user" @close-modal="closeModal"
      @logout="logout" />

    <div class="method-selection-zone">
      <h3><i>LOG Filter</i></h3>
      <div class="radio-group-container">
        <label>REST Method:</label>
        <div class="radio-group">
          <label>
            <input type="radio" v-model="methodType" value="All" />
            All
          </label>
        </div>
        <div class="radio-group">
          <label>
            <input type="radio" v-model="methodType" value="Get" />
            Get
          </label>
          <label>
            <input type="radio" v-model="methodType" value="Post" />
            Post
          </label>
          <label>
            <input type="radio" v-model="methodType" value="Put" />
            Put
          </label>
          <label>
            <input type="radio" v-model="methodType" value="Del" />
            Del
          </label>
        </div>
      </div>
      <div class="radio-group-container">
        <label>Object Type:</label>
        <div class="radio-group">
          <label>
            <input type="radio" v-model="onwhat" value="All" />
            All
          </label>
        </div>
        <div class="radio-group">
          <label>
            <input type="radio" v-model="onwhat" value="ehr" />
            Ehr
          </label>
          <label>
            <input type="radio" v-model="onwhat" value="ehrstatus" />
            Ehrstatus
          </label>
          <label>
            <input type="radio" v-model="onwhat" value="folder" />
            Directory
          </label>
          <label>
            <input type="radio" v-model="onwhat" value="template" />
            Template
          </label>
          <label>
            <input type="radio" v-model="onwhat" value="composition" />
            Composition
          </label>
          <label>
            <input type="radio" v-model="onwhat" value="contribution" />
            Contribution
          </label>
          <label>
            <input type="radio" v-model="onwhat" value="query" />
            Query
          </label>
          <label>
            <input type="radio" v-model="onwhat" value="form" />
            Form
          </label>
        </div>
      </div>
      <div class="radio-group-container">
        <label>Outcome:</label>
        <div class="radio-group">
          <label>
            <input type="radio" v-model="outcome" value="All" />
            All
          </label>
          <label>
            <input type="radio" v-model="outcome" value="Success" />
            Success
          </label>
          <label>
            <input type="radio" v-model="outcome" value="Failure" />
            Failure
          </label>
        </div>
      </div>
      <div class="radio-group-container">
        <label>Order by:</label>
        <div class="radio-group">
          <label>
            <input type="radio" v-model="order" value="oldest" />
            Oldest first
          </label>
          <label>
            <input type="radio" v-model="order" value="newest" />
            Newest first
          </label>
        </div>
      </div>

      <div class="customsearch">
        <label for="customsearch">Search keywords:</label>
        <textarea id="customsearch" v-model="customsearch" placeholder="Allowed: (),AND,OR,NOT,keywords,*" rows="1"
          cols="31" class="big-textarea" style="font-size: 8px;"></textarea>
      </div>

      <div v-for="(method, index) in currentMethods" :key="index" class="method-item" :style="getMethodStyle(index)">
        <button @click="selectMethod(index)">{{ method.label }}</button>
      </div>

      <!-- class="method-item" :style="getMethodStyle(index)">
          <button @click="selectMethod(index)" :class="{ selected: selectedMethodIndex === index }" >{{ method.label }}</button>
        </div> -->


      <!-- </div> -->
    </div>


    <div class="main-content">
      <!-- Your main content goes here -->

      <!-- Method Actions Section -->

      <!-- Results Section -->
      <div class="results-section">
        <h3>Results</h3>
        <div class="results-container">
          <div class="results-content">
            <div v-if="resultsOK" class="flex justify-center items-center">
              <button type="submit" @click="saveResultsToFile">Save Results to File</button>
            </div>
            <pre>{{ results }}</pre>
          </div>
          <div v-if="isLoading" class="flex justify-center items-center ehr-spinner">
            <Circle4Spinner :size="'50px'" :background="'#48f791'"></Circle4Spinner>
          </div>


        </div>
      </div>
    </div>

  </div>


  <EHRInfoModal v-if="isEHRInfoVisible" :isVisible="isEHRInfoVisible" :ehrData="ehrData" @close-ehr-modal="closeEHRInfo"
    :isLoading="isLoadingEHR" />
  <TemplateInfoModal v-if="isTemplateInfoVisible" :isVisible="isTemplateInfoVisible" :templateData="templateData"
    @close-template-modal="closeTemplateInfo" :isLoading="isLoadingTemplate" />
  <CompositionInfoModal v-if="isCompositionInfoVisible" :isVisible="isCompositionInfoVisible"
    :compositionData="compositionData" @close-composition-modal="closeCompositionInfo"
    :isLoading="isLoadingComposition" />
  <AQLInfoModal v-if="isAQLInfoVisible" :isVisible="isAQLInfoVisible" :aqlData="aqlData" @close-aql-modal="closeAQLInfo"
    :isLoading="isLoadingAQL" />

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
import { BACKEND_HOST } from '@/config';



export default defineComponent({
  name: 'LOGPage',
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
      resultsName: 'log.json',
      methodType: "All",
      onwhat: "All",
      outcome: "All",
      order: "oldest",
      customsearch: "",
      resultsOK: false,
      resultsFile: {},
      isLoading: false,
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
      currentRadioParams: [],
      currentFile: false,
      labelFile: null,
      results: null,
      isLoadingEHR: false,
      isLoadingTemplate: false,
      isLoadingComposition: false,
      isLoadingAQL: false,
      ehrid: '',
      subjectid: '',
      subjectnamespace: '',
      selectedFile: null,
      // selectedMethodIndex: null,
    };
  },
  computed: {
  },
  mounted() {
    // Fetch data when the component is first mounted
    this.fetchEHRdata();
    this.fetchTemplateData();
    this.fetchCompositionData();
    this.fetchAQLData();
    this.currentMethods = this.getMethodsForLog();
    this.fetchlog();
  },
  watch: {
    '$route'() {
      // Fetch data when the route changes
      this.fetchEHRdata();
      this.fetchTemplateData();
      this.fetchCompositionData();
      this.fetchAQLData();
      this.fetchlog();
    },

  },
  methods: {
    getMethodStyle(index) {
      return index === this.selectedMethod
        ? { backgroundColor: '#bad489', color: 'white' } : {};
    },
    selectMethod(index) {
      this.resultsOK = false;
      this.resultsName = 'log.json';
      this.currentMethods = this.getMethodsForLog();
      this.selectedMethod = index;
      if (this.selectedMethod == 0) {
        this.fetchlog();
      } else if (this.selectedMethod == 1) {
        this.ResetFilter();
        this.fetchlog();
      } else if (this.selectedMethod == 2) {
        this.DeleteLog();
        this.fetchlog();
      }

    },
    getMethodsForLog() {
      const methods = {
        'methods': [
          { label: 'Run Filter' },
          { label: 'Reset Filter' },//1
          { label: 'Delete Log' },//2
        ]
      };
      return methods['methods'] || [];
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
        const response = await axios.get(`http://${BACKEND_HOST}/rsidebar/ehrs`,
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
        const response = await axios.get(`http://${BACKEND_HOST}/rsidebar/templates`,
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
        const response = await axios.get(`http://${BACKEND_HOST}/rsidebar/compositions`,
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
        const response = await axios.get(`http://${BACKEND_HOST}/rsidebar/queries`,
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
    async saveResultsToFile() {
      const content = JSON.stringify(this.results, null, 2);
      // --- Determine MIME type based on filename ---
      const mimeType = 'application/json';
      // --- ---
      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = this.resultsName || 'log.json';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      // const blob = new Blob([content], { type: format === 'json' ? "application/json" : "application/xml" });
    },
    async fetchlog() {
      console.log('inside fetchlog')
      this.isLoading = true;
      this.resultsOK = false;
      try {

        console.log('before get')
        const response = await axios.get(`http://${BACKEND_HOST}/log`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            params: {
              'methodType': this.methodType,
              'onwhat': this.onwhat,
              'outcome': this.outcome,
              'order': this.order,
              'customsearch': this.customsearch,
            },
          });
        this.resultsOK = true;
        console.log('response log', response.data.log)
        this.results = response.data.log;
      }
      catch (error) {
        console.error("Error in fetchlog:", error);
        if (error?.response?.status) {
          if (error.response.status === 401) {
            console.error("Unauthorized access. Please login again.");
            this.logout();
          } else if (402 <= error.response.status <= 500) {
            this.results = error.response.data;
          } else {
            this.results = { status: 500, message: `An unexpected error occurred ${error.response.status}` };
          }
        }
      } finally {
        this.isLoading = false;
      }
    },
    ResetFilter() {
      this.methodType = "All";
      this.onwhat = "All";
      this.outcome = "All";
      this.order = "oldest";
      this.customsearch = "";
      this.resultsOK = false;
    },
    async DeleteLog() {
      console.log('inside delete log')
      this.isLoading = true;
      this.resultsOK = false;
      try {

        console.log('before get')
        const response = await axios.delete(`http://${BACKEND_HOST}/log`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
          });
        this.resultsOK = true;
        console.log('response log', response.data.log)
        this.results = response.data.log;
      }
      catch (error) {
        console.error("Error in deletelog:", error);
        if (error?.response?.status) {
          if (error.response.status === 401) {
            console.error("Unauthorized access. Please login again.");
            this.logout();
          } else if (402 <= error.response.status <= 500) {
            this.results = error.response.data;
          } else {
            this.results = { status: 500, message: `An unexpected error occurred ${error.response.status}` };
          }
        }
      } finally {
        this.isLoading = false;
      }
    },















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
  width: calc(100% - 290px);
  flex: 1;
  margin-left: 260px;
  margin-right: 60px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  box-sizing: border-box;
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
  position: fixed;
  /* Fix the method selection on the left */
  top: 0;
  left: 50px;
  width: 190px;
  /* You can adjust this width as needed */
  height: 100%;
  /* Take up the full height */
  background: #f4f4f4;
  /* padding: 20px; */
  overflow-y: auto;
  /* Allow vertical scrolling within the method section */
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

.method-actions {
  margin-bottom: 0px;
}

.parameter-container {
  width: 100%;
  /* max-width: 1000px; */
  background-color: #f0f0f0;
  padding: 20px;
  padding-top: 10px;
  margin-bottom: 20px;
  margin-top: 0px;
  border-radius: 8px;
  box-sizing: border-box;
  display: flex;
  justify-content: center;
}


.parameter-form {
  flex: 0 0 90%;
  /* background-color: white; */
  box-sizing: border-box;
}


.parameters-title {
  width: 100%;
}


.parameter-form input,
.parameter-form select {
  width: 100%;
  padding: 10px;
  margin-bottom: 30px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;

}

.parameter-form label {
  display: block;
  margin-bottom: 5px;
}

.parameter-form .action-button {
  background-color: #a5a5a5;
}

.parameter-form .form-group {
  margin-bottom: 30px;
  /* Adjust the spacing between form groups */
}


.results-section {
  width: 100%;
  /* */
  max-width: 100%;
  overflow-x: auto;
  padding: 10px;
  background-color: #fff;
  box-sizing: border-box;
  margin-top: 20px;
}


.results-section pre {
  font-size: 14px;
  text-align: left;
  max-width: 100%;
  overflow-x: auto;
  white-space: pre-wrap;
  /* Or pre-line if you want to break lines more aggressively */
  word-break: break-word;
  /* Very important */
}

.separator {
  height: 1px;
  background-color: #ccc;
  margin: 20px 0;
}

.results-container {
  /* width: 100%; */
  /* overflow-x: auto; */
  /* Enable horizontal scrolling */
  /* overflow-y: hidden; */
  /* Disable vertical scrolling */
  /* white-space: nowrap; */
  /* Prevent text wrapping */
  /* padding: 10px;
  border: 1px solid #ccc;
  margin-bottom: 10px; */
  width: 100%;
  overflow-x: hidden;
  overflow-y: visible;
}



.results-content {
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
  box-sizing: border-box;
}


.results-content pre {
  white-space: pre-wrap;
  word-break: break-word;
  overflow-x: auto;
  margin: 0;
  padding: 10px;
  background-color: #f8f8f8;
  border: 1px solid #eee;
  border-radius: 4px;
  margin-top: 10px;
  /* max-width: 100%; */
  /* box-sizing: border-box; */
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
  margin-top: 30px;
}

.method-title {
  background: #bad489
}

.file-input {
  padding: 20px;
  margin-bottom: 30px;
  /* display: flex;
  flex-direction: column; */
}

.radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 3px;
  padding-top: 5px;
  padding-bottom: 5px;
  /* padding-left: 5px;
  padding-right: 5px; */
  /* Adjust the gap between the radio buttons */
}

.radio-group label {
  display: flex;
  align-items: center;
  font-size: 11px;
  /* Smaller label size */
}

.radio-group input {
  margin-right: 0px;
  /* Space between radio button and label text */
}


.radio-group-container {
  border: 2px solid #007BFF;
  /* Blue border around radio buttons area */
  padding: 0px;
  padding-bottom: 5px;
  /* Space between radio buttons and the border */
  border-radius: 5px;
  /* Optional: rounded corners */
  margin-bottom: 30px;
}


.form-check-group {
  display: flex;
  /* align-items: center; */
  width: 100%;
  column-gap: 20px;
  margin-bottom: 25px;
  /* margin-left: 30%; */
  /* Ensures the container spans the full width */
}


.form-check {
  display: inline-flex;
  flex-direction: row;
  /* align-items: center; */
  /* margin-right: 0px; */
  /* margin-bottom: 100px; */
  /* min-width: 0px; */
  /* text-align: center; */
  align-items: center;
  margin-bottom: 0px;
  padding: 0px;
  line-height: 1;
  row-gap: 0px;
  height: auto;
  /* padding: 0px; */
}


.form-check-input {
  /* margin-top: 0px; */
  margin-bottom: 0px;
  padding: 0px;
  vertical-align: top;
  line-height: 1;
  vertical-align: middle;
}

.form-check-label {
  /* margin: 0; */
  margin: 0px;
  padding: 0px;
  font-size: 0.7em;
  line-height: 1;
  vertical-align: middle;
}

.results-button-save {
  display: flex;
  justify-content: center;
  margin-bottom: 10px;
  z-index: 1;
}
</style>
