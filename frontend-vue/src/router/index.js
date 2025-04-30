import { createRouter, createWebHistory } from 'vue-router';
import Login from '@/views/Login.vue';
import HomePage from '@/views/HomePage.vue';
import EHRPage from '@/views/EHRPage.vue';
import TemplatePage from '@/views/TemplatePage.vue';
import CompositionPage from '@/views/CompositionPage.vue';

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
    name: 'ehr',
    component: EHRPage,
    meta: { sidebarIndex: 2 }, // EHR icon is index 2
  },
  {
    path: '/template',
    name: 'template',
    component: TemplatePage,
    meta: { sidebarIndex: 3 }, // Template icon is index 3
  },
  {
    path: '/composition',
    name: 'composition',
    component: CompositionPage,
    meta: { sidebarIndex: 4 }, // Composition icon is index 4
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;

