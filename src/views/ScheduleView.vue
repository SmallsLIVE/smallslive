<script setup>
import Header from '@/components/Header.vue';
import eventService from '@/services/eventService';
import { computed, onMounted, ref } from 'vue'

const loading = ref(false)
const dayList = ref([]);
async function getAllEvents() {

  try {
    loading.value = true
    const response = await eventService.getAllEvents()
    // console.log(response.data);
    dayList.value = response.data?.results?.day_list ?? [];
    loading.value = false
  } catch (error) {
    console.log(error);
  }
}

onMounted(() => {
  getAllEvents();
});

const uiDays = computed(() => {
  return (dayList.value || []).map((day) => ({
    day_start: day.day_start,
    events: flattenAndSortDayEvents(day),
  }));
});

function flattenAndSortDayEvents(day) {
  const all = [];
  const dayEvents = day?.day_events || {};

  Object.values(dayEvents).forEach((events) => {
    (events || []).forEach((e) => all.push(e));
  });

  all.sort((a, b) => new Date(a.start) - new Date(b.start));
  return all;
}

// Formatting helpers
function formatDay(dayStart) {
  const d = new Date(`${dayStart}T12:00:00`);
  return d.toLocaleDateString("en-US", {
    weekday: "short",
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}

function formatTime(iso) {
  return new Date(iso).toLocaleTimeString("en-US", {
    timeZone: "America/New_York",
    hour: "numeric",
    minute: "2-digit",
  });
}

// Link logic: tickets_url > link > slug route > fallback
function eventHref(ev) {
  if (ev?.tickets_url) return ev.tickets_url;
  if (ev?.link) return ev.link;

  const siteUrl = import.meta.env.VITE_SITE_URL ?? "";

  if (ev?.id && ev?.slug) {
    return `${siteUrl}/events/${ev.id}-${ev.slug}/`;
  }

  return "#";
}
</script>

<template>
  <Header />
  <section class="relative overflow-hidden bg-white">
    <div class="relative main-section mx-auto max-w-3xl mt-5 rounded-[10px] px-4 py-5 border-[#F6ECC1] border-[1px]">
      <div class="text-center">
        <hr class="frame-head-border-sm">
        <hr class="frame-head-border">
        <h2 class="text-sm font-extrabold tracking-[0.35em] text-black">SCHEDULE</h2>
        <hr class="frame-head-border bottom">
        <hr class="frame-head-border-sm bottom">
        <p class="mt-4 text-sm text-black">
          Please click on the link for additional information and advanced ticketing
        </p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="mx-auto mt-10 max-w-md text-center text-sm text-black">
        Loading...
      </div>

      <!-- Days -->
      <div v-else class="mx-auto mt-10 max-w-md">
        <div v-for="day in uiDays" :key="day.day_start" class="mb-10 text-center">
          <h3 class="text-base font-extrabold text-[#5e2f80]">
            {{ formatDay(day.day_start) }}
          </h3>

          <div v-for="ev in day.events" :key="ev.id" class="mt-4">
            <div class="text-sm font-medium text-black">
              {{ formatTime(ev.start) }} to {{ formatTime(ev.end) }}
            </div>

            <a target="_blank" :href="eventHref(ev)"
              class="mt-1 inline-block text-sm text-orange-500 underline underline-offset-2 hover:text-orange-600">
              {{ ev.title }}
            </a>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-if="!loading && uiDays.length === 0" class="mx-auto mt-10 max-w-md text-center text-sm text-black">
        No events found.
      </div>
    </div>
  </section>

</template>

<style scoped>
.frame-head-border-sm.bottom {
  background-color: transparent;
  border-bottom: none;
  border-top: 1px solid #DCB505;
  margin: 4px 70px 0px 70px;
  padding-top: 0;
  padding-bottom: 8px;
}

.frame-head-border.bottom {
  background-color: transparent;
  border-bottom: none;
  border-top: 1px solid #DCB505;
  margin: 10px 0 0 0;
  padding-top: 0;
}

.frame-head-border-sm {
  background-color: transparent;
  border-top: none;
  border-bottom: 1px solid #DCB505;
  margin: 0px 70px 4px 70px;
  padding-top: 20px;
}

.frame-head-border {
  background-color: transparent;
  border-bottom: 1px solid #DCB505;
  margin: 0 0 10px 0;
  border-top: 0;
}


</style>
