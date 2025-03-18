<template>
  <div id="app">
    <!-- You can have a global navbar, footer, or other common layout elements here -->
    <Sidebar @open-user-info="openUserInfo" />
    <rsidebar  @open-ehr-info="openEHRInfo" @open-template-info="openTemplateInfo"
      @open-composition-info="openCompositionInfo" @open-aql-info="openAQLInfo" >
  </rsidebar>
    <UserInfoModal v-if="isUserInfoVisible" :isVisible="isUserInfoVisible" :user="user" @close-modal="closeModal"
      @logout="logout" />
    <div class="main-content">
      <!-- Your main content goes here -->
      <h1>Dashboard</h1>
      <div v-if="isLoadingDashboard" class="flex justify-center items-center dashboard-spinner">
        <RotateSquare2  :size="'100px'" :background="'#ff5733'"></RotateSquare2>
      </div>
      <div class='gridt grid-cols-6 gap-6 p-6'>
        <!-- Info Panel -->
        <MyCardComponent class='card3 col-span-6 bg-green-100 p-6'>
          <!-- <h2 class='text-green-800 font-semibold'>Info</h2> -->
          <CardContent>
            <div class="grid-container">
              <div v-for="(value, key) in info" :key="key" class="grid-item">
                <div class="key">{{ key }}</div>
                <div class="value">{{ value }}</div>
              </div>
            </div>
          </CardContent>
        </MyCardComponent>
      </div>
      <div class='grid grid-cols-1 gap-4 p-4'>
        <!-- Metrics Cards -->
        <MyCardComponent class='p-2'>
          <CardContent>
            <h2 class='text-1-large'>EHRs in Use/EHRS</h2>
            <p class='text-normal font-bold'>{{ metrics.ehrsInUse }}/{{ metrics.ehrsCount }}</p>
          </CardContent>
        </MyCardComponent>
        <MyCardComponent class='p-2'>
          <CardContent>
            <h2 class='text-2-large'>Compositions</h2>
            <p class='text-2xl font-bold'>{{ metrics.compositionsCount }}</p>
          </CardContent>
        </MyCardComponent>
        <MyCardComponent class='p-2'>
          <CardContent>
            <h2 class='text-3-large'>Templates in Use/Templates</h2>
            <p class='text-2xl font-bold'>{{ metrics.templatesInUse }}/{{ metrics.templatesCount }}</p>
          </CardContent>
        </MyCardComponent>
        <MyCardComponent class='p-2'>
          <CardContent>
            <h2 class='text-4-large'>AQL Queries Stored</h2>
            <p class='text-2xl font-bold'>{{ metrics.aqlsCount }}</p>
          </CardContent>
        </MyCardComponent>
      </div>
      <div class='grid2 grid-cols-4 gap-4 p-4'>
        <!-- BarChart -->
        <MyCardComponent class='col-span-2 p-2 card2'>
          <CardContent>
            <h2 class='text-bar font-semibold'>EHR frequency per #Compositions</h2>
            <MyBarChart :data="barChartData" :key="barChartKey" />
          </CardContent>
        </MyCardComponent>

        <!-- PieChart -->
        <MyCardComponent class='col-span-2 p-2 card2'>
          <CardContent>
            <h2 class='text-pie font-semibold'>Compositions per Template</h2>
            <MyPieChart :data="pieChartData" :key="pieChartKey" />
          </CardContent>
        </MyCardComponent>
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
import MyCardComponent from "@/components/ui/MyCardComponent";
import CardContent from "@/components/ui/CardContent";
import MyBarChart from '@/components/MyBarChart.vue'; // Import the chart compone
import MyPieChart from '@/components/MyPieChart.vue'; // Import the PieChart component
import  RotateSquare2  from '@/components/ui/RotateSquare2.vue'; // Import the RotateSquare2 component


export default defineComponent({
  name: 'HomePage',
  components: {
    Sidebar,
    UserInfoModal,
    rsidebar,
    EHRInfoModal,
    TemplateInfoModal,
    CompositionInfoModal,
    AQLInfoModal,
    MyBarChart,
    MyPieChart,
    MyCardComponent,
    CardContent,
    RotateSquare2,
  },
  data() {
    return {
      //for user info modal
      isLoadingDashboard: false,
      isLoadingEHR: false,
      isLoadingTemplate: false,
      isLoadingComposition: false,
      isLoadingAQL: false,
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
      metrics: {
        ehrsCount: "",
        ehrInUse: "",
        compositionsCount: "",
        templatesCount: "",
        templatesInUse: "",
        aqlsCount: "",
      },
      barChartData: {
        labels: [],
        datasets: [
          {
            type: 'bar',
            label: "EHR frequency per #Compositions",
            data: [],
            backgroundColor: "rgba(54, 162, 235, 0.2)",
            borderColor: "rgba(54, 162, 235, 1)",
            borderWidth: 1,
            hoverBackgroundColor: "rgba(54, 162, 235, 0.4)",
            hoverBorderColor: "rgba(54, 162, 235, 1)",
            hoverBorderWidth: 2,
          },
        ],
      },
      pieChartData: {
        labels: [],
        datasets: [
          {
            type: 'pie', // Add this line to specify the chart type
            data: [],
            label: "Compositions per Template",
            backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"],
            hoverBackgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"],
            hoverBorderColor: ["#FF6384", "#36A2EB", "#FFCE56"],
            hoverBorderWidth: 0,
            borderWidth: 1,
          },
        ],
      },
      info: {},
      barChartKey: 0,
      pieChartKey: 0,
    };
  },
  mounted() {
    // Fetch data when the component is first mounted
    this.fetchDashboardData();
    this.fetchEHRdata();
    this.fetchTemplateData();
    this.fetchCompositionData();
    this.fetchAQLData();
  },
  watch: {
    '$route'() {
      // Fetch data when the route changes
      this.fetchDashboardData();
      this.fetchEHRdata();
      this.fetchTemplateData();
      this.fetchCompositionData();
      this.fetchAQLData();
    },
  },
  methods: {
    async fetchDashboardData() {
      try {
        this.isLoadingDashboard = true; 
        // Replace with your Flask API endpoint
        const response = await axios.get('http://127.0.0.1:5000/dashboard',
          { method: 'GET', headers: { 'Authorization': `Bearer ${localStorage.getItem("authToken")}` }, },
          { timeout: 2000000 }); // Adjust the URL to your Flask API
        if (response.status === 401) {
          console.error("Unauthorized access. Please login again.");
          this.logout();
          return
        }
        if (response.status != 200) {
          console.error("Error fetching data:", response);
          return;
        }
        // Assuming the backend returns data in this structure
        console.log(response)
        this.metrics = response.data.dashboard_data.metrics;
        console.log('this.metrics', this.metrics);
        const barData = response.data.dashboard_data.barData;
        const pieData = response.data.dashboard_data.pieData;
        if (Object.keys(barData).length > 0) {
          this.barChartData.labels = Object.keys(barData);
          this.barChartData.datasets[0].data = Object.values(barData);
          this.barChartKey += 1;
          console.log('this.barChartData', this.barChartData);
        }
        if (Object.keys(pieData).length > 0) {
          this.pieChartData.labels = Object.keys(pieData);
          this.pieChartData.datasets[0].data = Object.values(pieData);
          this.pieChartKey += 1;
          console.log('this.pieChartData', this.pieChartData);
        }
        this.info = Object(response.data.dashboard_data.info);
        console.log('this.info', this.info);
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
        this.isLoadingDashboard = false;
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
    //for ehr info modal
    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    },
    async fetchEHRdata() {
      try {
        this.isLoadingEHR = true;
        // await this.sleep(5000);
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
      this.isLoadingEHR = false;
    },
    closeEHRInfo() {
      this.isEHRInfoVisible = false;
    },
    //for template info modal
    async fetchTemplateData() {
      try {
        this.isLoadingTemplate = true;
        // await this.sleep(20000);
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
        // await this.sleep(20000);
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
      }  
      finally {
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
        // await this.sleep(20000);
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
  },
});
</script>


<style scoped>
#app {
  display: flex;
  margin-top: 0px;
}

/* .sidebar {
  width: 250px;
} */
.grid-container {
  display: grid;
  /*grid-template-columns: repeat(6, 1fr);*/
  /* Create 6 columns */
  grid-template-columns: 1fr 1fr 2fr 1fr 2fr 4fr;
  gap: 20px;
  text-align: center;
  overflow: visible
}

.key {
  font-weight: bold;
  margin-bottom: 8px;
}

.value {
  margin-top: 8px;
}

.grid-item {
  display: flex;
  flex-direction: column;
  align-items: center;
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
  /* flex-grow: 1; */
  padding-top: 0px;
  padding-left: 60px;
  padding-right: 60px;
  margin-top: 0px;
  margin-left: 20px;
  margin-right: 20px;
}

.card {
  height: 100px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: top;
  padding: 5px;
  margin: 5px;
  /* background-color: #f8f8f8;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 10px;
  margin: 1rem; */
}

.card2 {
  height: 350px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: bottom;
  padding: 5px;
  margin: 5px;
  /* background-color: #f8f8f8;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 10px;
  margin: 1rem; */
}

.card3 {
  height: 130px;
  /* background-color: #b7ddd2; */
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: top;
  padding: 5px;
  margin: 5px;
  /* background-color: #f8f8f8;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 10px;
  margin: 1rem; */
}
</style>


<style scoped>
/* .dashboard-container {
  display: flex;
  height: 100vh;
} */
/* 
.sidebar {
  width: 250px;
  background-color: #f8f8f8;
  padding: 1rem;
  border-right: 1px solid #ddd;
} */
/* 
.sidebar ul {
  list-style: none;
  padding: 0;
}

.sidebar li {
  padding: 10px;
  cursor: pointer;
}

.sidebar li:hover {
  background-color: #f0f0f0;
} */

/* .content {
  flex-grow: 1;
  padding: 2rem;
} */

/* .main-content {
  display: flex;
  flex-direction: column;
  padding: 20px;
} */
.grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  /* 2 equal-width columns */
  gap: 10px;
  /* Adjust the gap between cards */
  overflow: visible
}

.grid>* {
  background-color: #b4b3b3;
  /* Add background to cards */
  border-radius: 20px;
  /* Rounded corners for the cards */
  box-shadow: 0 20px 20px rgba(0, 0, 0, 0.1);
  /* Optional shadow for better appearance */
}


.text-1-large {
  font-size: 15px;
  /* Adjust the font size */
  color: aqua
}

.text-1-normal {
  font-size: 10px;
  /* Adjust the font size */
  color: aqua
}

.text-2-large {
  font-size: 15px;
  /* Adjust the font size */
  color: rgb(201, 126, 29)
}

.text-2-normal {
  font-size: 10px;
  /* Adjust the font size */
  color: rgb(201, 126, 29)
}

.text-3-large {
  font-size: 15px;
  /* Adjust the font size */
  color: rgb(89, 0, 255)
}

.text-3-normal {
  font-size: 10px;
  /* Adjust the font size */
  color: rgb(89, 0, 255)
}

.text-4-large {
  font-size: 15px;
  /* Adjust the font size */
  color: rgb(235, 27, 27)
}

.text-4-normal {
  /* Dark grey text color */
  font-size: 10px;
  /* Adjust the font size */
  color: rgb(235, 27, 27)
}

.text-bar {
  /* Dark grey text color */
  font-size: 25px;
  /* Adjust the font size */
  color: black;
}

.text-pie {
  /* Dark grey text color */
  font-size: 25px;
  /* Adjust the font size */
  color: black;
}

.grid2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  /* 2 equal-width columns */
  gap: 10px;
  /* Adjust the gap between cards */
  overflow: visible
}

.grid2>* {
  /* background-color: #b4b3b3; */
  /* Add background to cards */
  border-radius: 20px;
  /* Rounded corners for the cards */
  box-shadow: 0 20px 20px rgba(0, 0, 0, 0.1);
  /* Optional shadow for better appearance */
}

gridt {
  display: grid;
  /* grid-template-columns: repeat(4, 1fr); */
  /* grid-template-columns: 1fr 1fr 2fr 1fr 2fr 4fr; */
  /* 2 equal-width columns */
  /* gap: 10px; */
  /* Adjust the gap between cards */
  /* overflow: visible */
}

.gridt>* {
  background-color: #b4b3b3;
  /* Add background to cards */
  border-radius: 20px;
  /* Rounded corners for the cards */
  box-shadow: 0 20px 20px rgba(0, 0, 0, 0.1);
  /* Optional shadow for better appearance */
}

.MyBarChart {
  height: 100%;
  width: 100%;
}

.MyPieChart {
  height: 50%;
  width: 100%;
}

.dashboard-spinner {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
}

.ehrspinner {
  position: fixed;
  top: 5%;
  right: 5%;
  transform: translate(-50%, -50%);
  z-index: 20;
}

</style>
