<template>

<div class="relative min-h-screen text-white">
    <!-- Background Image -->
    <div 
      class="fixed absolute inset-0 bg-cover bg-center" 
      :style="{ backgroundImage: 'url(/background.jpg)' }"
    ></div>
    <div class="fixed absolute inset-0 bg-black/60"></div>

    <!-- Main Content -->
    <div class="relative z-10">
      <router-view />
    </div>
  </div>
</template>