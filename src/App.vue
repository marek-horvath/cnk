<template>
  <AdminPage v-if="isAdminRoute" @open-site="navigateToSite" />
  <PublicSite v-else @open-admin="navigateToAdmin" />
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import AdminPage from './components/AdminPage.vue'
import PublicSite from './components/PublicSite.vue'

const basePath = process.env.BASE_URL.replace(/\/$/, '')
const redirectedRoute = new URLSearchParams(window.location.search).get('route')
const redirectedPath = redirectedRoute === 'admin' ? `${basePath}/admin` || '/admin' : ''
const currentPath = ref(redirectedPath || window.location.pathname)

const isAdminRoute = computed(() => {
  return currentPath.value === '/admin' || currentPath.value === `${basePath}/admin`
})

onMounted(() => {
  if (redirectedPath) {
    window.history.replaceState({}, '', redirectedPath)
  }

  window.addEventListener('popstate', syncPath)
})

onBeforeUnmount(() => {
  window.removeEventListener('popstate', syncPath)
})

function syncPath() {
  currentPath.value = window.location.pathname
}

function navigateToAdmin() {
  const target = basePath ? `${basePath}/admin` : '/admin'
  window.history.pushState({}, '', target)
  currentPath.value = target
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function navigateToSite() {
  const target = basePath || '/'
  window.history.pushState({}, '', target)
  currentPath.value = target
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<style>
@font-face {
  font-family: 'Mokoto';
  src: url('@/assets/fonts/Mokoto.ttf') format('truetype');
  font-weight: normal;
  font-style: normal;
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  font-family:
    Inter,
    ui-sans-serif,
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    sans-serif;
  background: #f6f3ec;
  color: #162329;
}

a {
  color: inherit;
  text-decoration: none;
}

img {
  display: block;
  max-width: 100%;
}
</style>
