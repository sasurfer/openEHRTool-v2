<template>
  <div class="modal" v-if="isVisible">
    <div class="modal-content">
      <h2>Stored EHRs:</h2>
      <RotateSquare2 class='ehrspinner' v-if="isLoading" :size="'40px'" :background="'#ff5733'"></RotateSquare2>
      <ol>
        <li v-for="(ehr, index) in ehrData" :key="ehr"
          :class="{ 'odd-item': index % 2 !== 0, 'even-item': index % 2 === 0 }">
          {{ ehr }}
        </li>
      </ol>
      <!-- Add more user information as needed -->

      <!-- <div class="buttons">
        <button @click="closeEHRModal">Close</button>
      </div> -->
    </div>
  </div>
</template>

<script>
import RotateSquare2 from '@/components/ui/RotateSquare2.vue';
export default {
  props: {
    isVisible: {
      type: Boolean,
      required: true,
    },
    isLoading: {
      type: Boolean,
      required: true,
    },
    ehrData: {
      type: Array,
      required: true,
    },
  },
  components: {
    RotateSquare2,
  },
  methods: {
    closeEHRModal() {
      this.$emit("close-ehr-modal");
    },
  },
};
</script>

<style scoped>
.modal {
  position: fixed;
  top: 0;
  right: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 10px;
  background-color: #5e5d5d;
}

.modal-content {
  background-color: #5e5d5d;
  color: white;
  border-radius: 10px;
  width: 400px;
  max-width: 100%;
  height: 300px;
  max-height: 100%;
  overflow-y: scroll;
  text-align: center;
}

.buttons {
  display: flex;
  margin-top: 40px;
  margin-left: 60px;
  margin-right: 40px;
}

button {
  /* padding: 0px 20px; */
  /* margin: 10px 10px; */
  font-size: 1rem;
  cursor: pointer;
}

button:hover {
  background-color: #ccc;
}

.even-item {
  background-color: #5e5d5d;
  ;
  /* Light grey for even items */
}

/* Style for odd items */
.odd-item {
  background-color: #912929;
  /* Slightly darker grey for odd items */
}

.ehrspinner {
  margin-top: 20px;
  margin-bottom: 20px;
  margin-left: 60px;
  margin-right: 20px;
  padding: 20px;
}
</style>
