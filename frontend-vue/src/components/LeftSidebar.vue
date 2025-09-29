<template>
  <div class="app-container">
    <!-- Left Sidebar (Menu with Icons) -->
    <div class="sidebar">
      <ul>
        <div class="top-icons">
          <li v-for="(item, index) in menuItems.slice(0, 1)" :key="index"
            :class="{ active: activeIndex === index, firsticon: index === 0 }" @click="selectIcon(index)">
            <i :class="item.icon"></i>
            <img v-if="item.iconType === 'svg'" :src="item.icon" alt="icon" width="25" height="25" />
            <!-- <img v-if="activeIndex === index" :src="item.icon2" alt="icon" width="25" height="25" />
            <img v-else :src="item.icon2" alt="icon" width="25" height="25" /> -->
          </li>
        </div>

        <div class="icon-spacer"></div>
        <div class="bottom-icons">
          <li v-for="(item, index) in menuItems.slice(1, 10)" :key="index" @click="selectIcon(index + 1)"
            :class="{ active: activeIndex === index + 1 }">
            <i :class="item.icon"></i>
            <img v-if="item.iconType === 'svg'" :src="item.icon" alt="icon" width="25" height="25" />
            <!--<img
       v-if="item.iconType === 'svg'"
      :src="activeIndex === index ? item.icon : item.icon2"
      alt="icon"
      width="25"
      height="25"
    /> -->

            <!-- <img v-if="activeIndex === index + 1" :src="item.icon2" alt="icon" width="25" height="25" />
            <img v-else :src="item.icon" alt="icon" width="25" height="25" /> -->
          </li>
        </div>
      </ul>
    </div>
  </div>
</template>

<script>
import logicon from "@/assets/log-icon.svg";
import logicon_active from "@/assets/log-icon_active.svg";
import adminicon from "@/assets/admin-icon.svg";
import adminicon_active from "@/assets/admin-icon_active.svg";
import contributionicon from "@/assets/contribution-icon.svg";
import contributionicon_active from "@/assets/contribution-icon_active.svg";
import formicon from "@/assets/form-icon.svg";
import formicon_active from "@/assets/form-icon_active.svg";
import aqlicon from "@/assets/aql-icon.svg";
import aqlicon_active from "@/assets/aql-icon_active.svg";
import compositionicon from "@/assets/composition-icon.svg";
import compositionicon_active from "@/assets/composition-icon_active.svg";
import templateicon from "@/assets/template-icon.svg";
import templateicon_active from "@/assets/template-icon_active.svg";
import ehricon from "@/assets/ehr-icon.svg";
import ehricon_active from "@/assets/ehr-icon_active.svg";
import homeicon from "@/assets/home-icon.svg";
import homeicon_active from "@/assets/home-icon_active.svg";
import loginicon from "@/assets/login-icon.svg";
import loginicon_active from "@/assets/login-icon_active.svg";


export default {
  data() {
    return {
      // Icons on the Left Sidebar
      // Path for the Home icon
      // homeIcon: require('@/assets/home-icon.png'),
      // activeIndex: 1, // Default active icon (Home)
      menuItems: [
        { label: 'login', iconType: "svg", icon2: loginicon, icon: loginicon_active },
        { label: 'Home', iconType: "svg", icon2: homeicon_active, icon: homeicon },
        { label: 'EHR', iconType: "svg", icon: ehricon, icon2: ehricon_active },
        { label: 'Template', iconType: "svg", icon: templateicon, icon2: templateicon_active },
        { label: 'Composition', iconType: "svg", icon: compositionicon, icon2: compositionicon_active },
        { label: 'AQL', iconType: "svg", icon: aqlicon, icon2: aqlicon_active },
        { label: 'Form', iconType: "svg", icon: formicon, icon2: formicon_active },
        { label: 'Contribution', iconType: "svg", icon: contributionicon, icon2: contributionicon_active },
        { label: 'Admin', iconType: "svg", icon: adminicon, icon2: adminicon_active },
        { label: 'LOG', iconType: "svg", icon: logicon, icon2: logicon_active },
      ],

      // selectedIcon: null,
      // selectedMethod: null,
      // methodActions: [],
      // currentMethods: [],
      // currentParams: [],
      // currentFile: false,
      // results: null,
      // overlayVisible: false,
      // overlayTitle: '',
      // overlayValues: [],
      // isHomePage: true, // Flag to determine if we're on the Home page
    };
  },
  computed: {
    activeIndex() {
      // Use the current route's metadata to get the sidebar index
      return this.$route.meta.sidebarIndex !== undefined
        ? this.$route.meta.sidebarIndex
        : 1; // Default to 1 (Home) if no metadata is found
    },
  },
  methods: {
    openUserInfo() {
      this.$emit("open-user-info");
    },

    // Select the icon from the left sidebar
    selectIcon(index) {
      // this.setActive(index);
      // console.log("index: ", index);
      // console.log("activeIndex: ", this.activeIndex);

      //   this.$nextTick(() => {
      //   // After Vue updates the DOM, ensure the proper active styles are applied
      // });
      switch (index) {
        case 0:
          // this.isHomePage = false;
          this.openUserInfo(); // Open user info modal
          break;
        case 1:
          // this.isHomePage = true; // Home is selected
          // this.selectedIcon = null; // Reset selected icon
          // this.results = null; // Reset results
          // this.selectedMethod = null; // Reset selected method
          // this.currentParams = []; // Clear parameters
          // this.methodActions = []; // Clear actions
          this.$router.push("/home"); // Redirect to the home page   
          break;
        case 2:
          // this.isHomePage = false;
          this.$router.push("/ehr"); // Redirect to ehr page
          break;
        case 3:
          // this.isHomePage = false;
          this.$router.push("/template"); // Redirect to template page
          break;
        case 4:
          // this.isHomePage = false;
          this.$router.push("/composition"); // Redirect to composition page
          break;
        case 5:
          // this.isHomePage = false;
          this.$router.push("/query"); // Redirect to the aql page
          break;
        case 6:
          // this.isHomePage = false;
          this.$router.push("/form"); // Redirect to the form page
          break;
        case 7:
          // this.isHomePage = false;
          this.$router.push("/contribution"); // Redirect to the contribution page
          break;
        case 8:
          // this.isHomePage = false;
          this.$router.push("/admin"); // Redirect to the admin page
          break;
        case 9:
          // this.isHomePage = false;
          this.$router.push("/log"); // Redirect to the log page
          break;
        default:
          break;
      }

    },
    // setActive(index) {
    //   this.activeIndex = index; // Set the clicked icon as active
    // },
  },
};
</script>


<style></style>
<style scoped>
.app-container {
  display: flex;
  height: 100vh;
}

.sidebar {
  position: fixed;
  /* Fix sidebar position */
  top: 0;
  left: 0;
  width: 40px;
  background: #333;
  /* color: white; */
  padding: 5px;
  height: 100vh;
  /* Ensures the sidebar spans the full height of the screen */
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  /* Pushes top-icons to the top and bottom-icons to the bottom */
  /* padding-top: 20px; */
  overflow-y: auto;
  z-index: 10;
}

.sidebar ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.sidebar li.active {
  background-color: #bad489;
}

.sidebar li i.active {
  background-color: #bad489;
}

/* .sidebar li { 
  color: white;
  stroke: black;
  fill: black;
}  */

/*
li.active i {
   font-weight: bold; 
}*/

li a:hover {
  background-color: #1e5696;
}

.firsticon {
  /* border: 2px solid #bad489;
  border-left: 2px solid #bad489;
  border-right: 2px solid #bad489; */
  /* border-bottom: 2px solid #bad489; */
  padding: 2px;
  margin-top: 0px;
  margin-left: 0px;
  margin-right: 0px;
  margin-bottom: 0px;
}

.top-icons {
  display: flex;
  flex-direction: column;
}

.icon-spacer {
  height: 50px;
  /* Fill up the space between top and bottom icons */
}

.bottom-icons {
  display: flex;
  flex-direction: column;
  margin-top: auto;
  /* Pushes bottom-icons to the bottom */
  gap: 10px;
  /* Space between bottom icons */
}
</style>
