<script setup>
import Header from '@/components/Header.vue';
import eventService from '@/services/eventService';
import { computed, onMounted, ref } from 'vue'

const loading = ref(false)
const venueId = 3
const dayList = ref([]);
const limit = ref(5)
const offset = ref(0)
const count = ref(0)


const currentPage = computed(() =>
  Math.floor(offset.value / limit.value) + 1
)

const totalPages = computed(() =>
  Math.ceil(count.value / limit.value)
)

function goNext() {
  if (offset.value + limit.value < count.value) {
    offset.value += limit.value
    getAllEvents()
  }
}

function goPrev() {
  if (offset.value - limit.value >= 0) {
    offset.value -= limit.value
    getAllEvents()
  }
}

async function getAllEvents() {

  try {
    loading.value = true
    const response = await eventService.getAllEvents({
      venue: venueId,
      limit: limit.value,
      offset: offset.value,
    })
    // console.log(response.data);
    const data = response.data
    dayList.value = data?.results?.day_list ?? []
    count.value = data?.count ?? 0
    loading.value = false
  } catch (error) {
    console.log(error);
  } finally {
    loading.value = false
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
  <section class="relative overflow-hidden">
    <div class="relative main-section mx-auto max-w-5xl mt-5 mb-10 rounded-[10px] px-4 py-5 font-raleway">
      <div class="text-center">
        <h1 class="text-[2rem] md:text-[2.5rem] font-bold tracking-[0.2em] uppercase">
          SCHEDULE
        </h1>
        <div
          class="space-y-6 text-[14px] md:text-[17px] font-light tracking-[0.12em] md:tracking-[0.18em] text-gray-200 uppercase my-8">
          <p v-if="!loading && count" class="mt-4 text-sm">
            Please click on the link for additional information and advanced ticketing
          </p>

          <div>
            <!-- Empty state -->
            <div v-if="loading"
              class="absolute inset-0 z-20 flex items-center justify-center bg-white/70 backdrop-blur-sm">
              <div class="text-sm font-semibold text-[#5e2f80]">
                Loading...
              </div>
            </div>

            <!-- No Results State -->
            <div v-else-if="!dayList.length"
              class="flex flex-col items-center justify-center py-20 text-center uppercase tracking-[0.2em] text-white">

              <h3 class="text-2xl font-bold tracking-[0.3em]">
                NO EVENTS FOUND
              </h3>

              <p class="text-[14px] md:text-[16px] font-light md:tracking-[0.18em] text-gray-200 uppercase my-8 tracking-[0.18em] max-w-lg leading-7">
                There are currently no scheduled performances.
                Please check back soon.
              </p>
            </div>

            <!-- Event Days -->
            <div v-else class="mx-auto max-w-md">
              <div v-for="day in uiDays" :key="day.day_start" class="mb-10 text-center">
                <h3 class="font-extrabold">
                  {{ formatDay(day.day_start) }}
                </h3>

                <div v-for="ev in day.events" :key="ev.id">
                  <div class="font-medium">
                    {{ formatTime(ev.start) }} to {{ formatTime(ev.end) }}
                  </div>

                  <a target="_blank" :href="eventHref(ev)"
                    class="mt-1 inline-block underline hover:text-orange-300">
                    {{ ev.title }}
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>



      <!-- Pagination -->
      <div v-if="!loading && count > limit"
        class="mt-6 flex items-center justify-between gap-3 border-t border-[#DCB505] pt-4">

        <button @click="goPrev" :disabled="offset === 0 || loading" class="rounded-md border px-4 cursor-pointer py-2 text-sm font-semibold
           disabled:cursor-not-allowed disabled:opacity-50
           hover:bg-gray-50 hover:text-black">
          Prev
        </button>

        <div class="text-sm font-medium">
          Page {{ currentPage }} of {{ totalPages }}
        </div>

        <button @click="goNext" :disabled="offset + limit >= count || loading" class="rounded-md border cursor-pointer px-4 py-2 text-sm font-semibold
           disabled:cursor-not-allowed disabled:opacity-50
           hover:bg-gray-50 hover:text-black">
          Next
        </button>
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
