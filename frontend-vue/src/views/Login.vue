<template>
  <div class="login-container">
    <div class="login-form">
      <img src="@/assets/logo.svg" alt="Logo" class="logo" />
      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="username">Username:</label>
          <input type="text" v-model="username" id="username" required />
        </div>
        <div class="input-group">
          <label for="password">Password:</label>
          <input type="password" v-model="password" id="password" required />
        </div>
        <div class="input-group">
          <label for="url">Server URL:</label>
          <input type="url" v-model="url" id="url" required placeholder="http://ehrbase:8080/ehrbase/" />
        </div>
        <button type="submit">Login</button>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </form>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

export default {
  name: 'LoginPage',
  setup() {
    const username = ref('');
    const password = ref('');
    const url = ref('');
    const errorMessage = ref('');
    const router = useRouter();

    const handleLogin = async () => {
      errorMessage.value = ''; // Reset error message

      try {
        const response = await axios.post('http://localhost:5000/auth/login', {
          username: username.value,
          password: password.value,
          url: url.value,
        });

        // If login is successful, redirect to another page
        if (response.status === 200 && response.data.token) {
          localStorage.setItem('authToken', response.data.token); // Store auth token
          localStorage.setItem('username', username.value); // Store username
          localStorage.setItem('isAuthenticated', true); // Store authentication status
          router.push({ name: 'home' }); // Navigate to dashboard
        }
      } catch (error) {
        errorMessage.value = 'Login failed. Please check your credentials and try again.';
      }
    };

    return {
      username,
      password,
      url,
      errorMessage,
      handleLogin,
    };
  },
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f4f4f4;
}

.login-form {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  width: 300px;
  text-align: center;
}

.logo {
  width: 100px;
  margin-bottom: 1rem;
}

.input-group {
  margin-bottom: 1rem;
}

input {
  width: 100%;
  padding: 0.8rem;
  margin-top: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  width: 100%;
  padding: 0.8rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}

button:hover {
  background-color: #45a049;
}

.error-message {
  color: red;
  font-size: 0.9rem;
  margin-top: 1rem;
}
</style>

