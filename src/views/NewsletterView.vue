<template>
    <div class="relative min-h-screen flex flex-col md:block">
        <Header />
        <div class="flex-1 flex items-center justify-center pointer-events-none md:absolute md:inset-0">
            <div class="pointer-events-auto w-full">
                <Newsletter />
            </div>
        </div>
    </div>
</template>

<script setup>
import Header from '@/components/Header.vue';
import Newsletter from '@/components/Newsletter.vue';

</script>