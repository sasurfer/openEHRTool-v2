<template>
  <div id="app">
    <!-- You can have a global navbar, footer, or other common layout elements here -->
    <Sidebar @open-user-info="openUserInfo" />
    <rsidebar @open-ehr-info="openEHRInfo" @open-template-info="openTemplateInfo"
      @open-composition-info="openCompositionInfo" @open-aql-info="openAQLInfo" />
    <UserInfoModal v-if="isUserInfoVisible" :isVisible="isUserInfoVisible" :user="user" @close-modal="closeModal"
      @logout="logout" />

    <div class="method-selection-zone">
      <h3><i>Template Methods</i></h3>
      <div class="radio-group-container">
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
        <div class="radio-group">
          <label>
            <input type="radio" v-model="onwhat" value="template" />
            Template
          </label>
        </div>
      </div>


      <div v-for="(method, index) in filteredMethods" :key="index" class="method-item" :style="getMethodStyle(index)">
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
      <div v-if="selectedMethod !== null" class="actions">
        <div class="method-title">
          <h2>{{ filteredMethods[selectedMethod].label }}</h2>
        </div>


        <!-- Parameter Form Zone -->
        <div class="parameter-form">
          <div class="parameters-title">
            <h3>Input Parameters</h3>
          </div>
          <form @submit.prevent="submitForm">

            <div v-for="(param, index) in currentParams" :key="index" class="form-group">
              <label>{{ param.label }}:</label>

              <!-- Existing Input for text, etc. -->
              <input v-if="param.type !== 'select'" v-model="param.value" :type="param.type"
                :placeholder="param.placeholder" />
              <!-- New Select Dropdown -->
              <select v-else-if="param.type === 'select'" v-model="param.value" class="form-select">
                <!-- Default disabled option -->
                <option disabled value="">{{ placeholderText }}</option>
                <!-- Dynamic options from data -->
                <option v-for="optionValue in this[param.optionsKey]" :key="optionValue" :value="optionValue">
                  {{ optionValue }}
                </option>
              </select>
              <!-- Add a message if options failed to load -->
              <p
                v-if="param.type === 'select' && !isLoadingTemplateNames && (!this[param.optionsKey] || this[param.optionsKey].length === 0)">
                Could not load template list.
              </p>
            </div>





            <div v-for="(radioparam, radioIndex) in currentRadioParams" :key="radioIndex" class="form-check-group">
              <label>{{ radioparam.label }}:</label>
              <div v-for="(option, optionIndex) in radioparam.options" :key="optionIndex" class="form-check">
                <input :id="`param-${radioIndex}-option-${optionIndex}`" type="radio" :name="`param-${radioIndex}`"
                  :value="option" v-model="radioparam.selected" class="form-check-input" />
                <label :for="`param-${radioIndex}-option-${optionIndex}`" class="form-check-label">{{ option }}</label>
              </div>
            </div>

            <div v-if="currentFile" class="file-input">
              <label>{{ labelFile }}</label>
              <input type="file" ref="fileInput" @change="handleFileUpload" />
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
              <div v-if="resultsOK" class="flex justify-center items-center">
                <div class="results-button-save">
                  <button type="submit" @click="saveResultsToFile">Save Results to File</button>
                </div>
              </div>
              <pre>{{ results }}</pre>
            </div>
            <div v-if="isLoading" class="flex justify-center items-center ehr-spinner">
              <Circle4Spinner :size="'50px'" :background="'#48f791'"></Circle4Spinner>
            </div>


          </div>
        </div>
      </div>
      <div v-else class="no-method">
        <svg width="40" height="40" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg" transform="translate(0, 5)">
          <path d="M40 25H10m0 0l7-7m-7 7l7 7" stroke="black" stroke-width="3" fill="none" />
        </svg>
        <p>Please select a method from the left methods menu.</p>

      </div>
    </div>


    <EHRInfoModal v-if="isEHRInfoVisible" :isVisible="isEHRInfoVisible" :ehrData="ehrData"
      @close-ehr-modal="closeEHRInfo" :isLoading="isLoadingEHR" />
    <TemplateInfoModal v-if="isTemplateInfoVisible" :isVisible="isTemplateInfoVisible" :templateData="templateData"
      @close-template-modal="closeTemplateInfo" :isLoading="isLoadingTemplate" />
    <CompositionInfoModal v-if="isCompositionInfoVisible" :isVisible="isCompositionInfoVisible"
      :compositionData="compositionData" @close-composition-modal="closeCompositionInfo"
      :isLoading="isLoadingComposition" />
    <AQLInfoModal v-if="isAQLInfoVisible" :isVisible="isAQLInfoVisible" :aqlData="aqlData"
      @close-aql-modal="closeAQLInfo" :isLoading="isLoadingAQL" />
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
  name: 'TemplatePage',
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
      resultsName: 'results.json',
      methodType: "All",
      onwhat: "template",
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
      templateNames: [],
      templates: [],
      isLoadingTemplateNames: false,
      // selectedMethodIndex: null,
    };
  },
  computed: {
    filteredMethods() {
      if (this.methodType === 'All') {
        return this.currentMethods;
      } else {
        return this.currentMethods.filter(method => method.type.includes(this.methodType) && method.what.includes(this.onwhat));
      }
    },
    placeholderText() {

      if (this.isLoadingTemplateNames) {
        return 'Loading...';
      } else if (this.templateNames && this.templateNames.length > 0) {
        return 'Select Template Name';
      } else {
        return 'No templates available';
      }
    }
  },
  mounted() {
    // Fetch data when the component is first mounted
    this.fetchEHRdata();
    this.fetchTemplateData();
    this.fetchCompositionData();
    this.fetchAQLData();
    this.currentMethods = this.getMethodsForTemplate();
  },
  watch: {
    '$route'() {
      // Fetch data when the route changes
      this.fetchEHRdata();
      this.fetchTemplateData();
      this.fetchCompositionData();
      this.fetchAQLData();
    },
    methodType() {
      // this.selectedMethodIndex=null;
      this.selectedMethod = null;
    },
    onwhat() {
      this.selectedMethod = null;
    }

  },
  methods: {
    getMethodStyle(index) {
      return index === this.selectedMethod
        ? { backgroundColor: '#bad489', color: 'white' } : {};
    },
    getIndexByTypeWhat(arr, targetIndex, type, what) {
      if (this.methodType === 'All') {
        return targetIndex;
      }
      let count = 0;
      for (let i = 0; i < arr.length; i++) {
        if (arr[i].type.includes(type) && arr[i].what.includes(what)) {
          if (targetIndex === count) {
            return i;
          }
          count++;
        }
      }
      return -1; // Return -1 if no element with the specified type is found.
    },
    getNeedFile(index) {
      const needFile = [
        { file: false, label: '' },
        { file: false, label: '' },
        { file: true, label: 'Choose Template File' },
      ];
      return needFile[index] || { file: false, label: '' };
    },
    selectMethod(index) {
      this.resultsOK = false;
      this.resultsName = 'results.json';
      this.currentMethods = this.getMethodsForTemplate();
      const index2 = this.getIndexByTypeWhat(this.currentMethods, index, this.methodType, this.onwhat)
      console.log("index", index)
      console.log("index2", index2)
      this.selectedMethod = index;
      // this.selectedMethodIndex = index;
      this.methodActions = this.getActionsForMethod(index2);
      this.currentParams = this.getParamsForMethod(index2);
      this.currentRadioParams = this.getRadioParamsForMethod(index2);
      this.needFile = this.getNeedFile(index2);
      this.currentFile = this.needFile.file;
      this.labelFile = this.needFile.label;
      console.log('currentfile', this.currentFile);
      console.log('labelFile', this.labelFile);
      this.results = null; // Reset results
      if (index2 === 1) {
        this.fetchTemplateNames();
      }
    },
    getMethodsForTemplate() {
      const methods = {
        'methods': [
          { label: 'List Templates', type: ['Get'], what: ['template'] },//1
          { label: 'Retrieve Template by Name', type: ['Get'], what: ['template'] },//2
          { label: 'Insert Template', type: ['Post'], what: ['template'] },//3
        ]
      };
      return methods['methods'] || [];
    },

    // Get actions associated with the selected method
    getActionsForMethod(index) {
      const actions = [
        [{ label: 'Submit', action: 'submit_template_list' }],//1
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_template_get' }],//2
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_template_post' }],//3
      ];
      return actions[index] || [];
    },
    getRadioParamsForMethod(index) {
      const radioParams = [
        [],//1
        [{ label: 'Output Format', selected: "Opt", options: ['Opt', 'Webtemplate'] }],//2
        [],//3
      ];
      return radioParams[index] || [];
    },
    // Get input parameters for the selected method
    getParamsForMethod(index) {
      const params = [
        [//1
        ],
        [//2
          {
            label: "Template Name",
            value: "",
            type: "select",
            optionsKey: 'templateNames',
            placeholder: "Select Template Name",
          }
        ],
        [//3
          // {
          //   label: "Template File",
          //   value: "",
          //   type: "file",
          //   placeholder: "Choose Template File",
          // }
        ],
      ];
      if (index === 1 && params[1] && params[1][0]) {
        params[1][0].value = '';
      }
      return params[index] || [];
    },

    // Handle action button click
    async executeAction(action) {
      this.results = null
      if (action == 'submit_template_list') //get template list
      {
        try {
          this.templates = await this.fetchTemplateNames();
          console.log('templates', this.templates);
          this.results = JSON.stringify(this.templates, null, 2);
          this.resultsOK = true;
        }
        catch (error) {
          console.error("Error in executeAction:", error);
          this.results = `Error: ${error.message}`;
        }
      } else if (action == 'clear_all') {
        this.currentParams.forEach(param => { param.value = ''; });
        this.results = null;
        this.resultsOK = false;
        this.selectedFile = null;
        const fileInput = this.$refs.fileInput;
        if (fileInput) {
          fileInput.value = null;
        }

      } else if (action == 'submit_template_get') //get template by name
      {
        this.resultsOK = false;
        const tid = this.currentParams.find(p => p.label === 'Template Name');
        if (!tid.value) {
          this.results = 'Template Name is required';
          return;
        }
        console.log('tid is', tid?.value);
        this.format = this.currentRadioParams.find(p => p.label === 'Output Format')?.selected || "Opt";
        try {
          const templateResults = await this.gettemplate(tid.value, this.format);
          console.log('results', templateResults);

          if (this.format.toLowerCase() == 'opt') {
            this.resultsName = 'results.opt';
            this.results = this.formatXml(templateResults);
          } else {
            this.resultsName = 'results.json';
            this.results = JSON.stringify(templateResults, null, 2);
          }
        }
        catch (error) {
          console.error("Error in executeAction:", error);
          this.results = `Error: ${error.message}`;
        }

      }
      else if (action == 'submit_template_post') //post template
      {
        console.log('inside submit_template_post')
        this.resultsOK = false;
        if (!this.selectedFile) {
          this.results = 'Please select a Template file'
          return;
        }
        try {
          const reader = new FileReader();
          reader.onload = async () => {
            try {
              const parser = new DOMParser();
              const template = parser.parseFromString(reader.result, "application/xml");
              console.log('template is', template);
              const templateResults = await this.posttemplate(template);
              console.log('results', templateResults);
              this.results = JSON.stringify(templateResults, null, 2);
            }
            catch (error) {
              console.error("Error uploading OPT file:", error);
              this.results = `Error: ${error.message}`;
            }
          };
          reader.readAsText(this.selectedFile);
        }
        catch (error2) {
          console.error("Error in posttemplate:", error2);
          this.results = `Error: ${error2.message}`;
        }
      }
      else {
        this.results = null;
        this.resultsOK = false;
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
      this.selectedFile = file;
      console.log('File selected:', file);
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
    //for template list and get
    async fetchTemplateNames() {
      try {
        console.log('fetchTemplateNames called');
        this.isLoadingTemplateNames = true;
        this.templateNames = [];
        const response = await axios.get('http://127.0.0.1:5000/template/templates',
          { method: 'GET', headers: { 'Authorization': `Bearer ${localStorage.getItem("authToken")}` }, },
          { timeout: 2000000 });
        this.isLoadingTemplateNames = false;
        if (response.status === 401) {
          console.error("Unauthorized access. Please login again.");
          this.logout();
          return
        }
        if (response.status != 200) {
          console.error("Error fetching templates list:", response);
          return;
        }
        // Assuming the backend returns data in this structure
        console.log(response)
        console.log(response.data)
        this.templates = response.data
        console.log('this.templates', this.templates);
        console.log(typeof this.templates);
        this.templateNames = this.templates.template.map(template => template.template_id);
        console.log('this.templateNames', this.templateNames);

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
        this.isLoadingNames = false;
      }

      return this.templates;
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
    async saveResultsToFile() {
      const content = this.results;
      // --- Determine MIME type based on filename ---
      const fileExtension = this.resultsName.split('.').pop().toLowerCase();
      const mimeType = fileExtension === 'opt' ? 'application/xml' : 'application/json';
      // --- ---
      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = this.resultsName || 'results.json';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      // const blob = new Blob([content], { type: format === 'json' ? "application/json" : "application/xml" });
    },



    async gettemplate(templateid, format) {
      try {
        console.log('gettemplate called');
        this.isLoading = true;
        this.resultsOK = false;
        console.log('templateid is', templateid);
        console.log('format is', format);
        const response = await axios.get('http://127.0.0.1:5000/template/',
          {
            headers: { 'Authorization': `Bearer ${localStorage.getItem("authToken")}` },
            params: {
              templateid: templateid,
              format: format
            },
            timeout: 2000000
          });
        this.isLoading = false;
        if (response.status === 401) {
          console.error("Unauthorized access. Please login again.");
          this.logout();
          return
        }
        if (response.status != 200) {
          console.error("Error fetching templates list:", response);
          return;
        }
        this.resultsOK = true;
        return response.data.template;

      } catch (error) {
        console.error("Error fetching template", error);
        if (error?.response?.status) {
          if (error.response.status === 401) {
            console.error("Unauthorized access. Please login again.");
            this.logout();
            return
          }
        }
      }
      finally {
        this.isLoading = false;
      }
    },
    async posttemplate(template) {
      console.log('inside posttemplate')
      console.log(localStorage.getItem("authToken"))
      this.isLoading = true;
      this.resultsOK = false;
      const serializer = new XMLSerializer();
      const templateString = serializer.serializeToString(template);
      console.log('templateString=', templateString);
      // await this.sleep(5000);
      try {
        const response = await axios.post(`http://127.0.0.1:5000/template/`,
          { "template": templateString },
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            timeout: 2000000,
          });
        this.isLoading = false;
        return response.data.template;
      }
      catch (error) {
        console.error("Error in posttemplate:", error);
        if (error?.response?.status) {
          if (error.response.status === 401) {
            console.error("Unauthorized access. Please login again.");
            this.logout();
            return
          }
          if (402 <= error.response.status <= 500) {
            return error.response.data;
          }

          throw { status: 500, message: `An unexpected error occurred ${error.response.status}` };
        }
      } finally {
        this.isLoading = false;
      }
    },
    formatXml(xml) {
      let formatted = '';
      const reg = /(>)(<)(\/*)/g;
      xml = xml.replace(reg, '$1\n$2$3'); // Ensuring proper line breaks between tags

      let pad = 0;
      xml.split('\n').forEach(node => {
        // Decrease indentation before closing tags
        if (node.match(/^<\/\w/)) {
          pad -= 1;
        }

        // Add indentation and the node itself
        formatted += '  '.repeat(Math.max(pad, 0)) + node + '\n'; // Ensure pad is not negative

        // Increase indentation after opening tags (not self-closing)
        if (node.match(/^<[^!/?\w]/) && !node.endsWith('/>')) {
          pad += 1;
        }
      });

      return formatted;
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
  margin-top: 0px;
  margin-bottom: 100px;
  margin-right: 30px;
  margin-left: 220px;
  position: relative;
  z-index: 0;
  overflow: auto;
  max-width: calc(100vw - 220px - 60px);
  ;
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
  left: 60px;
  width: 180px;
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

method-actions {
  margin-bottom: 0px;
}

.parameter-form {
  /* background-color: #a0a0a0; */
  background-color: #f0f0f0;
  padding: 20px;
  margin-bottom: 20px;
  /* flex: 1; */
  border-radius: 8px;
  max-width: 100%;
  box-sizing: border-box;
}

.parameters-title {
  background-color: #f0f0f0;
}

.parameter-form .form-group {
  background-color: #f0f0f0;
  margin-bottom: 10px;
}

.parameter-form .form-group input,
.parameter-form .form-group select {
  width: 100%;
  max-width: 400px;
  padding: 8px;
  box-sizing: border-box;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.parameter-form label {
  display: block;
  margin-bottom: 5px;
}

.parameter-form .action-button {
  background-color: #a5a5a5;
}

.results-section {
  max-width: 100%;
  overflow-x: auto;
  /* Horizontal scroll */
  /* overflow-y: visible; */
  /* border: 1px solid #ccc; */
  padding: 10px;
  background-color: #fff;
  box-sizing: border-box;
  margin-top: 20px;
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
  /* padding: 0;
  margin: 0;
  border: none; */
  width: 100%;
  overflow-x: auto;
  overflow-y: visible;
}



/* .results-content {
  display: inline-block;
  min-width: 100%;
 
} */

.results-content {
  width: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.results-content pre {
  white-space: pre;
  overflow-x: auto;
  margin: 0;
  padding: 10px;
  background-color: #f8f8f8;
  border: 1px solid #eee;
  border-radius: 4px;
  margin-top: 10px;
  max-width: 100%;
  box-sizing: border-box;
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

.file-input {
  padding: 20px;
  margin-bottom: 20px;
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
  margin-bottom: 10px;
}


.form-check-group {
  display: flex;
  justify-content: space-between;
  /* Distributes items evenly */
  align-items: center;
  width: 30%;
  margin-left: 30%;
  /* Ensures the container spans the full width */
}

.form-check {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  /* margin-right: 0px; */
  margin-bottom: 5px;
  /* min-width: 0px; */
  text-align: center;
  /* padding: 0px; */
}

/* 
.form-check-input {
  margin: 0 0 3px 0;
} */

.form-check-label {
  /* margin: 0; */
  font-size: 0.9em;
}

.results-button-save {
  display: flex;
  justify-content: center;
  margin-bottom: 10px;
  z-index: 1;
}

/* .results-section,
.results-container,
.results-content,
.results-content>div,
.results-content>pre {
  border: 1px dashed red;
} */
</style>
