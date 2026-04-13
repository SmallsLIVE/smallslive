<template>
  <section id="mc_embed_shell" class="py-5">
    <div class="container mx-auto px-4">
      <div class="flex flex-col items-center">

        <div id="mc_embed_signup" class="w-full max-w-xl">

          <!-- Response messages -->
          <div v-if="errorMessage"
            class="mb-4 px-4 py-3 rounded bg-red-900/50 border border-red-500 text-red-300 text-sm"
            v-html="errorMessage"
          />
          <div v-if="successMessage"
            class="mb-4 px-4 py-3 rounded bg-green-900/50 border border-green-500 text-green-300 text-sm"
            v-html="successMessage"
          />

          <label for="mce-EMAIL" class="block text-white text-sm font-medium mb-3 tracking-wide uppercase">
            Subscribe to our newsletter
          </label>

          <!-- Input + Button inline -->
          <div class="flex items-stretch gap-0">
            <input
              v-model="email"
              type="email"
              id="mce-EMAIL"
              name="EMAIL"
              required
              placeholder="Email address"
              class="flex-1 px-4 py-3 bg-transparent border border-white text-white placeholder-gray-400 text-sm focus:outline-none focus:border-gray-300 rounded-l-sm"
            />
            <button
              @click.prevent="subscribe"
              :disabled="isLoading"
              class="px-6 py-3 bg-transparent border border-l-0 cursor-pointer border-white text-white text-sm font-semibold tracking-widest uppercase hover:bg-white hover:text-black transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed rounded-r-sm whitespace-nowrap"
            >
              {{ isLoading ? 'Subscribing...' : 'Subscribe' }}
            </button>
          </div>

          <!-- Validation message -->
          <p v-if="validationMessage" class="mt-2 text-red-400 text-xs">
            {{ validationMessage }}
          </p>

          <!-- Honeypot — do not remove -->
          <div aria-hidden="true" style="position: absolute; left: -5000px;">
            <input
              v-model="honeypot"
              type="text"
              name="b_76eb9d2dd6485b9ecfbcbe904_de8ca4ce7a"
              tabindex="-1"
            />
          </div>

        </div>
      </div>
    </div>
  </section>
</template>


<script setup>
import { ref } from 'vue'

const email           = ref('')
const honeypot        = ref('')
const isLoading       = ref(false)
const errorMessage    = ref('')
const successMessage  = ref('')
const validationMessage = ref('')

const MC_BASE_URL = import.meta.env.VITE_MC_BASE_URL 
const MC_U        = import.meta.env.VITE_MC_U
const MC_ID       = import.meta.env.VITE_MC_ID
const MC_F_ID     = import.meta.env.VITE_MC_F_ID

function validate() {
  if (!email.value) {
    validationMessage.value = 'Email address is required.'
    return false
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email.value)) {
    validationMessage.value = 'Please enter a valid email address.'
    return false
  }
  validationMessage.value = ''
  return true
}

function subscribe() {
  if (!validate()) return

  isLoading.value     = true
  errorMessage.value  = ''
  successMessage.value = ''

  const callbackName = `mcCallback_${Date.now()}`

  const params = new URLSearchParams({
    u:      MC_U,
    id:     MC_ID,
    f_id:   MC_F_ID,
    EMAIL:  email.value,
    [`b_${MC_U}_${MC_ID}`]: honeypot.value,  // honeypot — must stay empty
    c:      callbackName,
  })

  // JSONP — the only way to avoid CORS with Mailchimp
  const script = document.createElement('script')
  script.src = `${MC_BASE_URL}?${params.toString()}`

  window[callbackName] = (data) => {
    isLoading.value = false

    if (data.result === 'success') {
      successMessage.value = data.msg
      email.value = ''
      // Auto-hide success message after 3 seconds
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      errorMessage.value = data.msg
    }

    delete window[callbackName]
    document.body.removeChild(script)
  }

  script.onerror = () => {
    isLoading.value     = false
    errorMessage.value  = 'Something went wrong. Please try again later.'
    delete window[callbackName]
    document.body.removeChild(script)
  }

  document.body.appendChild(script)
}
</script>