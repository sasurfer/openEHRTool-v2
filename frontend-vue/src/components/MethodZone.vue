<template>
  <div class="app-container">
    <!-- Left Sidebar (Menu with Icons) -->
    <div class="sidebar">
      <ul>
        <!-- Home Icon -->
        <!-- <li @click="goHome">
          <img :src="homeIcon" alt="Home" /> -->

        <!-- </li> -->
        <li v-for="(item, index) in menuItems" :key="index" @click="selectIcon(index)">
          <i :class="item.icon"></i>
          <img v-if="item.iconType === 'svg'" :src="item.icon" alt="icon" />
          <!-- <span>{{ item.label }}</span> -->
        </li>
      </ul>
    </div>

    <!-- Center Column (Method Selection Zone) -->
    <div class="method-selection-zone">
      <!-- Only show methods if it's not the Home page -->
      <div v-if="!isHomePage">
        <div v-for="(method, index) in currentMethods" :key="index" class="method-item">
          <button @click="selectMethod(index)">{{ method.label }}</button>
        </div>
      </div>
    </div>

    <!-- Main Content (Right) -->
    <div class="main-content">
      <!-- Home Page Content -->
      <div v-if="isHomePage">
        <h2>This is a title</h2>
        <p>Welcome to the Home page. No methods available here, only a welcome message.</p>
      </div>

      <!-- Method Actions Section -->
      <div v-if="!isHomePage && selectedMethod !== null" class="actions">
        <h2>{{ currentMethods[selectedMethod].label }}</h2>

        <!-- Method-specific Actions -->
        <div v-for="(action, index) in methodActions" :key="index" class="action-button">
          <button @click="executeAction(index)">{{ action.label }}</button>
        </div>
      </div>

      <!-- Parameter Form Zone -->
      <div v-if="!isHomePage" class="parameter-form">
        <h3>Input Parameters</h3>
        <form @submit.prevent="submitForm">
          <div v-for="(param, index) in currentParams" :key="index" class="form-group">
            <label>{{ param.label }}:</label>
            <input v-model="param.value" :type="param.type" placeholder="Enter value" />
          </div>

          <div v-if="currentFile" class="file-input">
            <label>Upload File:</label>
            <input type="file" @change="handleFileUpload" />
          </div>
        </form>
      </div>

      <!-- Results Section -->
      <div v-if="!isHomePage" class="results-section">
        <h3>Results</h3>
        <div class="results-content">
          <pre>{{ results }}</pre>
        </div>
      </div>

      <!-- Separator Line between Top and Results -->
      <div class="separator" v-if="!isHomePage"></div>
    </div>

    <!-- Far Right Icons (For Showing Overlay Windows) -->
    <div class="far-right-icons">
      <ul>
        <li v-for="(icon, index) in rightIcons" :key="index" @click="toggleOverlay(index)">
          <i :class="icon.icon"></i>
        </li>
      </ul>

      <!-- Overlay Zone for Triangle and Star -->
      <div v-if="overlayVisible" class="overlay">
        <div class="overlay-content">
          <h3>{{ overlayTitle }}</h3>
          <ul>
            <li v-for="(value, index) in overlayValues" :key="index">{{ value }}</li>
          </ul>
          <button @click="closeOverlay">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import loginicon from "@/assets/login-icon.svg";
import homeicon from "@/assets/home-icon.svg";
import ehricon from "@/assets/ehr-icon.svg";
import templateicon from "@/assets/template-icon.svg";
import compositionicon from "@/assets/composition-icon.svg";
import aqlicon from "@/assets/aql-icon.svg";
import formicon from "@/assets/form-icon.svg";
import contributionicon from "@/assets/contribution-icon.svg";
import adminicon from "@/assets/admin-icon.svg";
import logicon from "@/assets/log-icon.svg";
export default {
  data() {
    return {
      // Icons on the Left Sidebar
      // Path for the Home icon
      // homeIcon: require('@/assets/home-icon.png'),
      menuItems: [
        { label: 'login', iconType: "svg", icon: loginincon },
        { label: 'nothing', iconType: "None", icon: 'fa fa-caret-square-up' },
        { label: 'nothing2', iconType: "None", icon: 'fa fa-caret-square-up' },
        { label: 'Home', iconType: "svg", icon: homeicon },
        { label: 'EHR', iconType: "svg", icon: ehricon },
        { label: 'Template', iconType: "svg", icon: templateicon },
        { label: 'Composition', iconType: "svg", icon: compositionicon },
        { label: 'AQL', iconType: "svg", icon: aqlicon },
        { label: 'Form', iconType: "svg", icon: formicon },
        { label: 'Contribution', iconType: "svg", icon: contributionicon },
        { label: 'Admin', iconType: "svg", icon: adminicon },
        { label: 'LOG', iconType: "svg", icon: logicon },
      ],

      // Icons on the Far Right
      rightIcons: [
        { icon: 'fa fa-caret-square-up', data: ['10-15-24', '10-20-32'] },
        { icon: 'fa fa-star', data: ['20-25-35', '20-30-40'] },
      ],

      selectedIcon: null,
      selectedMethod: null,
      methodActions: [],
      currentMethods: [],
      currentParams: [],
      currentFile: false,
      results: null,
      overlayVisible: false,
      overlayTitle: '',
      overlayValues: [],
      isHomePage: true, // Flag to determine if we're on the Home page
    };
  },
  methods: {
    // Select the icon from the left sidebar
    selectIcon(index) {
      if (index === 3) {
        this.isHomePage = true; // Home is selected
        this.selectedIcon = null; // Reset selected icon
        this.results = null; // Reset results
        this.selectedMethod = null; // Reset selected method
        this.currentParams = []; // Clear parameters
        this.methodActions = []; // Clear actions
      } else if (index == 0) { //logout
        this.isHomePage = false;
      } else {
        this.isHomePage = false; // Other icons
        this.selectedIcon = index;
        this.currentMethods = this.getMethodsForIcon(index); // Load methods for the selected icon
        this.selectedMethod = null; // Reset selected method
        this.results = null; // Reset results
      }
    },

    // Get methods related to the selected icon
    getMethodsForIcon(index) {
      const methods = {
        5: [
          { label: 'Method 1' },
          { label: 'Method 2' },
          { label: 'Method 3' },
        ], // Circle Methods
        6: [
          { label: 'Method 4' },
          { label: 'Method 5' },
        ], // Square Methods
      };
      return methods[index] || [];
    },

    // Select the method from the list of methods
    selectMethod(index) {
      this.selectedMethod = index;
      this.methodActions = this.getActionsForMethod(index);
      this.currentParams = this.getParamsForMethod(index);
      this.results = null; // Reset results
    },

    // Get actions associated with the selected method
    getActionsForMethod(index) {
      const actions = [
        [{ label: 'Action 1' }, { label: 'Action 2' }],
        [{ label: 'Action A' }, { label: 'Action B' }],
        [{ label: 'Action X' }, { label: 'Action Y' }],
      ];
      return actions[index] || [];
    },

    // Get input parameters for the selected method
    getParamsForMethod(index) {
      const params = [
        [
          { label: 'Parameter 1', value: '', type: 'text' },
          { label: 'Parameter 2', value: '', type: 'number' },
        ],
        [
          { label: 'Param A', value: '', type: 'text' },
          { label: 'Param B', value: '', type: 'number' },
        ],
        [
          { label: 'Param X', value: '', type: 'text' },
          { label: 'Param Y', value: '', type: 'number' },
        ],
      ];
      return params[index] || [];
    },

    // Handle action button click
    executeAction(index) {
      this.results = `Result for ${this.methodActions[index].label} will appear here.`;
    },

    // Submit form with parameter values
    submitForm() {
      this.results = `Form submitted with values: ${JSON.stringify(this.currentParams)}`;
    },

    // Handle file upload
    handleFileUpload(event) {
      const file = event.target.files[0];
      console.log('File selected:', file);
      this.currentFile = file.name;
    },

    // Toggle overlay visibility (for triangle/star)
    toggleOverlay(index) {
      if (this.overlayVisible) {
        this.overlayVisible = false;
      } else {
        this.overlayTitle = `Overlay Info ${index + 1}`;
        this.overlayValues = this.rightIcons[index].data;
        this.overlayVisible = true;
      }
    },

    // Close the overlay
    closeOverlay() {
      this.overlayVisible = false;
    },
  },
};
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 40px;
  background: #333;
  color: white;
  padding: 10px;
  height: 100vh;
  /* Ensures the sidebar spans the full height of the screen */
  display: flex;
  flex-direction: column;
}

.sidebar ul {
  list-style-type: none;
  padding: 0;
}

.sidebar li {
  cursor: pointer;
  margin-bottom: 0px;
}

.sidebar i {
  margin-right: 10px;
}

.method-selection-zone {
  width: 150px;
  background: #f4f4f4;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.method-item {
  margin-bottom: 15px;
}

.method-item button {
  width: 100%;
}

.main-content {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.method-actions {
  margin-bottom: 0px;
}

.parameter-form {
  background-color: #f0f0f0;
  padding: 20px;
  margin-bottom: 20px;
  flex: 2;
  border-radius: 8px;
}

.parameter-form .form-group {
  margin-bottom: 10px;
}

.parameter-form label {
  display: block;
  margin-bottom: 5px;
}

.results-section {
  flex: 1;
  background-color: #fff;
  padding: 20px;
}

.results-section pre {
  font-size: 14px;
}

.separator {
  height: 1px;
  background-color: #ccc;
  margin: 20px 0;
}

.far-right-icons {
  width: 50px;
  background: #333;
  color: white;
  padding: 20px;
}

.far-right-icons ul {
  list-style-type: none;
  padding: 0;
}

.far-right-icons li {
  margin-bottom: 30px;
  cursor: pointer;
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
}

.overlay-content {
  background: #444;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.overlay-content button {
  margin-top: 20px;
}
</style>
