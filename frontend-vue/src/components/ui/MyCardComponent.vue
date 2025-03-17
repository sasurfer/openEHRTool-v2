<template>
  <div class="card">
    <slot></slot>  <!-- To render content passed to Card -->
  </div>
</template>

<script>
export default {
  name: 'MyCardComponent',
}
</script>

<style scoped>
.card {
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: white;
}
</style>
