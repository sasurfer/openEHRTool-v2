import { createRouter, createWebHistory } from 'vue-router';
import Login from '@/views/Login.vue';
import HomePage from '@/views/HomePage.vue';
import EHRPage from '@/views/EHRPage.vue';
import TemplatePage from '@/views/TemplatePage.vue';
import CompositionPage from '@/views/CompositionPage.vue';
import AQLPage from '@/views/AQLPage.vue';
import LOGPage from '@/views/LOGPage.vue';
import ADMINPage from '@/views/ADMINPage.vue';

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
  },
  {
    path: '/query',
    name: 'query',
    component: AQLPage,
    meta: { sidebarIndex: 5 }, // Query icon is index 5
  },
  {
    path: '/log',
    name: 'log',
    component: LOGPage,
    meta: { sidebarIndex: 9 } // Log icon is index 9
  },
  {
    path: '/admin',
    name: 'admin',
    component: ADMINPage,
    meta: { sidebarIndex: 8 } // Admin icon is index 8
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;

