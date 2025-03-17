<template>
  <div id="app">
    <!-- You can have a global navbar, footer, or other common layout elements here -->
    <router-view />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: 'App',
  setup() {
    const router = useRouter();
    const isLoggedIn = ref(false);

    // Check if the user is logged in (i.e., if there's a valid token in localStorage)
    onMounted(() => {
      const token = localStorage.getItem('authToken');
      if (token) {
        // If the token is found, the user is logged in, so redirect to the home
        isLoggedIn.value = true;
        router.push({ name: 'home' });
      } else {
        // If no token, ensure that the user stays on the login page
        isLoggedIn.value = false;
        router.push({ name: 'login' });
      }
    });

    return {
      isLoggedIn,
    };
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>

