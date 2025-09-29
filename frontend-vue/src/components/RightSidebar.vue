<template>
  <div class="app-container">
    <!-- Left Sidebar (Menu with Icons) -->
    <div class="rsidebar">
      <ul>
        <div class="ricons">
          <li v-for="(item, index) in menuItems" :key="index" @click="selectIcon(index)">
            <i :class="item.icon"></i>
            <img v-if="item.iconType === 'svg'" :src="item.icon" alt="icon" width="25" height="25" />
          </li>
        </div>
      </ul>
    </div>
  </div>
</template>

<script>
import ehricon from "@/assets/ehr-icon.svg";
import templateicon from "@/assets/template-icon.svg";
import compositionicon from "@/assets/composition-icon.svg";
import aqlicon from "@/assets/aql-icon.svg";


export default {
  data() {
    return {
      // Icons on the Right Sidebar
      menuItems: [
        { label: 'EHR', iconType: "svg", icon: ehricon },
        { label: 'Template', iconType: "svg", icon: templateicon },
        { label: 'Composition', iconType: "svg", icon: compositionicon },
        { label: 'AQL', iconType: "svg", icon: aqlicon },
      ],
    };
  },
  methods: {
    openEHRInfo() {
      this.$emit("open-ehr-info");
    },
    openTemplateInfo() {
      this.$emit("open-template-info");
    },
    openCompositionInfo() {
      this.$emit("open-composition-info");
    },
    openAQLInfo() {
      this.$emit("open-aql-info");
    },
    // Select the icon from the right sidebar
    selectIcon(index) {
      switch (index) {
        case 0:
          this.openEHRInfo();
          break;
        case 1:
          this.openTemplateInfo();
          break;
        case 2:
          this.openCompositionInfo();
          break;
        case 3:
          this.openAQLInfo();
          break;
        default:
          break;
      }

    },
  },
};
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
}

.rsidebar {
  position: fixed;
  /* Fix sidebar position */
  top: 0;
  right: 0;
  width: 40px;
  background: #5e5d5d;
  color: white;
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

.rsidebar ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  /* flex-grow: 1; */
  align-items: center;
  justify-content: center;
}

.rsidebar li {
  cursor: pointer;
  margin-bottom: 20px;
  margin-top: 20px;
  text-align: center;
  padding: 0px;
}

.rsidebar i {
  margin-left: 3px;
}

li.active {
  background-color: #dd1bad;
  color: white;
}

li.active i {
  font-weight: bold;
}

li a:hover {
  background-color: #1e5696;
}
</style>
