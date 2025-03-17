<template>
  <div class="card-content">
    <slot></slot>  <!-- To render content inside CardContent -->
  </div>
</template>

<script>
export default {
  name: 'CardContent'
}
</script>

<style scoped>
.card-content {
  padding: 10px;
}
</style>

