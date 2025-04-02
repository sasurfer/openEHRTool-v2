<template>
  <div class="modal" v-if="isVisible">
    <div class="modal-content">
      <h3>You are logged in as:</h3>
      <h2><strong> {{ user.name }} </strong></h2>
      <!-- Add more user information as needed -->

      <div class="buttons">
        <button @click="closeModal">Close</button>
        <button @click="logout">Logout</button>
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
    user: {
      type: Object,
      required: true,
    },
  },
  methods: {
    closeModal() {
      this.$emit("close-modal");
    },
    logout() {
      this.$emit("logout");
    },
  },
};
</script>

<style scoped>
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 20px;
  background-color: rgba(0, 0, 0, 0.8);
  z-index: 10;
}

.modal-content {
  background-color: rgb(192, 187, 187);
  padding: 20px;
  border-radius: 8px;
  width: 300px;
  text-align: center;
}

.buttons {
  display: flex;
  justify-content: space-between;
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
</style>

