import { createRouter, createWebHistory } from 'vue-router';
import Login from '@/views/Login.vue';
import HomePage from '@/views/HomePage.vue';

const routes = [
  {
    path: '/',
    redirect: '/login',
  },
  {
    path: '/login',
    name: 'login',
    component: Login,
  },
  {
    path: '/home',
    name: 'home',
    component: HomePage,
    meta: { sidebarIndex: 1 }, // Home icon is index 1
  },
  {
    path: '/ehr',
    name : 'ehr',
    component: () => import('@/views/EHRPage.vue'),
    meta: { sidebarIndex: 2 }, // EHR icon is index 2
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;

