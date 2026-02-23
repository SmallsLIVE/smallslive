import InfoView from "@/views/InfoView.vue";
import PhotoView from "@/views/PhotoView.vue";
import ReserveView from "@/views/ReserveView.vue";
import ScheduleView from "@/views/ScheduleView.vue";
import WhoWeAre from "@/views/WhoWeAre.vue";
import SmallsliveView from "@/views/SmallsliveView.vue";
import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: "/", name: "home", component: ScheduleView },
    {
      path: "/who-we-are",
      name: "who-we",
      component: WhoWeAre,
    },
    {
      path: "/smallslive",
      name: "smallslive",
      component: SmallsliveView,
    },
    {
      path: "/info",
      name: "info",
      component: InfoView,
    },
    {
      path: "/reserve",
      name: "reserve",
      component: ReserveView,
    },
    {
      path: "/photos",
      name: "photos",
      component: PhotoView,
    },
    {
      path: "/:pathMatch(.*)*",
      name: "NotFound",
      component: () => import("@/views/NotFound.vue"),
    },
  ],
});

export default router;
