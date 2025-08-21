<template>
  <div id="app">
    <!-- You can have a global navbar, footer, or other common layout elements here -->
    <Sidebar @open-user-info="openUserInfo" />
    <rsidebar @open-ehr-info="openEHRInfo" @open-template-info="openTemplateInfo"
      @open-composition-info="openCompositionInfo" @open-aql-info="openAQLInfo" />
    <UserInfoModal v-if="isUserInfoVisible" :isVisible="isUserInfoVisible" :user="user" @close-modal="closeModal"
      @logout="logout" />

    <div class="method-selection-zone">
      <h3><i>ADMIN Methods</i></h3>
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
      </div>
      <div class="radio-group-container">
        <div class="radio-group">
          <label>
            <input type="radio" v-model="onwhat" value="All" />
            All
          </label>
        </div>
        <div class="radio-group">
          <label>
            <input type="radio" v-model="onwhat" value="ehr" />
            EHR
          </label>
          <label>
            <input type="radio" v-model="onwhat" value="ehrstatus" />
            EHRStatus
          </label>
          <label>
            <input type="radio" v-model="onwhat" value="template" />
            Template
          </label>
          <label>
            <input type="radio" v-model="onwhat" value="folder" />
            Directory
          </label>
          <label>
            <input type="radio" v-model="onwhat" value="composition" />
            Composition
          </label>
          <label>
            <input type="radio" v-model="onwhat" value="query" />
            Query
          </label>
          <label>
            <input type="radio" v-model="onwhat" value="contribution" />
            Contribution
          </label>
        </div>
      </div>


      <div v-for="(method, index) in filteredMethods" :key="index" class="method-item" :style="getMethodStyle(index)">
        <div class="button-wrapper">
          <button class="mybutton" @click="selectMethod(index)">{{ method.label }}</button>
          <div v-if="workingFiltered(index) == true">
            <span class="overlay">Not<br>Active</span>
          </div>
        </div>
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
        <div class="input-section">
          <div class="parameters-title">
            <h3>Input</h3>
          </div>
          <div class="parameter-container">
            <div class="parameter-form">
              <form @submit.prevent="submitForm">

                <div v-for="(param, index) in currentParams" :key="index" class="form-group">
                  <label>{{ param.label }}:</label>

                  <!-- Existing Input for text, etc. -->
                  <input v-if="param.type !== 'select'" v-model="param.value" :type="param.type"
                    :placeholder="param.placeholder" />
                  <!-- New Select Dropdown -->
                  <select v-else-if="param.type === 'select'" v-model="param.value" class="form-select">
                    <!-- Default disabled option -->
                    <option disabled value="">{{ getPlaceholderText(param) }}</option>
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
                    <label :for="`param-${radioIndex}-option-${optionIndex}`" class="form-check-label">{{ option
                      }}</label>
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
          </div>
        </div>

        <!-- Separator Line between Top and Results -->
        <div class="separator"></div>

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
      <div v-else class="no-method-selected">
        <div class="results-section">
          <h3>Results</h3>
          <div class="results-container">
            <!-- <div class="results-content-first"> -->
            <pre>{{ results }}</pre>
            <div v-if="isLoading" class="flex justify-center items-center ehr-spinner">
              <Circle4Spinner :size="'50px'" :background="'#48f791'"></Circle4Spinner>
            </div>
            <!-- </div> -->
          </div>
        </div>
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
import { BACKEND_HOST } from '@/config';



export default defineComponent({
  name: 'ADMINPage',
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
      methodType: "Get",
      onwhat: "ehr",
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
      isLoadingTemplateNames: false,
      isLoadingComposition: false,
      isLoadingAQL: false,
      ehrid: '',
      subjectid: '',
      subjectnamespace: '',
      selectedFile: null,
      templateNames: [],
      queryNames: [],
      versionOptions: [],
      nametoversions: {},
      isLoadingQueryNames: false,
      isLoadingQueryVersions: false,
      // selectedMethodIndex: null,
    };
  },
  computed: {
    filteredMethods() {
      if (this.methodType === 'All') {
        if (this.onwhat === 'All') {
          return this.currentMethods;
        }
        else {
          return this.currentMethods.filter(method => method.what.includes(this.onwhat));
        }
      } else {
        if (this.onwhat === 'All') {
          return this.currentMethods.filter(method => method.type.includes(this.methodType));
        }
        else {
          return this.currentMethods.filter(method => method.type.includes(this.methodType) && method.what.includes(this.onwhat));
        }
      }
    },
    selectedQueryNameValue() {
      const queryNameParam = this.currentParams.find(p => p.label === "Qualified Query Name" && p.type === "select");
      return queryNameParam ? queryNameParam.value : null;
    },
    selectedVersionValue() {
      const versionParam = this.currentParams.find(p =>
        (p.label === 'Version' || p.label === 'Version (Optional)') && p.type === 'select'
      );
      return versionParam ? versionParam.value : null;
    }
  },
  mounted() {
    // Fetch data when the component is first mounted
    this.fetchEHRdata();
    this.fetchTemplateData();
    this.fetchCompositionData();
    this.fetchAQLData();
    this.currentMethods = this.getMethodsForEHR();
    this.fetchstatus();
  },
  watch: {
    '$route'() {
      // Fetch data when the route changes
      this.fetchEHRdata();
      this.fetchTemplateData();
      this.fetchCompositionData();
      this.fetchAQLData();
      this.fetchstatus();
    },
    methodType() {
      // this.selectedMethodIndex=null;
      this.selectedMethod = null;
    },
    onwhat() {
      this.selectedMethod = null;
    },
    selectedQueryNameValue(newQueryName, oldQueryName) {
      const versionParam = this.currentParams.find(p => (p.label === 'Version (Optional)' || p.label === 'Version') && p.type === "select");

      if (newQueryName && this.nametoversions && this.nametoversions[newQueryName]) {
        this.versionOptions = [...this.nametoversions[newQueryName]]; // Use spread to ensure reactivity if needed
        if (versionParam) {
          // Reset version if the new query name is different from the old one,
          // or if the current version is no longer valid for the new query name.
          const queryNameChanged = oldQueryName !== undefined && newQueryName !== oldQueryName;
          if (queryNameChanged || !this.versionOptions.includes(versionParam.value)) {
            versionParam.value = '';
          }
        }
      } else {
        this.versionOptions = [];
        if (versionParam) {
          versionParam.value = '';
        }
      }

    },
    selectedVersionValue(newVersion, oldVersion) {
      if (newVersion !== oldVersion) {
        this.fetchQuery(this.selectedQueryNameValue, newVersion);
      }
    }
  },
  methods: {
    getPlaceholderText(param) {
      if (param.label === 'Qualified Query Name') {
        if (this.isLoadingQueryNames) {
          return 'Loading...';
        } else if (this.queryNames && this.queryNames.length > 0) {
          return 'Please select a query name';
        } else {
          return 'No data available';
        }
      } else if (param.label === 'Version' || param.label === 'Version (Optional)') {
        if (this.isLoadingQueryNames) {
          return 'Loading...';
        } else if (this.versionOptions && this.versionOptions.length > 0) {
          return 'Please select a version';
        } else if (this.currentParams.find(p => p.label === "Qualified Query Name" && p.type === "select")?.value) {
          return 'No versions available';
        } else {
          return 'Select Query Name first';
        }
      }
      else {
        return "No data available";
      }
    },
    workingFiltered(index) {
      const myindex = this.getIndexByTypeWhat(this.currentMethods, index, this.methodType, this.onwhat);
      return this.getWorkingForMethod(myindex);
    },
    getMethodStyle(index) {
      return index === this.selectedMethod
        ? { backgroundColor: '#bad489', color: 'white' } : {};
    },
    getIndexByTypeWhat(arr, targetIndex, type, what) {
      let count = -1;
      for (let i = 0; i < arr.length; i++) {
        const method = arr[i];
        const typeMatch = type === 'All' || method.type.includes(type);
        const whatMatch = what === 'All' || method.what.includes(what);

        if (typeMatch && whatMatch) {
          count++;
          if (count === targetIndex) {
            return i;
          }
        }
      }
      return -1; // Should not be reached if targetIndex is valid
    },
    getNeedFile(index) {
      const needFile = [
        { file: true, label: 'Choose Template File' },//1
        { file: false, label: '' },//2
        { file: false, label: '' },//3
        { file: true, label: 'Choose EHR File' },//4
        { file: false, label: '' },//5
        { file: false, label: '' },//6
        { file: false, label: '' },//7
        { file: false, label: '' },//8
        { file: true, label: 'Choose Contribution File' },//9
        { file: false, label: '' },//10
        { file: false, label: '' },//11
        { file: false, label: '' },//12
        { file: false, label: '' },//13
        { file: false, label: '' }//14
      ];
      return needFile[index] || { file: false, label: '' };
    },
    selectMethod(index) {
      this.resultsOK = false;
      this.resultsName = 'results.json';
      this.currentMethods = this.getMethodsForEHR();
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
      } else if (index2 === 5) {
        this.fetchQueryNames();
      }
    },
    getMethodsForEHR() {
      const methods = {
        'methods': [
          { label: 'Update Template', type: ['Put'], what: ['template'] },//1
          { label: 'Delete Template by name', type: ['Del'], what: ['template'] },//2
          { label: 'Delete all Templates', type: ['Del'], what: ['template'] },//3
          { label: 'Update EHR', type: ['Put'], what: ['ehr', 'ehrstatus'] },//4
          { label: 'Delete EHR', type: ['Del'], what: ['ehr'] },//5
          { label: 'Delete Stored Query', type: ['Del'], what: ['query'] },//6
          { label: 'Delete Directory', type: ['Del'], what: ['folder'] },//7
          { label: 'Delete Composition', type: ['Del'], what: ['composition'] },//9
          { label: 'Update Contribution', type: ['Put'], what: ['contribution'] },//9
          { label: 'Delete Contribution', type: ['Del'], what: ['contribution'] },//10
          { label: 'Merge source EHR into target EHR', type: ['Post'], what: ['ehr'] },//11
          { label: 'Retrieve target EHR', type: ['Get'], what: ['ehr'] },//12
          { label: 'Retrieve merging status of source EHR/target EHR', type: ['Get'], what: ['ehr'] },//13
          { label: 'Retrieve merging details', type: ['Get'], what: ['ehr'] },//14
        ]
      };
      return methods['methods'] || [];
    },

    // Get actions associated with the selected method
    getActionsForMethod(index) {
      const actions = [
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_update_template' }],//1
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_delete_template' }],//2
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_delete_all_templates' }],//3
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_update_ehr' }],//4
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_delete_ehr' }],//5
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_delete_stored_query' }],//6
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_delete_directory' }],//7
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_delete_composition' }],//8
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_update_contribution' }],//9
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_delete_contribution' }],//10
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_merge' }],//11
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_get_target_ehr' }],//12
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_folder_get_merging_status' }],//13
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_get_merging_details' }],//14


      ];
      return actions[index] || [];
    },
    getRadioParamsForMethod(index) {
      const radioParams = [
        [],//1
        [],//2
        [],//3
        [],//4
        [],//5  
        [],//6
        [],//7
        [],//8
        [],//9
        [],//10
        [],//11
        [],//12
        [],//13
        [],//14
      ];
      return radioParams[index] || [];
    },
    getWorkingForMethod(index) {
      const working = [
        false,//1
        false,//2
        false,//3
        true,//4
        false,//5  
        false,//6
        false,//7
        false,//8
        false,//9
        false,//10
        true,//11
        true,//12
        true,//13
        true,//14
      ];
      return working[index] || false;
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
        ],
        [//4
          { label: 'EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" }
          // { label: '2 POST', value: "", type: 'text' }
        ],
        [{ label: 'EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" }],//5
        [//6
          {
            label: "Qualified Query Name",
            value: "",
            type: "select",
            optionsKey: 'queryNames',
            placeholder: "Select Query Name",
          }, { label: 'Version', value: '', optionsKey: 'versionOptions', type: 'select', placeholder: "Select Version" }],
        [//7
          { label: 'EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" }, { label: 'Directory id', value: '', type: 'text', placeholder: "afe46cce-d8c9-4db8-940b-ee3db170a646::local.ehrbase.org::1" }],
        [//8
          { label: 'EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" }, { label: 'Composition versioned id', value: '', type: 'text', placeholder: "afe46cce-88c1-1bf5-9993-ee11b170a710::local.ehrbase.org::1" }],
        [//9
          { label: 'EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" }, { label: 'Contribution versioned id', value: '', type: 'text', placeholder: "afe46cce-88c1-1bf5-9993-ee11b170a710::local.ehrbase.org::1" }],
        [//10
          { label: 'EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" }, { label: 'Contribution versioned id', value: '', type: 'text', placeholder: "afe46cce-88c1-1bf5-9993-ee11b170a710::local.ehrbase.org::1" }],
        [//11
          { label: 'source EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" }, { label: 'target EHRid', value: '', type: 'text', placeholder: "a8e46cce-d8c9-4db8-940b-ee3db170a646" }, { label: 'Detail Level (optional)', value: '', type: 'text', placeholder: "BASIC" }, { label: 'Reversible', value: '', type: 'Boolean', placeholder: "true" }, { label: 'Dry Run (optional)', value: '', type: 'Boolean', placeholder: "true" }, { label: 'Folder Merge (optional)', value: '', type: 'text', placeholder: "BASIC" }, { label: 'Composition Merge (optional)', value: '', type: 'text', placeholder: "BASIC" }],
        [//12
          { label: 'Source EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" }],
        [//13
          { label: 'Source EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" }, { label: 'target EHRid', value: '', type: 'text', placeholder: "a8e46cce-d8c9-4db8-940b-ee3db170a646" },
          { label: 'Cascaded (optional)', value: '', type: 'Boolean', placeholder: "true" }],
        [//14
          { label: 'Source EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" }, { label: 'target EHRid', value: '', type: 'text', placeholder: "a8e46cce-d8c9-4db8-940b-ee3db170a646" }, { label: 'Unmerge data (optional)', value: '', type: 'Boolean', placeholder: "true" },
        ],
      ];
      return params[index] || [];
    },

    // Handle action button click
    async executeAction(action) {
      this.results = null
      if (action == 'submit_update_template') //update template
      {
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
              const templateResults = await this.updatetemplate(template);
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
          console.error("Error in updatetemplate:", error2);
          this.results = `Error: ${error2.message}`;
        }
      }
      else if (action == 'submit_delete_template') //delete template by name
      {
        this.resultsOK = false;
        const templateName = this.currentParams.find(p => p.label === 'Template Name');
        if (!templateName?.value) {
          this.results = 'Template Name is required';
          return;
        }
        try {
          const templateResults = await this.deletetemplate(templateName.value);
          console.log('results', templateResults);
          this.results = JSON.stringify(templateResults, null, 2);
        }
        catch (error) {
          console.error("Error in executeAction:", error);
          this.results = `Error: ${error.message}`;
        }
      }
      else if (action == 'submit_delete_all_templates') //delete all templates
      {
        this.resultsOK = false;
        try {
          const templateResults = await this.deletealltemplates();
          console.log('results', templateResults);
          this.results = JSON.stringify(templateResults, null, 2);
        }
        catch (error) {
          console.error("Error in executeAction:", error);
          this.results = `Error: ${error.message}`;
        }
      }
      else if (action == 'submit_update_ehr') //update EHR
      {
        this.resultsOK = false;
        const ehrid = this.currentParams.find(p => p.label === 'EHRid');
        if (!ehrid?.value) {
          this.results = 'EHRid is required';
          return;
        }
        if (!this.selectedFile) {
          this.results = 'Please select a EHR file'
          return;
        }
        try {
          const reader = new FileReader();
          reader.onload = async () => {
            try {
              const parser = new DOMParser();
              const ehrData = parser.parseFromString(reader.result, "application/xml");
              console.log('ehrData is', ehrData);
              const ehrResults = await this.updateehr(ehrid.value, ehrData);
              console.log('results', ehrResults);
              this.results = JSON.stringify(ehrResults, null, 2);
            }
            catch (error) {
              console.error("Error uploading EHR file:", error);
              this.results = `Error: ${error.message}`;
            }
          };
          reader.readAsText(this.selectedFile);
        }
        catch (error2) {
          console.error("Error in updateehr:", error2);
        }
      }
      else if (action == 'submit_delete_ehr') {
        console.log('inside submit_delete_ehr')
        this.resultsOK = false;
        const ehrid = this.currentParams.find(p => p.label === 'EHRid');
        if (!ehrid?.value) {
          this.results = 'EHRid is required';
          return;
        }
        try {
          const ehrResults = await this.deleteehr(ehrid.value);
          console.log('results', ehrResults);
          this.results = JSON.stringify(ehrResults, null, 2);
        }
        catch (error) {
          console.error("Error in executeAction:", error);
          this.results = `Error: ${error.message}`;
        }
      } else if (action == 'submit_delete_stored_query') {
        console.log('inside submit_delete_stored_query')
        this.resultsOK = false;
        const queryname = this.currentParams.find(p => p.label === 'Qualified Query Name')?.value;
        console.log('queryname', queryname);
        if (!queryname) {
          this.results = 'Qualified Query Name is required';
          return;
        }
        const queryversion = this.currentParams.find(p => p.label === 'Version')?.value;
        console.log('queryversion', queryversion);
        if (!queryversion) {
          this.results = 'Version is required';
          return;
        }
        try {
          const queryResults = await this.deletestoredquery(queryname, queryversion);
          console.log('results', queryResults);
          this.results = JSON.stringify(queryResults, null, 2);
          await this.fetchQueryNames();
          const queryNameParam = this.currentParams.find(p => p.label === 'Qualified Query Name');
          if (queryNameParam) {
            queryNameParam.value = '';
          }
          const versionParam = this.currentParams.find(p => p.label === 'Version');
          if (versionParam) {
            versionParam.value = '';
          }
        }
        catch (error) {
          console.error("Error in executeAction:", error);
          this.results = `Error: ${error.message}`;
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
    //for update template and delete template by name
    async fetchTemplateNames() {
      try {
        console.log('fetchTemplateNames called');
        this.isLoadingTemplateNames = true;
        this.templateNames = [];
        const response = await axios.get(`http://${BACKEND_HOST}/template/templates`,
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
        this.isLoadingQueryNames = false;
      }

      return this.templates;
    },
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
      const content = this.results;
      // --- Determine MIME type based on filename ---
      const fileExtension = this.resultsName.split('.').pop().toLowerCase();
      const mimeType = fileExtension === 'xml' ? 'application/xml' : 'application/json';
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
    async fetchstatus() {
      console.log('inside fetchstatus')
      console.log(localStorage.getItem("authToken"))
      this.isLoading = true;
      this.resultsOK = false;
      // await this.sleep(5000);
      try {
        const response = await axios.get(`http://${BACKEND_HOST}/admin/status`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            timeout: 2000000,
          });
        this.isLoading = false;
        this.results = response.data.status;
      }
      catch (error) {
        console.error("Error in fetchstatus:", error);
        if (error?.response?.status) {
          if (error.response.status === 401) {
            console.error("Unauthorized access. Please login again.");
            this.logout();
            return
          }
          if (error.response.status === 403) {
            this.results = 'User does not have permission to access these methods. Please login as an ADMIN user.\n\n' + error.response.data.status.detail;
            console.log('results:', this.results);
            return;
          }
          if (402 <= error.response.status <= 500) {
            this.results = error.response.data;
            return
          }

          throw { status: 500, message: `An unexpected error occurred ${error.response.status}` };
        }
      } finally {
        this.isLoading = false;
      }
    },
    async deletetemplate(template) {
      console.log('inside deletetemplate')
      console.log(localStorage.getItem("authToken"))
      console.log('template=', template)
      this.isLoading = true;
      this.resultsOK = false;
      // await this.sleep(5000);
      try {
        const response = await axios.delete(`http://${BACKEND_HOST}/admin/template/`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            params: {
              template_name: template
            },
            timeout: 2000000,
          });
        this.resultsOK = true;
        return response.data.template;
      }
      catch (error) {
        console.error("Error in deletetemplate:", error);
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
    }, async deletealltemplates() {
      console.log('inside deletealltemplates')
      console.log(localStorage.getItem("authToken"))
      this.isLoading = true;
      this.resultsOK = false;
      // await this.sleep(5000);
      try {
        const response = await axios.delete(`http://${BACKEND_HOST}/admin/templates/`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            timeout: 2000000,
          });
        this.resultsOK = true;
        return response.data.templates;
      }
      catch (error) {
        console.error("Error in deletealltemplates:", error);
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
    }, async updatetemplate(template) {
      console.log('inside updatetemplate')
      console.log(localStorage.getItem("authToken"))
      this.isLoading = true;
      this.resultsOK = false;
      const serializer = new XMLSerializer();
      const templateString = serializer.serializeToString(template);
      console.log('templateString=', templateString);
      // await this.sleep(5000);
      try {
        const response = await axios.put(`http://${BACKEND_HOST}/admin/template/`,
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
        console.error("Error in updatetemplate:", error);
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
    }, async deleteehr(ehrid) {
      console.log('inside deleteehr')
      console.log(localStorage.getItem("authToken"))
      console.log('ehrid=', ehrid)
      this.isLoading = true;
      this.resultsOK = false;
      // await this.sleep(5000);
      try {
        const response = await axios.delete(`http://${BACKEND_HOST}/admin/ehr/`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            params: {
              ehrid: ehrid
            },
            timeout: 2000000,
          });
        this.resultsOK = true;
        return response.data.ehr;
      }
      catch (error) {
        console.error("Error in deleteehr:", error);
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
    async deletestoredquery(queryname, queryversion) {
      console.log('inside deletestoredquery')
      console.log(localStorage.getItem("authToken"))
      console.log('queryname=', queryname)
      console.log('queryversion=', queryversion)
      this.isLoading = true;
      this.resultsOK = false;
      // await this.sleep(5000);
      try {
        const response = await axios.delete(`http://${BACKEND_HOST}/admin/query/`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            params: {
              queryname: queryname,
              version: queryversion
            },
            timeout: 2000000,
          });
        this.resultsOK = true;
        return response.data.query;
      }
      catch (error) {
        console.error("Error in deletestoredquery:", error);
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
    },
    async fetchQueryNames() {
      try {
        console.log('fetchQueryNames called');
        this.isLoadingQueryNames = true;
        this.queryNames = [];
        const response = await axios.get(`http://${BACKEND_HOST}/query/query`,
          { method: 'GET', headers: { 'Authorization': `Bearer ${localStorage.getItem("authToken")}` }, },
          { timeout: 2000000 });
        this.isLoadingQueryNames = false;
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
        console.log(response);
        console.log(response.data);
        this.nametoversions = response.data.query.nametoversions;
        this.queries = response.data.query.queries;
        console.log('this.nametoversions', this.nametoversions);
        this.queryNames = Object.keys(this.nametoversions);
        console.log('this.queryNames', this.queryNames);
        this.queriesinfo = response.data.query.queriesinfo;
        if (this.index2 === 5) {
          console.log('queryNamessssssssss', this.queryNames);
          if (!this.queryNames.includes('None')) {
            this.queryNames.unshift('None');
            console.log('queryNamessssssssss', this.queryNames);
            this.nametoversions['None'] = [''];
          }
        }

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
        this.isLoadingQueryNames = false;
      }

      return this.queriesinfo;
    },
    async fetchQuery(queryname, queryversion) {
      try {
        if (queryname === 'None') {
          this.aql = '';
          return;
        }
        if (!queryname && !queryversion) {
          return;
        }
        console.log('fetchQuery called');

        const response = await axios.get(`http://${BACKEND_HOST}/query/`,
          {
            headers: { 'Authorization': `Bearer ${localStorage.getItem("authToken")}` },
            params: {
              queryname: queryname,
              version: queryversion,
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
          console.error("Error fetching query:", response);
          return;
        }
        this.aql = response.data.query.q;

      } catch (error) {
        console.error("Error fetching query", error);
        if (error?.response?.status) {
          if (error.response.status === 401) {
            console.error("Unauthorized access. Please login again.");
            this.logout();
            return
          }
        }
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

.results-content-first {
  display: flex;
  justify-content: center;
}

.button-wrapper {
  position: relative;
  display: inline-block;
}

.my-button {
  position: relative;
  /* Enables the overlay to anchor to this */
  z-index: 1;
  /* So the button is above background if needed */
}

.overlay {
  position: absolute;
  top: 0%;
  left: 85%;
  transform: rotate(-30deg);
  color: rgba(255, 0, 0, 0.5);
  font-weight: bold;
  font-size: 10px;
  background-color: rgba(255, 255, 255, 0.7);
  padding: 4px 8px;
  text-align: center;
  line-height: 1.2;
  pointer-events: none;
  white-space: nowrap;
}
</style>
