<script setup>
import { useInfiniteScroll } from '@vueuse/core'
import Header from '@/components/Header.vue';
import eventService from '@/services/eventService';
import { computed, onMounted, ref } from 'vue'

const loading = ref(false)
const venueId = 3
const dayList = ref([]);
const limit = ref(5)
const offset = ref(0)
const count = ref(0)
const loadMoreTrigger = ref(null)

const hasMore = computed(() =>
  dayList.value.length < count.value
)

const isInitialLoading = computed(() =>
  loading.value && dayList.value.length === 0
)


async function getAllEvents() {
  if (loading.value) return

  try {
    loading.value = true
    const response = await eventService.getAllEvents({
      venue: venueId,
      limit: limit.value,
      offset: offset.value,
    })
    const data = response.data
    const newItems = data?.results?.day_list ?? []
    dayList.value.push(...newItems)
    count.value = data?.count ?? 0
    offset.value += newItems.length
  } catch (error) {
    console.log(error);
  } finally {
    loading.value = false
  }
}

useInfiniteScroll(
  loadMoreTrigger,
  () => {
    if (hasMore.value && !loading.value) {
      getAllEvents()
    }
  },
  {
    distance: 100,
  }
)

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
    return new URL(ev.absolute_url, siteUrl).href;
  }

  return "#";
}
</script>

<template>
  <Header />
  <section class="relative overflow-hidden">
    <div class="relative main-section mx-auto max-w-5xl md:mt-5 mb-10 h-auto rounded-[10px] px-4 py-5 font-raleway">
      <div class="text-center">
        <h1 class="text-[28px] md:text-[2.5rem] font-bold tracking-[0.2em] uppercase">
          SCHEDULE
        </h1>
        <div
          class="space-y-6 text-[14px] md:text-[17px] font-light tracking-[0.12em] md:tracking-[0.18em] text-gray-200 uppercase my-8">
          <p v-if="!loading && count" class="mt-4 text-sm">
            Please click on the link for additional information and advanced ticketing
          </p>


          <div>
            <!-- Initial Empty state -->
            <div v-if="isInitialLoading" class="absolute inset-0 z-20 flex flex-col mt-32 items-center justify-center">
              <!-- Spinner -->
              <div class="flex items-center justify-center">
                <div
                  class="w-10 h-10 min-w-[40px] min-h-[40px] border-4 border-white border-t-transparent rounded-full animate-spin">
                </div>
              </div>
              <div class="mt-4 mb-5 text-sm font-semibold tracking-[0.25em] uppercase text-white">
                Loading...
              </div>
            </div>


            <!-- No Results State -->
            <div v-else-if="!dayList.length"
              class="flex flex-col items-center justify-center md:py-20 text-center uppercase tracking-[0.2em] text-white">

              <h3 class="text-2xl font-bold tracking-[0.3em]">
                NO EVENTS FOUND
              </h3>

              <p
                class="text-[14px] md:text-[16px] font-light md:tracking-[0.18em] text-gray-200 uppercase my-8 tracking-[0.18em] max-w-lg leading-7">
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
                    {{ ev.set_hours_display?.split('-')[0].trim() }}
                  </div>

                  <a target="_blank" :href="eventHref(ev)" class="mt-1 inline-block underline hover:text-orange-300">
                    {{ ev.title }}
                  </a>
                </div>
              </div>
            </div>
            <div ref="loadMoreTrigger" class="h-10"></div>
            <div v-if="loading && dayList.length" class="py-6 text-center">
              <div class="w-6 h-6 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

</template>

<style scoped></style>
