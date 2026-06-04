import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import PersonsView from '../views/PersonsView.vue'
import PersonPhotosView from '../views/PersonPhotosView.vue'
import SettingsView from '../views/SettingsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    {
      path: '/libraries/:libraryId/persons',
      name: 'persons',
      component: PersonsView,
      props: true,
    },
    {
      path: '/persons/:personId',
      name: 'person-photos',
      component: PersonPhotosView,
      props: true,
    },
    { path: '/settings', name: 'settings', component: SettingsView },
  ],
})

export default router
