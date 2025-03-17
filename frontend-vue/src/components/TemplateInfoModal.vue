<template>
  <div class="modal" v-if="isVisible">
    <div class="modal-content">
      <h2>Stored Templates:</h2>
      <ul>
        <li v-for="(item,index) in templateData" :key="index"
        :class="{'odd-item': index % 2 !== 0, 'even-item': index % 2 === 0}">
        {{ item.template_id }} {{ item.created_timestamp }}
        </li>
      </ul>

      <div class="buttons">
        <button @click="closeTemplateModal">Close</button>
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
    templateData: {
      type: Object,
      required: true,
    },
  },
  methods: {
    closeTemplateModal() {
      this.$emit("close-template-modal");
    },
  },
};
</script>

<style scoped>
.modal {
  position: fixed;
  top: 0;
  right: 440px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 10px;
  background-color:  #5e5d5d;
}

.modal-content {
  background-color: #5e5d5d;
  color: white;
  border-radius: 10px;
  width: 600px;
  max-width: 100%;
  height: 280px;
  max-height: 100%;
  overflow-y: scroll;
  text-align: center
}

.buttons {
  display: flex;
  margin-top: 40px;
  margin-left: 60px;
  margin-right: 40px;
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

