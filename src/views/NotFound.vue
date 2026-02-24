<template>
  <Header />

  <div class="flex justify-center font-raleway overflow-hidden my-2 min-h-[80vh]">

    <div class="w-full max-w-[75rem] text-white px-6 text-center mt-5">

      <h1 class="text-[7rem] md:text-[11rem] font-bold tracking-normal text-white select-none leading-none">
        404
      </h1>

      <h2 class="text-[1.8rem] md:text-[2.8rem] font-bold tracking-normal text-gray-400 mt-4">
        NOT FOUND
      </h2>

      <div class="mt-12 space-y-6 uppercase tracking-[0.18em] text-white max-w-3xl mx-auto">

        <p class="text-[14px] md:text-[16px] font-light">
          The page you’re looking for doesn’t exist or may have been moved.
        </p>

        <div class="pt-6">
          <RouterLink to="/"
            class="inline-block px-10 py-3 border border-white text-white hover:bg-white hover:text-black transition-all duration-300 tracking-[0.25em]">
            BACK TO HOME
          </RouterLink>
        </div>

      </div>

    </div>
  </div>
</template>

<script setup>
import Header from '@/components/Header.vue'
</script>

<style scoped></style>