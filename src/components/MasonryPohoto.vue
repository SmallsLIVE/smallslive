<script setup>
import { MasonryWall } from '@yeger/vue-masonry-wall'

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

</script>

<template>
    <div class="w-full max-w-[75rem] mx-auto px-6 py-12">

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
                    class="w-10 h-10 min-w-[40px] min-h-[40px] border-4 border-white border-t-transparent rounded-full animate-spin">
                </div>
            </div>

            <!-- Loading Text -->
            <div class="mt-4 mb-5 text-sm font-semibold tracking-[0.25em] uppercase text-white">
                Loading...
            </div>
        </div>

        <MasonryWall v-else :items="props.photos" :column-width="300" :gap="30">
            <template #default="{ item }">

                <div class="group overflow-hidden rounded-xl bg-black">
                    <img :src="item.photo" :alt="item.title" loading="lazy"
                        class="w-full h-auto object-cover transition duration-500 group-hover:scale-105" />

                </div>

            </template>
        </MasonryWall>

    </div>
</template>
