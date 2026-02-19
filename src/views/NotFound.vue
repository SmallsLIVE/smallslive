<template>
  <section class="bg-white">
    <div class="max-w-3xl mx-auto px-4 py-10">
      <div class="border border-[#F6ECC1] rounded-[10px] px-6 py-8 text-center">
        <!-- Frame header -->
        <div class="mb-6">
          <div class="h-px bg-[#DCB505] mx-[70px] mb-1"></div>
          <div class="h-px bg-[#DCB505] mb-3"></div>

          <h2 class="text-sm font-extrabold tracking-[0.35em] text-black">
            PAGE NOT FOUND
          </h2>

          <div class="h-px bg-[#DCB505] mt-3"></div>
          <div class="h-px bg-[#DCB505] mx-[70px] mt-1"></div>

          <p class="mt-4 text-sm text-black">
            The page you’re looking for doesn’t exist or may have moved.
          </p>
        </div>

        <!-- 404 badge -->
        <div
          class="inline-flex items-center gap-3 rounded-xl border border-[#F6ECC1] bg-white px-4 py-2"
        >
          <span class="text-xs font-extrabold tracking-[0.25em] text-black">404</span>
          <span class="h-4 w-px bg-[#F6ECC1]"></span>
          <span class="text-xs font-semibold text-black/70">
            Not Found
          </span>
        </div>

        <!-- Title + helpers -->
        <div class="mt-6">
          <h3 class="text-base font-extrabold text-[#5e2f80]">
            We can’t find that page.
          </h3>
          <p class="mt-2 text-sm text-black/80">
            Try heading back to the schedule or browsing events.
          </p>
        </div>

        <!-- Actions -->
        <div class="mt-7 flex flex-col items-center gap-3">
          <a
            href="/"
            class="w-full sm:w-auto inline-flex items-center justify-center rounded-[10px] border border-[#F16722] bg-[#F16722]/[0.06] px-5 py-2.5 text-xs font-extrabold tracking-[0.12em] uppercase text-[#F16722] hover:bg-[#F16722]/[0.10]"
          >
            Back to Schedule
          </a>

          <div class="flex flex-col sm:flex-row items-center justify-center gap-3">
            <a
              href="/events"
              class="text-sm text-[#F16722] underline underline-offset-2 hover:text-[#F16722]/90"
            >
              Browse Events
            </a>
            <span class="hidden sm:inline-block h-1 w-1 rounded-full bg-[#F6ECC1]"></span>
            <a
              href="/contact"
              class="text-sm text-[#F16722] underline underline-offset-2 hover:text-[#F16722]/90"
            >
              Info / Contact
            </a>
          </div>
        </div>

        <!-- Hint box -->
        <div class="mt-8 mx-auto max-w-md rounded-[10px] border border-[#F6ECC1] bg-white p-4 text-left">
          <div class="text-xs font-black tracking-[0.2em] uppercase text-[#5e2f80]">
            Quick tip
          </div>
          <p class="mt-2 text-sm text-black/80">
            If you were looking for a specific show, start from the schedule and click an
            event title for details and ticketing.
          </p>
        </div>

        <!-- Bottom divider -->
        <div class="mt-8 h-px bg-[#DCB505]"></div>
      </div>
    </div>
  </section>
</template>

    
<script setup>
    
</script>
    
<style>
    
</style>