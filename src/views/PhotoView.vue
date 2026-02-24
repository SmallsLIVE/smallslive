<template>
    <Header />
    <div class="relative flex items-center justify-center font-raleway overflow-hidden my-2 px-5 md:px-0">

        <div class="relative z-10 w-full max-w-[75rem] text-center text-white">
            <MasonryPohoto :photos="masonryPhotos" :loading="loading" />
        </div>
    </div>
</template>

<script setup>
import Header from '@/components/Header.vue';
import MasonryPohoto from '@/components/MasonryPohoto.vue';
import photoService from '@/services/photoService';
import { onMounted, ref } from 'vue';


const loading = ref(false)
const limit = ref(50)
const offset = ref(0)
const masonryPhotos = ref([])

async function getAllPhotos() {

  try {
    loading.value = true
    const response = await photoService.getAllJazzPhotos({
      limit: limit.value,
      offset: offset.value,
    })
    masonryPhotos.value = response?.data?.results ?? []
    loading.value = false
  } catch (error) {
    console.log(error);
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  getAllPhotos();
});
</script>

<style></style>