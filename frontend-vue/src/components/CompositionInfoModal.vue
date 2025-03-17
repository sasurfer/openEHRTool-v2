<template>
  <div class="modal" v-if="isVisible">
    <div class="modal-content">
      <h2>Stored Compositions:</h2>
      <ol>
        <li v-for="(composition,index) in compositionData" :key="composition" :class="{'odd-item': index % 2 !== 0, 'even-item': index % 2 === 0}">
          {{ composition }}
        </li>
      </ol>

      <div class="buttons">
        <button @click="closeCompositionModal">Close</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    isVisible: {
      type: Boolean,
      required: true,
    },
    compositionData: {
      type: Array,
      required: true,
    },
  },
  methods: {
    closeCompositionModal() {
      this.$emit("close-composition-modal");
    },
  },
};
</script>

<style scoped>
.modal {
  position: fixed;
  top: 290px;
  right:40px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.5);
  border-radius: 10px;
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
  margin-top: 20px;
}

button {
  padding: 10px 20px;
  font-size: 1rem;
  cursor: pointer;
}

button:hover {
  background-color: #ccc;
}

.even-item {
  background-color:  #5e5d5d;; /* Light grey for even items */
}

/* Style for odd items */
.odd-item {
  background-color: #912929; /* Slightly darker grey for odd items */
}
  </style>

