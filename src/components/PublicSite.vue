<template>
  <div class="site">
    <div v-if="isLoading" class="loading-state">Nacitavam CNK...</div>

    <template v-else>
      <nav class="nav">
        <a class="nav-logo" href="#hero" aria-label="Cloud Native Kosice">
          <img :src="logoImage" alt="Cloud Native Kosice logo" />
        </a>

        <ul class="nav-menu">
          <li><a href="#hero">Uvod</a></li>
          <li><a href="#sessions">Program</a></li>
          <li><a href="#notify">Email</a></li>
          <li><a href="#history">Historia</a></li>
          <li><a href="#location">Miesto</a></li>
        </ul>
      </nav>

      <section id="hero" class="hero">
        <div class="hero-motion" aria-hidden="true">
          <span></span>
          <span></span>
          <span></span>
        </div>

        <div class="hero-container">
          <p class="hero-kicker">Komunitne meetupy v Kosiciach</p>
          <h1>{{ featuredEvent.title }}</h1>
          <p v-if="featuredEvent.subtitle" class="hero-subtitle">{{ featuredEvent.subtitle }}</p>
          <p class="hero-date">
            Meetup #{{ featuredEvent.number }}:
            <strong>{{ scheduleLabel }}</strong>
          </p>
          <p class="hero-place">{{ featuredEvent.venue }}, {{ featuredEvent.address }}</p>
          <p class="hero-description">{{ featuredEvent.intro }}</p>
        </div>
      </section>

      <section id="sessions" class="sessions">
        <div class="sessions-container">
          <h2>Dalsi meetup</h2>
          <p class="section-lead">{{ featuredEvent.summary }}</p>

          <form id="notify" class="notify-panel" @submit.prevent="handleSignup">
            <div>
              <span class="panel-label">Pozvanka emailom</span>
              <h3>Daj nam email a posleme ti dalsiu akciu</h3>
              <p>
                Ked bude potvrdeny termin a program, posleme pozvanku ludom z tohto zoznamu.
              </p>
            </div>
            <div class="notify-form">
              <input
                v-model="email"
                type="email"
                autocomplete="email"
                placeholder="tvoj@email.sk"
                aria-label="Emailova adresa"
                required
              />
              <button type="submit">Chcem pozvanku</button>
              <p v-if="signupMessage" class="signup-message">{{ signupMessage }}</p>
              <p v-if="signupError" class="signup-error">{{ signupError }}</p>
            </div>
          </form>

          <div v-if="showFeaturedProgram" class="talk-list">
            <article
              v-for="(talk, index) in visibleFeaturedTalks"
              :key="`${featuredEvent.id}-${talk.title}-${index}`"
              class="talk-item"
            >
              <h3>Tema {{ index + 1 }}: {{ talk.title }}</h3>
              <p class="speaker">{{ talk.speaker }}</p>
              <p>{{ talk.abstract }}</p>
            </article>
          </div>

          <div v-if="showFeaturedDemo" class="demo-block">
            <h3>Co mozes cakat</h3>
            <ul class="session-list">
              <li v-for="point in visibleFeaturedDemoPoints" :key="point">{{ point }}</li>
            </ul>
          </div>
        </div>
      </section>

      <section id="history" class="history">
        <div class="history-container">
          <h2>Historia meetupov</h2>
          <p class="section-lead">
            {{ archiveEvents.length }} starsich komunitnych eventov Cloud Native Kosice.
          </p>

          <div class="history-layout">
            <div class="history-tabs" aria-label="Starsie eventy">
              <button
                v-for="event in archiveEvents"
                :key="event.id"
                type="button"
                :class="{ active: event.id === activeArchiveId }"
                @click="activeArchiveId = event.id"
              >
                <span>#{{ event.number }}</span>
                {{ event.subtitle }}
              </button>
            </div>

            <article v-if="selectedArchiveEvent" class="history-detail">
              <div class="history-title">
                <span>Meetup #{{ selectedArchiveEvent.number }}</span>
              </div>
              <h3>{{ selectedArchiveEvent.subtitle }}</h3>
              <p class="history-meta">
                {{ formatDate(selectedArchiveEvent.date) }} o {{ selectedArchiveEvent.time }} /
                {{ selectedArchiveEvent.venue }}, {{ selectedArchiveEvent.address }}
              </p>
              <p>{{ selectedArchiveEvent.summary }}</p>

              <ul class="history-talks">
                <li v-for="talk in selectedArchiveEvent.talks" :key="talk.title">
                  <strong>{{ talk.title }}</strong>
                  <span>{{ talk.abstract }}</span>
                </li>
              </ul>
            </article>
          </div>
        </div>
      </section>

      <section id="about" class="about">
        <div class="about-container">
          <h2>{{ settings.name }}</h2>
          <p>{{ settings.tagline }}</p>
          <p>{{ settings.description }}</p>
          <ul class="facts">
            <li>{{ settings.industry }}</li>
            <li>{{ settings.location }}</li>
          </ul>
        </div>
      </section>

      <section id="location" class="location">
        <div class="location-container">
          <h2>Miesto a cas</h2>
          <p>
            {{ featuredEvent.venue }}
            <br />
            {{ featuredEvent.address }}
            <br />
            {{ locationTimeLabel }}
          </p>
          <p class="hashtags">{{ tagsLine }}</p>
        </div>
      </section>

      <footer class="footer">
        <div class="footer-container">
          <a href="https://marek-horvath.github.io/portfolio/cnk" target="_blank" rel="noopener noreferrer">
            Autor: Marek Horvath
          </a>
          <div class="footer-meta">
            <span>{{ settings.name }}</span>
            <span>Posledna aktualizacia: {{ lastUpdated }}</span>
          </div>
        </div>
      </footer>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { loadContent, saveSubscriber } from '@/services/cnkDb'
import logoImage from '@/assets/logo.png'

defineEmits(['open-admin'])

const isLoading = ref(true)
const settings = ref({})
const events = ref([])
const activeArchiveId = ref('')
const lastUpdated = '06.07.2026'
const email = ref('')
const signupMessage = ref('')
const signupError = ref('')

const featuredEvent = computed(() => {
  return events.value.find((event) => event.featured) || events.value[0] || {}
})

const archiveEvents = computed(() => {
  return events.value.filter((event) => event.id !== featuredEvent.value.id)
})

const selectedArchiveEvent = computed(() => {
  return archiveEvents.value.find((event) => event.id === activeArchiveId.value) || archiveEvents.value[0]
})

const tagsLine = computed(() => {
  const tags = featuredEvent.value.tags || []
  return tags.map((tag) => `#${tag.replace(/\s+/g, '')}`).join(' ')
})

const hasScheduledEvent = computed(() => {
  return Boolean(featuredEvent.value.date && !featuredEvent.value.isTba)
})

const visibleFeaturedTalks = computed(() => {
  if (!hasScheduledEvent.value) {
    return []
  }

  return (featuredEvent.value.talks || []).filter((talk) => {
    return talk.title || talk.speaker || talk.abstract
  })
})

const visibleFeaturedDemoPoints = computed(() => {
  if (!hasScheduledEvent.value) {
    return []
  }

  return (featuredEvent.value.demoPoints || []).filter(Boolean)
})

const showFeaturedProgram = computed(() => {
  return visibleFeaturedTalks.value.length > 0
})

const showFeaturedDemo = computed(() => {
  return visibleFeaturedDemoPoints.value.length > 0
})

const scheduleLabel = computed(() => {
  if (!hasScheduledEvent.value) {
    return 'termin pripravujeme'
  }

  return `${formatDate(featuredEvent.value.date)} o ${featuredEvent.value.time}`
})

const locationTimeLabel = computed(() => {
  if (!hasScheduledEvent.value) {
    return 'Termin pripravujeme'
  }

  return `Zacina o ${featuredEvent.value.time}`
})

watch(
  archiveEvents,
  (items) => {
    if (!items.some((event) => event.id === activeArchiveId.value)) {
      activeArchiveId.value = items[0]?.id || ''
    }
  },
  { immediate: true }
)

onMounted(async () => {
  const content = await loadContent()
  settings.value = content.settings
  events.value = content.events
  activeArchiveId.value = archiveEvents.value[0]?.id || ''
  isLoading.value = false
})

function formatDate(value) {
  if (!value) {
    return 'Datum nie je urceny'
  }

  const [year, month, day] = value.split('-')
  return `${day}.${month}.${year}`
}

async function handleSignup() {
  signupMessage.value = ''
  signupError.value = ''

  const value = email.value.trim()
  const isValidEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)

  if (!isValidEmail) {
    signupError.value = 'Zadaj platny email.'
    return
  }

  try {
    const savedEmail = await saveSubscriber(value)
    email.value = ''
    signupMessage.value = `${savedEmail} je zapisany v zozname.`
  } catch (error) {
    console.error(error)
    signupError.value = 'Email sa nepodarilo ulozit. Skus to prosim neskor.'
  }
}
</script>

<style scoped>
.site {
  min-height: 100vh;
  background-color: #050a30;
  color: #48fcfa;
  font-family: 'Rajdhani', 'Segoe UI', Arial, sans-serif;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 0;
}

.loading-state {
  display: grid;
  min-height: 100vh;
  place-items: center;
  font-size: 1.4rem;
}

.nav {
  display: flex;
  align-items: center;
  padding: 20px 10%;
  background-color: #050a30;
}

.nav-logo {
  flex: 1;
}

.nav-logo img {
  width: 100px;
  height: 100px;
  object-fit: contain;
  filter: drop-shadow(0 0 14px rgba(72, 252, 250, 0.38));
  animation: logoFloat 5.5s ease-in-out infinite;
}

.nav-menu {
  display: flex;
  gap: 30px;
  align-items: center;
  margin: 0;
  padding: 0;
}

.nav-menu li {
  list-style: none;
}

.nav-menu a,
.footer a {
  border: 0;
  background: transparent;
  color: #48fcfa;
  font-family: 'Mokoto', Arial, sans-serif;
  font-size: 0.95rem;
  font-weight: 700;
  text-transform: uppercase;
  cursor: pointer;
}

.nav-menu a:hover,
.footer a:hover {
  color: #ffffff;
}

.hero {
  position: relative;
  overflow: hidden;
  background: #050a30;
  padding: 68px 10% 86px;
  text-align: center;
}

.hero::before {
  position: absolute;
  inset: 0;
  content: '';
  background-image:
    linear-gradient(rgba(72, 252, 250, 0.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(72, 252, 250, 0.07) 1px, transparent 1px);
  background-size: 52px 52px;
  mask-image: linear-gradient(to bottom, transparent, #000 16%, #000 72%, transparent);
  opacity: 0.55;
  transform: translate3d(0, 0, 0);
  animation: gridDrift 18s linear infinite;
}

.hero::after {
  position: absolute;
  inset: 0;
  content: '';
  background: linear-gradient(
    180deg,
    transparent 0%,
    rgba(72, 252, 250, 0.1) 48%,
    transparent 54%
  );
  opacity: 0.42;
  transform: translateY(-70%);
  animation: scanSweep 7.5s ease-in-out infinite;
}

.hero-motion {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.9;
}

.hero-motion span {
  position: absolute;
  left: -18%;
  width: 42%;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(72, 252, 250, 0.9), transparent);
  box-shadow: 0 0 20px rgba(72, 252, 250, 0.55);
  animation: dataLine 9s linear infinite;
}

.hero-motion span:nth-child(1) {
  top: 28%;
}

.hero-motion span:nth-child(2) {
  top: 48%;
  animation-delay: -3s;
  animation-duration: 11s;
}

.hero-motion span:nth-child(3) {
  top: 68%;
  animation-delay: -6s;
  animation-duration: 13s;
}

.hero-container {
  position: relative;
  z-index: 1;
  max-width: 980px;
  margin: 0 auto;
}

.hero-kicker {
  margin: 0 0 20px;
  color: rgba(72, 252, 250, 0.74);
  font-size: 0.95rem;
  text-transform: uppercase;
}

h1,
h2,
h3,
p,
button,
a {
  overflow-wrap: anywhere;
}

h1 {
  margin: 0;
  color: #48fcfa;
  font-family: 'Mokoto', Arial, sans-serif;
  font-size: clamp(2rem, 5vw, 3.3rem);
  line-height: 1.15;
  text-transform: uppercase;
}

h2 {
  margin: 0 0 28px;
  font-family: 'Mokoto', Arial, sans-serif;
  font-size: clamp(1.8rem, 4vw, 2.7rem);
  line-height: 1.15;
  text-transform: uppercase;
}

h3 {
  margin: 0 0 10px;
  font-family: 'Mokoto', Arial, sans-serif;
  font-size: 1.14rem;
  line-height: 1.3;
  text-transform: uppercase;
}

.hero-subtitle {
  margin: 20px auto 0;
  max-width: 840px;
  color: #ffffff;
  font-size: clamp(1.05rem, 2.5vw, 1.45rem);
  font-weight: 700;
  line-height: 1.45;
}

.hero-date,
.hero-place {
  margin: 22px 0 0;
  color: #48fcfa;
  font-size: 1.16rem;
  font-weight: 700;
}

.hero-place {
  margin-top: 16px;
}

.hero-description,
.section-lead,
.talk-item p,
.history-detail p,
.about p,
.location p {
  line-height: 1.65;
}

.hero-description {
  max-width: 850px;
  margin: 28px auto 0;
  color: #48fcfa;
  font-size: 1.12rem;
}

.sessions,
.history,
.about {
  background-color: #ffffff;
  color: #050a30;
  padding: 72px 10%;
  text-align: center;
}

.sessions-container,
.history-container,
.about-container,
.location-container {
  max-width: 960px;
  margin: 0 auto;
}

.section-lead {
  max-width: 880px;
  margin: 0 auto 34px;
}

.talk-list {
  display: grid;
  gap: 28px;
  margin: 36px auto;
  text-align: left;
}

.talk-item {
  padding: 0 0 24px;
  border-bottom: 2px solid rgba(5, 10, 48, 0.1);
}

.talk-item p {
  margin: 8px 0 0;
}

.speaker {
  color: #1c8d92;
  font-weight: 700;
}

.notify-panel {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 0.72fr);
  gap: 26px;
  align-items: center;
  margin: 30px 0 42px;
  border: 2px solid #050a30;
  background:
    linear-gradient(135deg, rgba(72, 252, 250, 0.11), transparent 58%),
    #050a30;
  color: #48fcfa;
  padding: clamp(22px, 4vw, 34px);
  text-align: left;
}

.notify-panel h3 {
  color: #ffffff;
}

.notify-panel p {
  margin: 10px 0 0;
  line-height: 1.55;
}

.panel-label {
  display: inline-block;
  margin-bottom: 12px;
  color: rgba(72, 252, 250, 0.76);
  font-family: 'Mokoto', Arial, sans-serif;
  font-size: 0.76rem;
  text-transform: uppercase;
}

.notify-form {
  display: grid;
  gap: 10px;
}

.notify-form input,
.notify-form button {
  width: 100%;
  min-height: 48px;
  border: 2px solid #48fcfa;
  font-family: 'Rajdhani', 'Segoe UI', Arial, sans-serif;
  font-size: 1rem;
  font-weight: 700;
}

.notify-form input {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
  padding: 0 14px;
}

.notify-form input::placeholder {
  color: rgba(255, 255, 255, 0.58);
}

.notify-form button {
  background: #48fcfa;
  color: #050a30;
  cursor: pointer;
}

.signup-message,
.signup-error {
  margin: 0;
  font-weight: 700;
}

.signup-message {
  color: #ffffff;
}

.signup-error {
  color: #ffb3b3;
}

.demo-block {
  margin: 34px auto 0;
  padding-top: 6px;
}

.session-list {
  display: inline-grid;
  gap: 10px;
  margin: 16px 0 0;
  padding: 0;
  text-align: left;
}

.session-list li {
  list-style: none;
}

.session-list li::before {
  content: '>';
  margin-right: 10px;
  color: #1c8d92;
  font-family: 'Mokoto', Arial, sans-serif;
}

.history {
  padding-top: 20px;
}

.history-layout {
  display: grid;
  grid-template-columns: minmax(220px, 320px) minmax(0, 1fr);
  gap: 30px;
  align-items: start;
  text-align: left;
}

.history-tabs {
  display: grid;
  gap: 10px;
  max-height: 520px;
  overflow: auto;
  padding-right: 6px;
}

.history-tabs button {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 8px;
  align-items: center;
  width: 100%;
  border: 2px solid #050a30;
  border-radius: 0;
  background: #ffffff;
  color: #050a30;
  padding: 12px;
  font-family: 'Rajdhani', 'Segoe UI', Arial, sans-serif;
  font-size: 0.82rem;
  font-weight: 700;
  line-height: 1.35;
  text-align: left;
  cursor: pointer;
}

.history-tabs button.active {
  background: #050a30;
  color: #48fcfa;
}

.history-tabs span {
  color: #1c8d92;
  font-weight: 700;
}

.history-tabs button.active span {
  color: #ffffff;
}

.history-detail {
  min-height: 420px;
  border: 2px solid #050a30;
  padding: 28px;
}

.history-title {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  color: #1c8d92;
  text-transform: uppercase;
  font-family: 'Mokoto', Arial, sans-serif;
}

.history-title strong {
  border: 2px solid #1c8d92;
  padding: 4px 8px;
  font-size: 0.68rem;
}

.history-detail h3 {
  font-size: 1.6rem;
}

.history-meta {
  color: #1c8d92;
  font-weight: 700;
}

.history-talks {
  display: grid;
  gap: 16px;
  margin: 24px 0 0;
  padding: 0;
}

.history-talks li {
  display: grid;
  gap: 7px;
  list-style: none;
}

.history-talks span {
  line-height: 1.55;
}

.about {
  padding-top: 26px;
}

.facts {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  margin: 26px 0 0;
  padding: 0;
}

.facts li {
  list-style: none;
  border: 2px solid #050a30;
  padding: 10px 14px;
}

.location {
  background-color: #050a30;
  padding: 78px 10%;
  text-align: center;
}

.location h2 {
  color: #48fcfa;
}

.location p {
  margin: 0 0 24px;
  color: #48fcfa;
}

.hashtags {
  word-spacing: 6px;
}

.footer {
  background-color: #050a30;
  padding: 24px 10%;
  color: #48fcfa;
}

.footer-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  flex-wrap: wrap;
}

.footer-meta {
  display: flex;
  gap: 18px;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-end;
}

@keyframes gridDrift {
  from {
    background-position: 0 0, 0 0;
  }

  to {
    background-position: 104px 52px, 104px 52px;
  }
}

@keyframes scanSweep {
  0%,
  22% {
    transform: translateY(-80%);
  }

  68%,
  100% {
    transform: translateY(80%);
  }
}

@keyframes dataLine {
  from {
    transform: translateX(0);
  }

  to {
    transform: translateX(330%);
  }
}

@keyframes logoFloat {
  0%,
  100% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-7px);
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero::before,
  .hero::after,
  .hero-motion span,
  .nav-logo img {
    animation: none;
  }
}

@media (max-width: 900px) {
  .nav {
    align-items: flex-start;
    flex-direction: column;
    gap: 18px;
  }

  .nav-menu {
    flex-wrap: wrap;
    gap: 16px 22px;
  }

  .history-layout {
    grid-template-columns: 1fr;
  }

  .notify-panel {
    grid-template-columns: 1fr;
  }

  .history-tabs {
    max-height: none;
  }
}

@media (max-width: 640px) {
  .nav,
  .hero,
  .sessions,
  .history,
  .about,
  .location,
  .footer {
    padding-left: 22px;
    padding-right: 22px;
  }

  .nav-logo img {
    width: 82px;
    height: 82px;
  }

  .nav-menu {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    width: 100%;
  }

  .history-detail {
    padding: 20px;
  }
}
</style>
