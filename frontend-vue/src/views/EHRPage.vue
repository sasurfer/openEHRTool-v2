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
      <div class="radio-group-container">
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
              <input v-model="param.value" :type="param.type" :placeholder="param.placeholder" />
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
    filteredMethods() {
      return this.currentMethods.filter(method => method.type.includes(this.methodType) && method.what.includes(this.onwhat));
    },
  },
  mounted() {
    // Fetch data when the component is first mounted
    this.fetchEHRdata();
    this.fetchTemplateData();
    this.fetchCompositionData();
    this.fetchAQLData();
    this.currentMethods = this.getMethodsForEHR();
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
        { file: false, label: '' },
        { file: false, label: '' },
        { file: true, label: 'Choose EHRStatus File' },
        { file: true, label: 'Choose EHRStatus File' },
        { file: false, label: '' },
        { file: false, label: '' },
        { file: false, label: '' },
        { file: false, label: '' },
        { file: false, label: '' },
        { file: false, label: '' },
        { file: true, label: 'Choose Directory/Folder File' },
        { file: true, label: 'Choose Directory/Folder File' },
        { file: false, label: '' },
        { file: false, label: '' }
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
    },
    getMethodsForEHR() {
      const methods = {
        'methods': [
          { label: 'Retrieve EHR by EHRid', type: ['Get'], what: ['ehr'] },//1
          { label: 'Retrieve EHR by SubjectId, SubjectNameSpace', type: ['Get'], what: ['ehr'] },//2
          { label: ' Create EHR with/without EHRid specified', type: ['Post', 'Put'], what: ['ehr'] },//3
          { label: 'Create EHR with SubjectId, SubjectNameSpace specified', type: ['Post', 'Put'], what: ['ehr'] },//4
          { label: 'Create EHR via EHRStatus', type: ['Post'], what: ['ehr', 'ehrstatus'] },//5
          { label: 'Update EHRStatus', type: ['Put'], what: ['ehrstatus'] },//6
          { label: 'Retrieve EHRStatus at time', type: ['Get'], what: ['ehrstatus'] },//7
          { label: 'Retrieve EHRStatus by version', type: ['Get'], what: ['ehrstatus'] },//8
          { label: 'Retrieve versioned EHRStatus info', type: ['Get'], what: ['ehrstatus'] },//9
          { label: 'Retrieve versioned EHRStatus revision history', type: ['Get'], what: ['ehrstatus'] },//10
          { label: 'Retrieve versioned EHRStatus at time', type: ['Get'], what: ['ehrstatus'] },//11
          { label: 'Retrieve versioned EHRStatus by version', type: ['Get'], what: ['ehrstatus'] },//12
          { label: 'Create Directory', type: ['Post'], what: ['folder'] },//13
          { label: 'Update Directory', type: ['Put'], what: ['folder'] },//14
          { label: 'Retrieve Directory/Folder at time', type: ['Get'], what: ['folder'] },//15
          { label: 'Retrieve Directory/Folder by version', type: ['Get'], what: ['folder'] },//16
          { label: 'Delete Directory/Folder', type: ['Del'], what: ['folder'] },//17

        ]
      };
      return methods['methods'] || [];
    },

    // Get actions associated with the selected method
    getActionsForMethod(index) {
      const actions = [
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_ehrid' }],//1
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_sid_sns' }],//2
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_ehrid_post' }],//3
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_ehrid_sid_sns_post' }],//4
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_ehrstatus' }],//5
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_ehrstatus_update' }],//6
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_ehrstatus_get_at_time' }],//7
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_ehrstatus_get_by_version' }],//8
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_ehrstatus_get_versioned_info' }],//9
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_ehrstatus_get_versioned_history' }],//10
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_ehrstatus_get_versioned_at_time' }],//11
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_ehrstatus_get_versioned_by_version' }],//12
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_folder' }],//13
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_folder_update' }],//14
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_folder_get_at_time' }],//15
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_folder_get_by_version' }],//16        
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_folder_delete' }],//17

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
        [{ label: 'Output Format', selected: "JSON", options: ['JSON', 'XML'] }],//15
        [{ label: 'Output Format', selected: "JSON", options: ['JSON', 'XML'] }],//16
        [],//17
      ];
      return radioParams[index] || [];
    },
    // Get input parameters for the selected method
    getParamsForMethod(index) {
      const params = [
        [//1
          { label: 'EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" },
          // { label: '1 GET', value: "", type: 'text' }
        ],
        [//2
          { label: 'SubjectId', value: '', type: 'text', placeholder: "Patient1234" },
          { label: 'SubjectNameSpace', value: '', type: 'text', placeholder: "Acme" },
          // { label: '2 GET', value: "", type: 'text' }
        ],
        [//3
          { label: 'EHRid (optional)', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" },
          // { label: '1 POST', value: "", type: 'text' }
        ],
        [//4
          { label: 'EHRid (optional)', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" }, { label: 'SubjectId', value: '', type: 'text', placeholder: "Patient1234" },
          { label: 'SubjectNameSpace', value: '', type: 'text', placeholder: "Acme" },
          // { label: '2 POST', value: "", type: 'text' }
        ],
        [],//5
        [//6
          { label: 'EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" },
          { label: 'EHRStatus versioned id', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646::local.ehrbase.org::1" }],
        [//7
          { label: 'EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" }, { label: 'At time (optional)', value: '', type: 'text', placeholder: "2020-01-20T16:40:07.227+01:00" }],
        [//8
          { label: 'EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" }, { label: 'EHRStatus versioned id (optional)', value: '', type: 'text', placeholder: "afe46cce-d8c9-4db8-940b-ee3db170a646::local.ehrbase.org::1" }],
        [//9
          { label: 'EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" }],
        [//10
          { label: 'EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" }],
        [//11
          { label: 'EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" }, { label: 'At time (optional)', value: '', type: 'text', placeholder: "2020-01-20T16:40:07.227+01:00" }],
        [//12
          { label: 'EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" }, { label: 'EHRStatus versioned id (optional)', value: '', type: 'text', placeholder: "afe46cce-d8c9-4db8-940b-ee3db170a646::local.ehrbase.org::1" }],
        [//13
          { label: 'EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" }],
        [//14
          { label: 'EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" }, { label: 'Directory folder versioned id', value: '', type: 'text', placeholder: "afe46cce-d8c9-4db8-940b-ee3db170a646::local.ehrbase.org::1" }],
        [//15
          { label: 'EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" },
          { label: 'Path (optional)', value: '', type: 'text' }, { label: 'At time (optional)', value: '', type: 'text', placeholder: "2050-01-20T16:40:07.227+01:00" },
        ],
        [//16
          { label: 'EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" },
          { label: 'Path (optional)', value: '', type: 'text' }, { label: 'Directory folder versioned id (optional)', value: '', type: 'text', placeholder: "afe46cce-d8c9-4db8-940b-ee3db170a646::local.ehrbase.org::1" }
        ],
        [//17
          { label: 'EHRid', value: '', type: 'text', placeholder: "56e46cce-d8c9-4db8-940b-ee3db170a646" },
          { label: 'Directory folder versioned id', value: '', type: 'text', placeholder: "afe46cce-d8c9-4db8-940b-ee3db170a646::local.ehrbase.org::1" }
        ],

      ];
      return params[index] || [];
    },

    // Handle action button click
    async executeAction(action) {
      this.results = null
      if (action == 'submit_ehrid') //get ehr by ehrid
      {
        const ehrid = this.currentParams.find(p => p.label === 'EHRid');
        console.log(ehrid);
        if (ehrid.value) {
          console.log('ehrid is', ehrid.value);
          try {
            const ehrResults = await this.getehrbyehrid(ehrid.value);
            console.log('results', ehrResults);
            this.results = JSON.stringify(ehrResults, null, 2);
          }
          catch (error) {
            console.error("Error in executeAction:", error);
            this.results = `Error: ${error.message}`;
          }
        } else {
          this.results = 'EHRid is required';
        }
      } else if (action == 'submit_sid_sns')//get ehr by subjectid and subjectnamespace
      {
        const subjectid = this.currentParams.find(p => p.label === 'SubjectId');
        const subjectnamespace = this.currentParams.find(p => p.label === 'SubjectNameSpace');
        if (subjectid.value && subjectnamespace.value) {
          try {
            const ehrResults = await this.getehrbysidandsns(subjectid.value, subjectnamespace.value);
            console.log('results', ehrResults);
            this.results = JSON.stringify(ehrResults, null, 2);
          }
          catch (error) {
            console.error("Error in executeAction:", error);
            this.results = `Error: ${error.message}`;
          }
        } else {
          this.results = 'SubjectId and SubjectNameSpace are required';
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
        this.subjectid = '';
        this.subjectnamespace = '';
        this.ehrid = '';
      } else if (action == 'submit_ehrid_post') //Post ehr with/without ehrid
      {
        this.resultsOK = false;
        const ehrid = this.currentParams.find(p => p.label === 'EHRid (optional)');
        console.log('ehrid is', ehrid?.value);
        this.ehrid = ehrid?.value || "";
        console.log('ehrid is', this.ehrid);
        try {
          const ehrResults = await this.postehrbyehrid(this.ehrid);
          console.log('results', ehrResults);
          this.results = JSON.stringify(ehrResults, null, 2);
        }
        catch (error) {
          console.error("Error in executeAction:", error);
          this.results = `Error: ${error.message}`;
        }

      } else if (action == 'submit_ehrid_sid_sns_post') //Post ehr with/without ehrid with subjectid and subjectnamespace
      {
        this.resultsOK = false;
        const ehrid = this.currentParams.find(p => p.label === 'EHRid (optional)');
        const subjectid = this.currentParams.find(p => p.label === 'SubjectId');
        const subjectnamespace = this.currentParams.find(p => p.label === 'SubjectNameSpace');
        console.log('ehrid is', ehrid?.value);
        this.ehrid = ehrid?.value || "";
        console.log('ehrid is', this.ehrid);
        if (subjectid.value && subjectnamespace.value) {
          try {
            const ehrResults = await this.postehrbysidsns(this.ehrid, subjectid.value, subjectnamespace.value);
            console.log('results', ehrResults);
            this.results = JSON.stringify(ehrResults, null, 2);
          }
          catch (error) {
            console.error("Error in executeAction:", error);
            this.results = `Error: ${error.message}`;
          }
        }
        else {
          this.results = 'SubjectId and SubjectNameSpace are required';
        }
      } else if (action == 'submit_ehrstatus') //post ehr with ehrstatus
      {
        console.log('inside submit_ehrstatus')
        this.resultsOK = false;
        if (!this.selectedFile) {
          this.results = 'Please select an EHRStatus file'
          return;
        }
        try {
          const reader = new FileReader();
          reader.onload = async () => {
            try {
              const ehrstatus = JSON.parse(reader.result);
              console.log('ehrstatus is', ehrstatus);
              const ehrResults = await this.postehrstatus(ehrstatus);
              console.log('results', ehrResults);
              this.results = JSON.stringify(ehrResults, null, 2);
            }
            catch (error) {
              console.error("Error uploading JSON file:", error);
              this.results = `Error: ${error.message}`;
            }
          };
          reader.readAsText(this.selectedFile);
        }
        catch (error2) {
          console.error("Error in postehrstatus:", error2);
          this.results = `Error: ${error2.message}`;
        }
      }
      else if (action == 'submit_ehrstatus_update') //update ehrstatus
      {
        console.log('inside submit_ehrstatus_update')
        this.resultsOK = false;
        const ehrid = this.currentParams.find(p => p.label === 'EHRid');
        const ehrstatusversionedid = this.currentParams.find(p => p.label === 'EHRStatus versioned id');

        if (!this.selectedFile) {
          this.results = 'Please select an EHRStatus file'
          return;
        }
        if (!ehrid.value || !ehrstatusversionedid.value) {
          this.results = 'EHRid and EHRstatus versioned id are required';
          return;
        }
        try {
          const reader = new FileReader();
          reader.onload = async () => {
            try {
              const ehrstatus = JSON.parse(reader.result);
              const ehrResults = await this.putehrstatus(ehrstatus, ehrid.value, ehrstatusversionedid.value);
              console.log('results', ehrResults);
              this.results = JSON.stringify(ehrResults, null, 2);
            }
            catch (error) {
              console.error("Error uploading JSON file:", error);
              this.results = `Error: ${error.message}`;
            }
          };

          reader.readAsText(this.selectedFile);
        }
        catch (error2) {
          console.error("Error in putehrstatus:", error2);
          this.results = `Error: ${error2.message}`;
        }
      }
      else if (action == 'submit_ehrstatus_get_at_time') //get ehrstatus at time
      {
        console.log('inside submit_ehrstatus_get_at_time')
        this.resultsOK = false;
        const ehrid = this.currentParams.find(p => p.label === 'EHRid');
        const timestamp = this.currentParams.find(p => p.label === 'At time (optional)');
        this.timestamp = timestamp?.value || "";
        console.log('timestamp is', this.timestamp);

        if (ehrid.value) {
          console.log('ehrid is', ehrid.value);
          try {
            const ehrResults = await this.getehrstatusattime(ehrid.value, this.timestamp);
            console.log('results', ehrResults);
            this.results = JSON.stringify(ehrResults, null, 2);
          }
          catch (error) {
            console.error("Error in executeAction:", error);
            this.results = `Error: ${error.message}`;
          }
        } else {
          this.results = 'EHRid is required';
        }
      }
      else if (action == 'submit_ehrstatus_get_by_version') //get ehrstatus by version
      {
        console.log('inside submit_ehrstatus_get_by_version')
        this.resultsOK = false;
        const ehrid = this.currentParams.find(p => p.label === 'EHRid');
        const version = this.currentParams.find(p => p.label === 'EHRStatus versioned id (optional)');
        this.version = version?.value || "";
        console.log('version is', this.version);

        if (ehrid.value) {
          console.log('ehrid is', ehrid.value);
          try {
            const ehrResults = await this.getehrstatusbyversion(ehrid.value, this.version);
            console.log('results', ehrResults);
            this.results = JSON.stringify(ehrResults, null, 2);
          }
          catch (error) {
            console.error("Error in executeAction:", error);
            this.results = `Error: ${error.message}`;
          }
        } else {
          this.results = 'EHRid is required';
        }
      }
      else if (action == 'submit_ehrstatus_get_versioned_info') //get versioned ehrstatus info
      {
        console.log('inside submit_ehrstatus_get_versioned_info')
        this.resultsOK = false;
        const ehrid = this.currentParams.find(p => p.label === 'EHRid');

        if (ehrid.value) {
          console.log('ehrid is', ehrid.value);
          try {
            const ehrResults = await this.getehrstatusversionedinfo(ehrid.value);
            console.log('results', ehrResults);
            this.results = JSON.stringify(ehrResults, null, 2);
          }
          catch (error) {
            console.error("Error in executeAction:", error);
            this.results = `Error: ${error.message}`;
          }
        } else {
          this.results = 'EHRid is required';
        }
      }
      else if (action == 'submit_ehrstatus_get_versioned_history') //get versioned ehrstatus revision history
      {
        console.log('inside submit_ehrstatus_get_versioned_history')
        this.resultsOK = false;
        const ehrid = this.currentParams.find(p => p.label === 'EHRid');

        if (ehrid.value) {
          console.log('ehrid is', ehrid.value);
          try {
            const ehrResults = await this.getehrstatusversionedhistory(ehrid.value);
            console.log('results', ehrResults);
            this.results = JSON.stringify(ehrResults, null, 2);
          }
          catch (error) {
            console.error("Error in executeAction:", error);
            this.results = `Error: ${error.message}`;
          }
        } else {
          this.results = 'EHRid is required';
        }
      }
      else if (action == 'submit_ehrstatus_get_versioned_at_time') //get ehrstatus versioned at time
      {
        console.log('inside submit_ehrstatus_get_versioned_at_time')
        this.resultsOK = false;
        const ehrid = this.currentParams.find(p => p.label === 'EHRid');
        const timestamp = this.currentParams.find(p => p.label === 'At time (optional)');
        this.timestamp = timestamp?.value || "";
        console.log('timestamp is', this.timestamp);

        if (ehrid.value) {
          console.log('ehrid is', ehrid.value);
          try {
            const ehrResults = await this.getehrstatusversionedattime(ehrid.value, this.timestamp);
            console.log('results', ehrResults);
            this.results = JSON.stringify(ehrResults, null, 2);
          }
          catch (error) {
            console.error("Error in executeAction:", error);
            this.results = `Error: ${error.message}`;
          }
        } else {
          this.results = 'EHRid is required';
        }
      }
      else if (action == 'submit_ehrstatus_get_versioned_by_version') //get ehrstatus versioned by version
      {
        console.log('inside submit_ehrstatus_get_versioned_by_version')
        this.resultsOK = false;
        const ehrid = this.currentParams.find(p => p.label === 'EHRid');
        const version = this.currentParams.find(p => p.label === 'EHRStatus versioned id (optional)');
        this.version = version?.value || "";
        console.log('version is', this.version);

        if (ehrid.value) {
          console.log('ehrid is', ehrid.value);
          try {
            const ehrResults = await this.getehrstatusversionedbyversion(ehrid.value, this.version);
            console.log('results', ehrResults);
            this.results = JSON.stringify(ehrResults, null, 2);
          }
          catch (error) {
            console.error("Error in executeAction:", error);
            this.results = `Error: ${error.message}`;
          }
        } else {
          this.results = 'EHRid is required';
        }
      }
      else if (action == 'submit_folder') //post directory
      {
        console.log('inside submit_folder')
        this.resultsOK = false;
        if (!this.selectedFile) {
          this.results = 'Please select a Directory folder file'
          return;
        }
        const ehrid = this.currentParams.find(p => p.label === 'EHRid');
        console.log('ehrid is', ehrid?.value);
        if (!ehrid?.value) {
          this.results = 'EHRid is required';
          return;
        }
        try {
          const reader = new FileReader();
          reader.onload = async () => {
            try {
              const folder = JSON.parse(reader.result);
              console.log('folder is', folder);
              const ehrResults = await this.postdirectory(ehrid.value, folder);
              console.log('results', ehrResults);
              this.results = JSON.stringify(ehrResults, null, 2);
            }
            catch (error) {
              console.error("Error uploading JSON file:", error);
              this.results = `Error: ${error.message}`;
            }
          };
          reader.readAsText(this.selectedFile);
        }
        catch (error2) {
          console.error("Error in postdirectory:", error2);
          this.results = `Error: ${error2.message}`;
        }
      }
      else if (action == 'submit_folder_update') //put directory
      {
        console.log('inside submit_folder_update')
        this.resultsOK = false;
        if (!this.selectedFile) {
          this.results = 'Please select a Directory folder file'
          return;
        }
        const ehrid = this.currentParams.find(p => p.label === 'EHRid');
        console.log('ehrid is', ehrid?.value);
        if (!ehrid?.value) {
          this.results = 'EHRid is required';
          return;
        }
        const versionedid = this.currentParams.find(p => p.label === 'Directory folder versioned id');
        if (!versionedid?.value) {
          this.results = 'Directory folder versioned id is required';
          return;
        }
        try {
          const reader = new FileReader();
          reader.onload = async () => {
            try {
              const folder = JSON.parse(reader.result);
              console.log('folder is', folder);
              const ehrResults = await this.putdirectory(ehrid.value, folder, versionedid.value);
              console.log('results', ehrResults);
              this.results = JSON.stringify(ehrResults, null, 2);
            }
            catch (error) {
              console.error("Error uploading JSON file:", error);
              this.results = `Error: ${error.message}`;
            }
          };
          reader.readAsText(this.selectedFile);
        }
        catch (error2) {
          console.error("Error in putdirectory:", error2);
          this.results = `Error: ${error2.message}`;
        }
      }
      else if (action == 'submit_folder_get_at_time') //get directory at time 
      {
        console.log('inside submit_folder_get_at_time')
        this.resultsOK = false;
        const ehrid = this.currentParams.find(p => p.label === 'EHRid');
        const timestamp = this.currentParams.find(p => p.label === 'At time (optional)');
        this.timestamp = timestamp?.value || "";
        console.log('timestamp is', this.timestamp);
        const path = this.currentParams.find(p => p.label === 'Path (optional)');
        this.path = path?.value || "";
        console.log('path is', this.path);
        this.format = this.currentRadioParams.find(p => p.label === 'Output Format')?.selected || "JSON";
        console.log('format is', this.format);


        if (ehrid.value) {
          console.log('ehrid is', ehrid.value);
          try {
            const ehrResults = await this.getdirectoryattime(ehrid.value, this.timestamp, this.path, this.format);
            console.log('results', ehrResults);
            if (this.format.toLowerCase() == 'xml') {
              this.resultsName = 'results.xml';
              this.results = this.formatXml(ehrResults);
            }
            else {
              this.resultsName = 'results.json';
              this.results = JSON.stringify(ehrResults, null, 2);
            }
          }
          catch (error) {
            console.error("Error in executeAction:", error);
            this.results = `Error: ${error.message}`;
          }
        } else {
          this.results = 'EHRid is required';
        }
      }
      else if (action == 'submit_folder_get_by_version') //get folder by version
      {
        console.log('inside submit_folder_get_by_version')
        this.resultsOK = false;
        const ehrid = this.currentParams.find(p => p.label === 'EHRid');
        const version = this.currentParams.find(p => p.label === 'Directory folder versioned id (optional)');
        this.version = version?.value || "";
        console.log('version is', this.version);
        const path = this.currentParams.find(p => p.label === 'Path (optional)');
        this.path = path?.value || "";
        this.format = this.currentRadioParams.find(p => p.label === 'Output Format')?.selected || "JSON";
        console.log('format is', this.format);

        if (ehrid.value) {
          console.log('ehrid is', ehrid.value);
          try {
            const ehrResults = await this.getdirectorybyversion(ehrid.value, this.version, this.path, this.format);
            console.log('results', ehrResults);
            if (this.format.toLowerCase() == 'xml') {
              this.resultsName = 'results.xml';
              this.results = this.results = this.formatXml(ehrResults);
            }
            else {
              this.resultsName = 'results.json';
              this.results = JSON.stringify(ehrResults, null, 2);
            }
          }
          catch (error) {
            console.error("Error in executeAction:", error);
            this.results = `Error: ${error.message}`;
          }
        } else {
          this.results = 'EHRid is required';
        }
      }
      else if (action == 'submit_folder_delete') //delete  directory
      {
        console.log('inside submit_folder_delete')
        this.resultsOK = false;
        const ehrid = this.currentParams.find(p => p.label === 'EHRid');
        const version = this.currentParams.find(p => p.label === 'Directory folder versioned id');
        if (!ehrid?.value) {
          this.results = 'EHRid is required';
          return;
        }
        if (!version?.value) {
          this.results = 'Directory folder versioned id is required';
          return;
        }
        try {
          const ehrResults = await this.deletedirectory(ehrid.value, version.value);
          console.log('results', ehrResults);
          this.results = JSON.stringify(ehrResults, null, 2);
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
    async getehrbyehrid(ehrid) {
      console.log('inside getehrbyehrid')
      console.log(ehrid)
      console.log(localStorage.getItem("authToken"))
      this.isLoading = true;
      this.resultsOK = false;
      // await this.sleep(5000);
      try {
        console.log('before get')
        const response = await axios.get(`http://127.0.0.1:5000/ehr/${ehrid}`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            timeout: 2000000,
          });
        this.resultsOK = true;
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
          if (402 <= error.response.status <= 500) {
            return error.response.data;
          }

          throw { status: 500, message: `An unexpected error occurred ${error.response.status}` };
        }
      } finally {
        this.isLoading = false;
      }
    },
    async getehrbysidandsns(subjectid, subjectnamespace) {
      console.log('inside getehrbysidandsns')
      console.log(localStorage.getItem("authToken"))
      console.log(subjectid)
      console.log(subjectnamespace)
      this.isLoading = true;
      this.resultsOK = false;
      // await this.sleep(5000);
      try {
        console.log('before get')
        const response = await axios.get(`http://127.0.0.1:5000/ehr/subjectid/${subjectid}/subjectnamespace/${subjectnamespace}`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            timeout: 2000000,
          });
        this.resultsOK = true;
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
          if (402 <= error.response.status <= 500) {
            return error.response.data;
          }
          throw { status: 500, message: `An unexpected error occurred ${error.response.status}` };
        }
      } finally {
        this.isLoading = false;
      }
    },
    async postehrbyehrid(ehrid) {
      console.log('inside postehrbyehrid')
      console.log('ehrid=', ehrid)
      console.log(localStorage.getItem("authToken"))
      this.isLoading = true;
      this.resultsOK = false;
      // await this.sleep(5000);
      try {
        console.log('before post')
        const response = await axios.post(`http://127.0.0.1:5000/ehr/${ehrid}`,
          {},
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
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
          if (402 <= error.response.status <= 500) {
            return error.response.data;
          }
          throw { status: 500, message: `An unexpected error occurred ${error.response.status}` };
        }
      } finally {
        this.isLoading = false;
      }
    },
    async postehrbysidsns(ehrid, subjectid, subjectnamespace) {
      console.log('inside postehrbysidsns')
      console.log('ehrid=', ehrid)
      console.log(localStorage.getItem("authToken"))
      this.isLoading = true;
      this.resultsOK = false;
      // await this.sleep(5000);
      try {
        console.log('before post')
        if (ehrid) {
          const response = await axios.post(`http://127.0.0.1:5000/ehr/${ehrid}/subjectid/${subjectid}/subjectnamespace/${subjectnamespace}`,
            {},
            {
              headers: {
                'Authorization': `Bearer ${localStorage.getItem("authToken")}`
              },
              timeout: 2000000,
            });
          return response.data.ehr;
        } else {
          const response = await axios.post(`http://127.0.0.1:5000/ehr/subjectid/${subjectid}/subjectnamespace/${subjectnamespace}`,
            {},
            {
              headers: {
                'Authorization': `Bearer ${localStorage.getItem("authToken")}`
              },
              timeout: 2000000,
            });
          return response.data.ehr;
        }
      }
      catch (error) {
        console.error("Error in postehrbysidsns:", error);
        if (error?.response?.status) {
          if (error.response.status === 401) {
            console.error("Unauthorized access. Please login again.");
            this.logout();
            return
          }
          if (402 <= error.response.status < 500) {
            return error.response.data;
          }

          if (error.response.status === 500) {
            return error.response.data;
            // throw { status: 500, message: "Server error" };
          }
          throw { status: 500, message: `An unexpected error occurred ${error.response.status}` };
        }
      } finally {
        this.isLoading = false;
      }
    },
    async postehrstatus(ehrstatus) {
      console.log('inside postehrstatus');
      console.log('ehrstatus=', ehrstatus);
      console.log(localStorage.getItem("authToken"))
      this.isLoading = true;
      this.resultsOK = false;
      const ehrstatusstring = JSON.stringify(ehrstatus);
      // await this.sleep(5000);
      try {
        console.log('before post');
        const response = await axios.post(`http://127.0.0.1:5000/ehr/ehrstatus`,
          { "ehrstatus": ehrstatusstring },
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            timeout: 2000000,
          });
        return response.data.ehr;
      }
      catch (error) {
        console.error("Error in postehrstatus:", error);
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
    async putehrstatus(ehrstatus, ehrid, ehrstatusversionedid) {
      console.log('inside putehrstatus');
      console.log('ehrstatus=', ehrstatus);
      console.log('ehrid=', ehrid);
      console.log('ehrstatusversionedid=', ehrstatusversionedid);
      console.log(localStorage.getItem("authToken"))
      this.isLoading = true;
      this.resultsOK = false;
      const ehrstatusstring = JSON.stringify(ehrstatus);
      // await this.sleep(5000);
      try {
        console.log('before post');
        const response = await axios.put(`http://127.0.0.1:5000/ehr/ehrstatus`,
          { "ehrstatus": ehrstatusstring, "ehrid": ehrid, "ehrstatusVersionedId": ehrstatusversionedid },
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`, 'Content-Type': 'application/json'
            },
            timeout: 2000000,
          });
        return response.data.ehr;
      }
      catch (error) {
        console.error("Error in putehrstatus:", error);
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
    async getehrstatusattime(ehrid, timestamp) {
      console.log('inside getehrstatusattime')
      console.log(ehrid)
      console.log(localStorage.getItem("authToken"))
      this.isLoading = true;
      this.resultsOK = false;
      // await this.sleep(5000);
      try {
        console.log('before get')
        const response = await axios.get(`http://127.0.0.1:5000/ehr/${ehrid}/ehrstatus`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            params: {
              data: timestamp
            },
            timeout: 2000000,
          });
        this.resultsOK = true;
        return response.data.ehrstatus;
      }
      catch (error) {
        console.error("Error in getehrstatusattime:", error);
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
    async getehrstatusbyversion(ehrid, version) {
      console.log('inside getehrstatusbyversion')
      console.log(ehrid)
      console.log(localStorage.getItem("authToken"))
      this.isLoading = true;
      this.resultsOK = false;
      // await this.sleep(5000);
      try {
        console.log('before get')
        const response = await axios.get(`http://127.0.0.1:5000/ehr/${ehrid}/ehrstatus`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            params: {
              data: version
            },
            timeout: 2000000,
          });
        this.resultsOK = true;
        return response.data.ehrstatus;
      }
      catch (error) {
        console.error("Error in getehrstatusbyversion:", error);
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
    async getehrstatusversionedinfo(ehrid) {
      console.log('inside getehrstatusversionedinfo')
      console.log(ehrid)
      console.log(localStorage.getItem("authToken"))
      this.isLoading = true;
      this.resultsOK = false;
      // await this.sleep(5000);
      try {
        console.log('before get')
        const response = await axios.get(`http://127.0.0.1:5000/ehr/${ehrid}/vehrstatus`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            params: {
              data: 'versionedinfo'
            },
            timeout: 2000000,
          });
        this.resultsOK = true;
        return response.data.ehrstatus;
      }
      catch (error) {
        console.error("Error in getehrstatusversionedinfo:", error);
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
    async getehrstatusversionedhistory(ehrid) {
      console.log('inside getehrstatusversionedhistory')
      console.log(ehrid)
      console.log(localStorage.getItem("authToken"))
      this.isLoading = true;
      this.resultsOK = false;
      // await this.sleep(5000);
      try {
        console.log('before get')
        const response = await axios.get(`http://127.0.0.1:5000/ehr/${ehrid}/vehrstatus`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            params: {
              data: 'versionedhistory'
            },
            timeout: 2000000,
          });
        this.resultsOK = true;
        return response.data.ehrstatus;
      }
      catch (error) {
        console.error("Error in getehrstatusversionedhistory:", error);
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
    async getehrstatusversionedattime(ehrid, timestamp) {
      console.log('inside getehrstatusversionedattime')
      console.log(ehrid)
      console.log(localStorage.getItem("authToken"))
      this.isLoading = true;
      this.resultsOK = false;
      // await this.sleep(5000);
      try {
        console.log('before get')
        const response = await axios.get(`http://127.0.0.1:5000/ehr/${ehrid}/vehrstatus`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            params: {
              data: timestamp
            },
            timeout: 2000000,
          });
        this.resultsOK = true;
        return response.data.ehrstatus;
      }
      catch (error) {
        console.error("Error in getehrstatusversionedattime:", error);
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
    async getehrstatusversionedbyversion(ehrid, version) {
      console.log('inside getehrstatusversionedbyversion')
      console.log(ehrid)
      console.log(localStorage.getItem("authToken"))
      this.isLoading = true;
      this.resultsOK = false;
      // await this.sleep(5000);
      try {
        console.log('before get')
        const response = await axios.get(`http://127.0.0.1:5000/ehr/${ehrid}/vehrstatus`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            params: {
              data: version
            },
            timeout: 2000000,
          });
        this.resultsOK = true;
        return response.data.ehrstatus;
      }
      catch (error) {
        console.error("Error in getehrstatusversionedbyversion:", error);
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
    async postdirectory(ehrid, folder) {
      console.log('inside postdirectory')
      console.log('folder=', folder);
      console.log(localStorage.getItem("authToken"))
      this.isLoading = true;
      this.resultsOK = false;
      const folderstring = JSON.stringify(folder);
      // await this.sleep(5000);
      try {
        console.log('before post');
        const response = await axios.post(`http://127.0.0.1:5000/ehr/${ehrid}/directory`,
          { "directory": folderstring },
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            timeout: 2000000,
          });
        return response.data.folder;
      }
      catch (error) {
        console.error("Error in postdirectory:", error);
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
    async putdirectory(ehrid, folder, foldervid) {
      console.log('inside putdirectory')
      console.log('folder=', folder);
      console.log(localStorage.getItem("authToken"))
      this.isLoading = true;
      this.resultsOK = false;
      const folderstring = JSON.stringify(folder);
      // await this.sleep(5000);
      try {
        const response = await axios.put(`http://127.0.0.1:5000/ehr/${ehrid}/directory`,
          { "directory": folderstring, "directoryVersionedId": foldervid },
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            timeout: 2000000,
          });
        return response.data.folder;
      }
      catch (error) {
        console.error("Error in postdirectory:", error);
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
    async getdirectoryattime(ehrid, timestamp, path, format) {
      console.log('inside getdirectoryattime')
      console.log(ehrid)
      console.log(localStorage.getItem("authToken"))
      this.isLoading = true;
      this.resultsOK = false;
      // await this.sleep(5000);
      try {
        console.log('before get')
        const response = await axios.get(`http://127.0.0.1:5000/ehr/${ehrid}/directory`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            params: {
              data: timestamp,
              path: path,
              format: format
            },
            timeout: 2000000,
          });
        this.resultsOK = true;
        return response.data.folder;
      }
      catch (error) {
        console.error("Error in getdorectoryattime:", error);
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
    async getdirectorybyversion(ehrid, version, path, format) {
      console.log('inside getdirectorybyversion')
      console.log(ehrid)
      console.log(localStorage.getItem("authToken"))
      this.isLoading = true;
      this.resultsOK = false;
      // await this.sleep(5000);
      try {
        console.log('before get')
        const response = await axios.get(`http://127.0.0.1:5000/ehr/${ehrid}/directory`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            params: {
              data: version,
              path: path,
              format: format
            },
            timeout: 2000000,
          });
        this.resultsOK = true;
        return response.data.folder;
      }
      catch (error) {
        console.error("Error in getdirectorybyversion:", error);
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
    async deletedirectory(ehrid, version) {
      console.log('inside deletedirectory')
      console.log(ehrid)
      console.log(localStorage.getItem("authToken"))
      this.isLoading = true;
      this.resultsOK = false;
      // await this.sleep(5000);
      try {
        console.log('before get')
        const response = await axios.delete(`http://127.0.0.1:5000/ehr/${ehrid}/directory`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            params: {
              value: version
            },
            timeout: 2000000,
          });
        this.resultsOK = true;
        return response.data.folder;
      }
      catch (error) {
        console.error("Error in deletedirectory:", error);
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
  overflow-x: auto;
  /* Add horizontal scroll to results section */
  overflow-y: hidden;
  /* Disable vertical scroll */
  white-space: nowrap;
  /* Prevent text wrapping */
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
  overflow-x: auto;
  /* Enable horizontal scrolling */
  overflow-y: hidden;
  /* Disable vertical scrolling */
  white-space: nowrap;
  /* Prevent text wrapping */
  padding: 10px;
  /* Add some padding */
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
</style>
