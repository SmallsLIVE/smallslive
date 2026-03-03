<script setup>
import { MasonryWall } from '@yeger/vue-masonry-wall'
import { computed, ref } from 'vue'
import VueEasyLightbox from 'vue-easy-lightbox'


const props = defineProps({
    photos: {
        type: Array,
        required: true
    },
    loading: {
        type: Boolean,
        required: true
    }
})

const visible = ref(false)
const index = ref(0)

const openLightbox = (i) => {
    index.value = i
    visible.value = true
}

const imageList = computed(() =>
    props.photos.map(photo => photo.photo)
)

const images = computed(() =>
  props.photos.map(photo => ({
    src: photo.photo,
    title: photo.title
  }))
)
</script>

<template>
    <div class="w-full max-w-300 mx-auto px-6 py-12">

        <!-- Empty State -->
        <div v-if="!props.photos.length && !props.loading" class="text-center">
            <h3 class="text-lg md:text-xl font-bold tracking-[0.2em] uppercase mt-5">
                No Photos Available. Please check back later.
            </h3>
        </div>

        <!-- Loading state -->
        <div v-if="props.loading" class="absolute inset-0 z-20 flex flex-col mt-5 items-center justify-center">
            <!-- Spinner -->
            <div class="flex items-center justify-center">
                <div
                    class="w-10 h-10 min-w-10 min-h-10 border-4 border-white border-t-transparent rounded-full animate-spin">
                </div>
            </div>

            <!-- Loading Text -->
            <div class="mt-4 mb-5 text-sm font-semibold tracking-[0.25em] uppercase text-white">
                Loading...
            </div>
        </div>

        <MasonryWall v-else :items="props.photos" :column-width="300" :gap="30"> <template #default="{ item, index }">
                <div @click="openLightbox(index)" class="group overflow-hidden rounded-xl bg-black"> <img
                        :src="item.photo" :alt="item.title" loading="lazy"
                        class="w-full h-auto object-cover transition duration-500 group-hover:scale-105 cursor-pointer" />
                </div>
                <p
                    class="mt-2 text-sm text-gray-300 font-raleway uppercase text-[14px] md:text-[16px] bg-white/20 rounded">
                    {{ item.title }}
                </p>
            </template>
        </MasonryWall>

        <VueEasyLightbox :visible="visible" :imgs="images" :index="index" @hide="visible = false">
            <template>
                <div
                    class="absolute bottom-9 left-0 w-full bg-black/60 text-white text-center py-4 text-sm md:text-lg tracking-wider">
                    {{ images[index].title }}
                </div>
            </template>
        </VueEasyLightbox>
    </div>
</template>

<style scoped>
:deep(.vel-img-title) {
    font-size: 20px;
    color: #fff;
}

@media (max-width: 767px) {
  :deep(.vel-img-title) {
    font-size: 16px;
    background-color: #000;
    padding: 20px;
    width: 100%;
  }
}
</style>