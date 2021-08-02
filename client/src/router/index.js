import { createRouter, createWebHistory } from "vue-router";
import HomeScreen from "../components/HomeScreen.vue";
import AboutScreen from "../components/AboutScreen.vue";

const routes = [
  {
    path: "/",
    name: "HomeScreen",
    component: HomeScreen
  },
  {
    path: "/about/",
    name: "AboutScreen",
    component: AboutScreen
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

export default router;
