<template>
  <div id="app">
    <!-- You can have a global navbar, footer, or other common layout elements here -->
    <Sidebar @open-user-info="openUserInfo" />
    <rsidebar @open-ehr-info="openEHRInfo" @open-template-info="openTemplateInfo"
      @open-composition-info="openCompositionInfo" @open-aql-info="openAQLInfo" />
    <UserInfoModal v-if="isUserInfoVisible" :isVisible="isUserInfoVisible" :user="user" @close-modal="closeModal"
      @logout="logout" />

    <div class="method-selection-zone">
      <h3><i>Query Methods</i></h3>
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
        </div>
        <div class="radio-group">
          <label>
            <input type="radio" v-model="onwhat" value="query" />
            Query
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
        <div class="input-section">
          <div class="parameters-title">
            <h3>Input</h3>
          </div>
          <div class="parameter-container">
            <div class="parameter-form">

              <form @submit.prevent="submitForm">
                <div v-if="filteredMethods[selectedMethod].label === 'Run Stored Query'" class="form-group">

                  <div v-for="(param, index) in currentParams.filter(p => p.type === 'select')" :key="index"
                    class="form-group">

                    <label>{{ param.label }}:</label>
                    <select v-model="param.value" class="form-select">

                      <!-- Default disabled option -->
                      <option disabled value="">{{ getPlaceholderText(param) }}</option>
                      <!-- Dynamic options from data -->
                      <option v-for="optionValue in this[param.optionsKey]" :key="optionValue" :value="optionValue">
                        {{ optionValue }}
                      </option>
                    </select>
                    <!-- Add a message if options failed to load -->
                    <p
                      v-if="param.label === 'Query Name' && param.type === 'select' && !isLoadingQueryNames && (!queryNames || queryNames.length === 0)">
                      Could not load query list.
                    </p>
                    <p v-if="param.type === 'select' && (param.label === 'Version' || param.label === 'Version (Optional)') &&
                      currentParams.find(p => p.label === 'Qualified Query Name' && p.type === 'select')?.value &&
                      !isLoadingQueryNames &&
                      (!versionOptions || versionOptions.length === 0)">
                      Could not load query versions.
                    </p>

                  </div>


                  <div v-if="aqltextarea2" class="form-textarea2">
                    <label for="aql">Stored AQL Query:</label>
                    <textarea id="aql" v-model="aql" rows="6" cols="80" readonly class="big-textarea"
                      style="font-size: 18px;"></textarea>
                  </div>




                  <div v-for="(param, index) in currentParams.filter(p => p.type !== 'select')" :key="index"
                    class="form-group">
                    <label>{{ param.label }}:</label>


                    <input v-model="param.value" :type="param.type" :placeholder="param.placeholder" />


                  </div>



                  <div v-for="(radioparam, radioIndex) in currentRadioParams" :key="radioIndex"
                    class="form-check-group">
                    <label>{{ radioparam.label }}:</label>
                    <div v-for="(option, optionIndex) in radioparam.options" :key="optionIndex" class="form-check">
                      <input :id="`param-${radioIndex}-option-${optionIndex}`" type="radio"
                        :name="`param-${radioIndex}`" :value="option" v-model="radioparam.selected"
                        class="form-check-input" />
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

                </div>


                <div v-else-if="filteredMethods[selectedMethod].label === 'Run Query'" class="form-group">
                  <div class="form-group-sidebyside">
                    <div class="left-side">
                      <label>Stored Queries</label>
                      <div v-for="(param, index) in currentParams.filter(p => p.type === 'select')" :key="index"
                        class="form-group">
                        <label>{{ param.label }}:</label>
                        <select v-model="param.value" class="form-select">

                          <!-- Default disabled option -->
                          <option disabled value="">{{ getPlaceholderText(param) }}</option>
                          <!-- Dynamic options from data -->
                          <option v-for="optionValue in this[param.optionsKey]" :key="optionValue" :value="optionValue">
                            {{ optionValue }}
                          </option>
                        </select>
                        <!-- Add a message if options failed to load -->
                        <p
                          v-if="param.label === 'Query Name' && param.type === 'select' && !isLoadingQueryNames && (!queryNames || queryNames.length === 0)">
                          Could not load query list.
                        </p>
                        <p v-if="param.type === 'select' && (param.label === 'Version' || param.label === 'Version (Optional)') &&
                          currentParams.find(p => p.label === 'Qualified Query Name' && p.type === 'select')?.value &&
                          !isLoadingQueryNames &&
                          (!versionOptions || versionOptions.length === 0)">
                          Could not load query versions.
                        </p>

                      </div>
                    </div>


                    <div class="right-side">
                      <label class="preset-label">Pre-set queries:</label>
                      <div v-for="choice in Object.keys(radioChoices)" :key="choice" class="radio-item">
                        <input type="radio" v-model="selectedRadio" :value="choice" class="radio-input"
                          :id="'radio-' + choice" />
                        <label :for="'radio-' + choice" class="radio-label">{{ choice }}</label>

                      </div>
                    </div>
                  </div>


                  <div class="aqltext">
                    <label for="aql">AQL Query:</label>
                    <textarea id="aql" v-model="aql" rows="6" cols="80" class="big-textarea"
                      style="font-size: 18px;"></textarea>
                  </div>


                  <div v-for="(param, index) in currentParams" :key="index" class="form-group">
                    <div v-if="param.type !== 'select'">
                      <label>{{ param.label }}:</label>


                      <input v-if="param.type !== 'select'" v-model="param.value" :type="param.type"
                        :placeholder="param.placeholder" />

                    </div>

                  </div>



                  <div v-for="(radioparam, radioIndex) in currentRadioParams" :key="radioIndex"
                    class="form-check-group">
                    <label>{{ radioparam.label }}:</label>
                    <div v-for="(option, optionIndex) in radioparam.options" :key="optionIndex" class="form-check">
                      <input :id="`param-${radioIndex}-option-${optionIndex}`" type="radio"
                        :name="`param-${radioIndex}`" :value="option" v-model="radioparam.selected"
                        class="form-check-input" />
                      <label :for="`param-${radioIndex}-option-${optionIndex}`" class="form-check-label">{{ option
                      }}</label>
                    </div>
                  </div>


                  <div class="action-group">
                    <div v-for="(action, index) in methodActions" :key="index" class="action-button">
                      <!-- <button type="submit">{{ action.label }}</button> -->
                      <button @click="executeAction(action.action)">{{ action.label }}</button>
                    </div>
                  </div>
                </div>



                <div v-else class="form-group">



                  <div v-if="aqltextarea" class="form-textarea">
                    <label for="aql">AQL Query:</label>
                    <textarea id="aql" v-model="aql" rows="6" cols="80" class="big-textarea"
                      style="font-size: 18px;"></textarea>
                  </div>
                  <div v-if="aqltextarea2" class="form-textarea2">
                    <label for="aql">Stored AQL Query:</label>
                    <textarea id="aql" v-model="aql" rows="6" cols="80" readonly class="big-textarea"
                      style="font-size: 18px;"></textarea>
                  </div>

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
                      v-if="param.label === 'Query Name' && param.type === 'select' && !isLoadingQueryNames && (!queryNames || queryNames.length === 0)">
                      Could not load query list.
                    </p>
                    <p v-if="param.type === 'select' && (param.label === 'Version' || param.label === 'Version (Optional)') &&
                      currentParams.find(p => p.label === 'Qualified Query Name' && p.type === 'select')?.value &&
                      !isLoadingQueryNames &&
                      (!versionOptions || versionOptions.length === 0)">
                      Could not load query versions.
                    </p>

                  </div>





                  <div v-for="(radioparam, radioIndex) in currentRadioParams" :key="radioIndex"
                    class="form-check-group">
                    <label>{{ radioparam.label }}:</label>
                    <div v-for="(option, optionIndex) in radioparam.options" :key="optionIndex" class="form-check">
                      <input :id="`param-${radioIndex}-option-${optionIndex}`" type="radio"
                        :name="`param-${radioIndex}`" :value="option" v-model="radioparam.selected"
                        class="form-check-input" />
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
  name: 'AQLPage',
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
      radioChoices: { 'None': '', 'All EHRs: EHR id': 'SELECT e/ehr_id/value \nFROM EHR e', 'All Compositions: EHR id, Composition id': 'SELECT e/ehr_id/value,\nc/uid/value \nFROM EHR e \nCONTAINS COMPOSITION c', 'All Compositions: EHR id, Composition id, Template id': 'SELECT e/ehr_id/value,\nc/uid/value,\nc/archetype_details/template_id/value \nFROM EHR e \nCONTAINS COMPOSITION c' },
      selectedRadio: 'None',
      queriesinfo: [],
      aqltextarea: false,
      aqltextarea2: false,
      aql: '',
      resultsName: 'results.json',
      methodType: "All",
      onwhat: "query",
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
      selectedFile: null,
      queryNames: [],
      versionOptions: [],
      templates: [],
      isLoadingQueryNames: false,
      isLoadingQueryVersions: false,
      nametoversions: {},
      // selectedMethodIndex: null,
      index2: null,
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
    this.currentMethods = this.getMethodsForQuery();
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
    selectedRadio(newVal) {
      if (newVal !== 'None') {
        this.aql = this.radioChoices[newVal];
      } else {
        this.aql = '';
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
        { file: false, label: '' },
        { file: false, label: '' },
        { file: false, label: '' },
      ];
      return needFile[index] || { file: false, label: '' };
    },
    selectMethod(index) {
      this.aql = '';
      this.resultsOK = false;
      this.resultsName = 'results.json';
      this.currentMethods = this.getMethodsForQuery();
      this.index2 = this.getIndexByTypeWhat(this.currentMethods, index, this.methodType, this.onwhat)
      console.log("index", index)
      console.log("index2", this.index2)
      this.selectedMethod = index;
      // this.selectedMethodIndex = index;
      this.methodActions = this.getActionsForMethod(this.index2);
      this.currentParams = this.getParamsForMethod(this.index2);
      this.currentRadioParams = this.getRadioParamsForMethod(this.index2);
      this.needFile = this.getNeedFile(this.index2);
      this.currentFile = this.needFile.file;
      this.labelFile = this.needFile.label;
      console.log('currentfile', this.currentFile);
      console.log('labelFile', this.labelFile);
      this.results = null; // Reset results
      if (this.index2 === 1 || index === 2 || this.index2 >= 4) {
        this.fetchQueryNames();
      }
      if (this.index2 === 3 || this.index2 === 5) {
        this.aqltextarea = true;
        this.aqltextarea2 = false;
      } else if (this.index2 === 4) {
        this.aqltextarea = false;
        this.aqltextarea2 = true;
      } else {
        this.aqltextarea = false;
        this.aqltextarea2 = false;
      }
    },
    getMethodsForQuery() {
      const methods = {
        'methods': [
          { label: 'List Queries', type: ['Get'], what: ['query'] },//1
          { label: 'Retrieve Query Versions by Name', type: ['Get'], what: ['query'] },//2
          { label: 'Retrieve Query by Name and Version', type: ['Get'], what: ['query'] },//3
          { label: 'Insert Query', type: ['Put'], what: ['query'] },//4
          { label: 'Run Stored Query', type: ['Get', 'Post'], what: ['query'] },//5
          { label: 'Run Query', type: ['Get', 'Post'], what: ['query'] },//6
        ]
      };
      return methods['methods'] || [];
    },

    // Get actions associated with the selected method
    getActionsForMethod(index) {
      const actions = [
        [{ label: 'Submit', action: 'submit_query_list' }],//1
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_query_getv' }],//2
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_query_get' }],//3
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_query_put' }],//4
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_query_run_stored' }],//5
        [{ label: 'Clear Input', action: 'clear_all' }, { label: 'Submit', action: 'submit_query_run' }],//6
      ];
      return actions[index] || [];
    },
    getRadioParamsForMethod(index) {
      const radioParams = [
        [],//1
        [],//2
        [],//3
        [],//4
        [{ label: 'Query Method', selected: "Get", options: ['Get', 'Post'] }],//4
        [{ label: 'Query Method', selected: "Get", options: ['Get', 'Post'] }],//5
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
            label: "Qualified Query Name",
            value: "",
            type: "select",
            optionsKey: 'queryNames',
            placeholder: "Select Query Name",
          },],
        [//3]
          {
            label: "Qualified Query Name",
            value: "",
            type: "select",
            optionsKey: 'queryNames',
            placeholder: "Select Query Name",
          }, { label: 'Version', value: '', optionsKey: 'versionOptions', type: 'select', placeholder: "Select Version" }
        ],
        [//4
          { label: 'Qualified Query Name', value: '', type: 'text', placeholder: "org.ehrbase.local::query1" }, { label: 'Version (Optional)', value: '', type: 'text', placeholder: "1.0.0" }],
        [//5      
          {
            label: "Qualified Query Name",
            value: "",
            type: "select",
            optionsKey: 'queryNames',
            placeholder: "Select Query Name",
          },
          { label: 'Version', value: '', type: 'select', optionsKey: 'versionOptions', placeholder: "Select version" },
          { label: 'Fetch (Optional)', value: '', type: 'text', placeholder: "10" },
          { label: 'Offset (Optional)', value: '', type: 'text', placeholder: "2" },
          { label: 'Query Parameters (Optional)', value: '', type: 'text', placeholder: "param1=value1,param2=value2" },
        ],
        [//6
          {
            label: "Qualified Query Name",
            value: "",
            type: "select",
            optionsKey: 'queryNames',
            placeholder: "Select Query Name",
          },
          { label: 'Version', value: '', type: 'select', optionsKey: 'versionOptions', placeholder: "Select version" },
          { label: 'Fetch (Optional)', value: '', type: 'text', placeholder: "10" },
          { label: 'Offset (Optional)', value: '', type: 'text', placeholder: "2" },
          { label: 'Query Parameters (Optional)', value: '', type: 'text', placeholder: "param1=value1,param2=value2" },
        ],
      ];
      if ((index === 1 || index >= 4) && params[index] && params[index][0]) {
        params[index][0].value = '';
      }
      return params[index] || [];
    },

    // Handle action button click
    async executeAction(action) {
      this.results = null
      if (action == 'submit_query_list') //get query list
      {
        try {
          const queryfetch = await this.fetchQueryNames();
          console.log('queryfetch', queryfetch);
          this.results = JSON.stringify(queryfetch.versions, null, 2);
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

      } else if (action == 'submit_query_getv') //get query versions by name 
      {
        this.resultsOK = false;
        const queryname = this.currentParams.find(p => p.label === 'Qualified Query Name')?.value;
        console.log('queryname', queryname);
        if (!queryname) {
          this.results = 'Qualified Query Name is required';
          return;
        }
        try {
          const queryResults = await this.getqueryversions(queryname);
          console.log('results', queryResults);
          this.resultsOK = true;
          this.resultsName = 'results.json';
          this.results = JSON.stringify(queryResults, null, 2);
        }
        catch (error) {
          console.error("Error in executeAction:", error);
          this.results = `Error: ${error.message}`;
        }
      } else if (action == 'submit_query_get') //get query by name and version 
      {
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
          const queryResults = await this.getquerybynameandversion(queryname, queryversion);
          console.log('results', queryResults);
          this.resultsOK = true;
          this.resultsName = 'results.json';
          this.results = JSON.stringify(queryResults, null, 2);
        }
        catch (error) {
          console.error("Error in executeAction:", error);
          this.results = `Error: ${error.message}`;
        }
      }
      else if (action == 'submit_query_put') //post query (though it's a put call)
      {
        this.resultsOK = false;
        if (this.aql === '' || !this.aql.toLowerCase().includes('select') || !this.aql.toLowerCase().includes('from')) {
          this.results = 'An AQL Query is required';
          return;
        }
        const queryname = this.currentParams.find(p => p.label === 'Qualified Query Name')?.value;
        console.log('queryname', queryname);
        if (!queryname) {
          this.results = 'A Qualified Query Name is required';
          return;
        }
        const queryversion = this.currentParams.find(p => p.label === 'Version (Optional)')?.value;
        console.log('queryversion', queryversion);
        if (!queryversion) {
          this.queryversion = '';
        } else {
          this.queryversion = queryversion;
        }
        console.log('queryversion', this.queryversion);
        try {
          const queryResults = await this.putquery(this.aql, queryname, this.queryversion);
          console.log('results', queryResults);
          this.resultsOK = true;
          this.resultsName = 'results.json';
          this.results = JSON.stringify(queryResults, null, 2);
        }
        catch (error) {
          console.error("Error in executeAction:", error);
          this.results = `Error: ${error.message}`;
        }
      }










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
    //for queries list and get
    async fetchQueryNames() {
      try {
        console.log('fetchQueryNames called');
        this.isLoadingQueryNames = true;
        this.queryNames = [];
        const response = await axios.get('http://127.0.0.1:5000/query/query',
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
    async getqueryversions(queryname) {
      try {
        console.log('getqueryversions called');
        this.isLoading = true;
        this.resultsOK = false;
        const response = await axios.get('http://127.0.0.1:5000/query/',
          {
            headers: { 'Authorization': `Bearer ${localStorage.getItem("authToken")}` },
            params: {
              queryname: queryname,
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
        return response.data.query;

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
      finally {
        this.isLoading = false;
      }
    },
    async getquerybynameandversion(queryname, queryversion) {
      try {
        console.log('getquerybynameandversion called');
        this.isLoading = true;
        this.resultsOK = false;
        const response = await axios.get('http://127.0.0.1:5000/query/',
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
        this.resultsOK = true;
        return response.data.query;

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
      finally {
        this.isLoading = false;
      }
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

        const response = await axios.get('http://127.0.0.1:5000/query/',
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
    async putquery(q, queryname, queryversion) {
      console.log('inside putquery');
      console.log(localStorage.getItem("authToken"))
      this.isLoading = true;
      this.resultsOK = false;
      // await this.sleep(5000);
      console.log('q', q);
      console.log('queryname', queryname);
      console.log('queryversion', queryversion);
      try {
        const response = await axios.put(`http://127.0.0.1:5000/query/`,
          {},
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem("authToken")}`
            },
            params: {
              "q": q,
              "queryname": queryname,
              "version": queryversion,
              "qtype": "AQL"
            },
            timeout: 2000000,
          },
        );
        this.isLoading = false;
        return response.data.query;
      }
      catch (error) {
        console.error("Error in putquery:", error);
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
  margin-bottom: 20px;
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
  /* padding: 0;
  margin: 0;
  border: none; */
  width: 100%;
  overflow-x: hidden;
  overflow-y: visible;
}



/* .results-content {
  display: inline-block;
  min-width: 100%;
 
} */



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
  background: #bad489;
  text-align: center;
}

.file-input {
  padding: 0px;
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

.form-textarea {
  margin-top: 10px;
  margin-bottom: 10px;
}

/* 
.big-textarea {
  font-size: 30px;
  font-family: monospace;
} */

.form-aqltext {
  margin-top: 0px;
  margin-bottom: 10px;
}

.form-aqltext textarea {
  margin-top: 0px;
}

.form-group-sidebyside {
  display: flex;
  gap: 100px;
  align-items: flex-start;
  margin-bottom: 0px;
}

.left-side {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.right-side {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0px;
}

.preset-label {
  /* font-weight: bold; */
  margin-bottom: 20px;
}

.radio-item {
  display: grid;
  grid-template-columns: 15px 1fr;
  align-items: start;
  column-gap: 10px;
  margin-bottom: 0px;
  margin-top: 0px;
}

.radio-input {
  flex-shrink: 0;
  width: 16px;
  height: 16px;
}

.radio-label {
  white-space: normal;
  line-height: 1.1;
}

/* 
* {
  outline: 1px dashed rgba(243, 5, 5, 0.2);
} */
</style>
