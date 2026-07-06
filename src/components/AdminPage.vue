<template>
  <div v-if="!isAuthenticated" class="admin-login">
    <form class="login-box" @submit.prevent="login">
      <p class="eyebrow">Admin</p>
      <h1>Sprava obsahu CNK</h1>
      <p>Zadaj admin heslo na spravu eventov a email zoznamu.</p>
      <input
        v-model="password"
        type="password"
        autocomplete="current-password"
        placeholder="Heslo"
        aria-label="Admin heslo"
      />
      <button type="submit" class="primary-button">Prihlasit</button>
      <p v-if="loginError" class="login-error">{{ loginError }}</p>
    </form>
  </div>

  <div v-else class="admin-page">
    <header class="admin-topbar">
      <div>
        <p class="eyebrow">Admin</p>
        <h1>Sprava obsahu</h1>
      </div>
      <div class="top-actions">
        <button type="button" class="ghost-button" @click="$emit('open-site')">Web</button>
        <button type="button" class="ghost-button" @click="logout">Odhlasit</button>
        <button type="button" class="primary-button" @click="saveCurrent">Ulozit zmeny</button>
      </div>
    </header>

    <main v-if="isLoading" class="admin-loading">Nacitavam data...</main>

    <main v-else class="admin-layout">
      <aside class="event-list">
        <div class="list-header">
          <h2>Eventy</h2>
          <button type="button" class="icon-button" aria-label="Pridat event" @click="addEvent">+</button>
        </div>

        <button
          v-for="event in sortedEvents"
          :key="event.id"
          type="button"
          :class="{ active: event.id === selectedEventId }"
          @click="selectEvent(event.id)"
        >
          <span>#{{ event.number }}</span>
          <strong>{{ event.title }}</strong>
          <small>{{ event.date || 'bez datumu' }}</small>
        </button>
      </aside>

      <section class="editor">
        <div v-if="message" class="status-message">{{ message }}</div>

        <section class="editor-section">
          <div class="section-title">
            <p class="eyebrow">Komunita</p>
            <h2>Texty webu</h2>
          </div>

          <div class="form-grid two-columns">
            <label>
              Nazov
              <input v-model="settings.name" type="text" />
            </label>
            <label>
              Podnadpis
              <input v-model="settings.tagline" type="text" />
            </label>
            <label class="full-span">
              Popis
              <textarea v-model="settings.description" rows="4"></textarea>
            </label>
            <label>
              Odvetvie
              <input v-model="settings.industry" type="text" />
            </label>
            <label>
              Lokalita
              <input v-model="settings.location" type="text" />
            </label>
            <label>
              Organizator
              <input v-model="settings.organizer" type="text" />
            </label>
          </div>
        </section>

        <section v-if="draft" class="editor-section">
          <div class="section-title split-title">
            <div>
              <p class="eyebrow">Event</p>
              <h2>{{ draft.title || 'Novy event' }}</h2>
            </div>
            <button type="button" class="danger-button" @click="deleteCurrent">Vymazat event</button>
          </div>

          <div class="form-grid two-columns">
            <label>
              Cislo meetupu
              <input v-model.number="draft.number" type="number" min="1" />
            </label>
            <label>
              Stav
              <select v-model="draft.status">
                <option value="upcoming">Planovany</option>
                <option value="past">Uskutocneny</option>
                <option value="draft">Koncept</option>
              </select>
            </label>
            <label class="full-span">
              Nazov
              <input v-model="draft.title" type="text" />
            </label>
            <label class="full-span">
              Podtitul
              <input v-model="draft.subtitle" type="text" />
            </label>
            <label>
              Datum
              <input v-model="draft.date" type="date" />
            </label>
            <label>
              Cas
              <input v-model="draft.time" type="time" />
            </label>
            <label>
              Miesto
              <input v-model="draft.venue" type="text" />
            </label>
            <label>
              Adresa
              <input v-model="draft.address" type="text" />
            </label>
            <label class="full-span checkbox-row">
              <input v-model="draft.featured" type="checkbox" />
              Zobrazit ako hlavny event na homepage
            </label>
            <label class="full-span checkbox-row">
              <input v-model="draft.isTba" type="checkbox" />
              Termin alebo program este nie je potvrdeny
            </label>
            <label class="full-span">
              Intro text
              <textarea v-model="draft.intro" rows="3"></textarea>
            </label>
            <label class="full-span">
              Zhrnutie
              <textarea v-model="draft.summary" rows="3"></textarea>
            </label>
            <label class="full-span">
              Tagy oddelene ciarkou
              <input :value="tagsText" type="text" @input="updateTags" />
            </label>
          </div>
        </section>

        <section v-if="draft && draft.isTba" class="editor-section tba-note">
          <div>
            <p class="eyebrow">Program</p>
            <h2>Agenda je skryta</h2>
            <p>
              Ked je event oznaceny ako nepotvrdeny, web nezobrazuje prednasky ani demo body.
              Po potvrdeni terminu vypni tuto volbu a dopln program.
            </p>
          </div>
        </section>

        <section v-if="draft && !draft.isTba" class="editor-section">
          <div class="section-title split-title">
            <div>
              <p class="eyebrow">Prednasky</p>
              <h2>Agenda eventu</h2>
            </div>
            <button type="button" class="ghost-button" @click="addTalk">Pridat prednasku</button>
          </div>

          <div class="repeaters">
            <article v-for="(talk, index) in draft.talks" :key="index" class="repeater">
              <div class="repeater-header">
                <strong>Prednaska {{ index + 1 }}</strong>
                <button type="button" class="text-button" @click="removeTalk(index)">Odstranit</button>
              </div>
              <label>
                Nazov
                <input v-model="talk.title" type="text" />
              </label>
              <label>
                Prednasajuci
                <input v-model="talk.speaker" type="text" />
              </label>
              <label>
                Abstrakt
                <textarea v-model="talk.abstract" rows="3"></textarea>
              </label>
            </article>
          </div>
        </section>

        <section v-if="draft && !draft.isTba" class="editor-section">
          <div class="section-title split-title">
            <div>
              <p class="eyebrow">Demo</p>
              <h2>Body programu</h2>
            </div>
            <button type="button" class="ghost-button" @click="addDemoPoint">Pridat bod</button>
          </div>

          <div class="demo-editor">
            <div v-for="(point, index) in draft.demoPoints" :key="index" class="demo-row">
              <input v-model="draft.demoPoints[index]" type="text" />
              <button type="button" class="text-button" @click="removeDemoPoint(index)">Odstranit</button>
            </div>
          </div>
        </section>

        <section class="editor-section">
          <div class="section-title split-title">
            <div>
              <p class="eyebrow">Email zoznam</p>
              <h2>Odberatelia ({{ subscribers.length }})</h2>
            </div>
            <button
              type="button"
              class="ghost-button"
              :disabled="subscribers.length === 0"
              @click="exportSubscribers"
            >
              Stiahnut CSV
            </button>
          </div>

          <div v-if="subscribers.length" class="subscriber-list">
            <div v-for="subscriber in subscribers" :key="subscriber.email" class="subscriber-row">
              <div>
                <strong>{{ subscriber.email }}</strong>
                <span>{{ formatTimestamp(subscriber.createdAt) }}</span>
              </div>
              <button type="button" class="text-button" @click="removeSubscriber(subscriber.email)">
                Odstranit
              </button>
            </div>
          </div>
          <p v-else class="empty-state">Zatial tu nie su ziadne emaily.</p>
        </section>

        <section class="editor-section danger-zone">
          <div>
            <p class="eyebrow">Databaza</p>
            <h2>Obnovit seed data</h2>
            <p>Obnova nahradi obsah pociatocnymi datami.</p>
          </div>
          <button type="button" class="danger-button" @click="resetDatabase">Obnovit</button>
        </section>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  createEventDraft,
  deleteSubscriber,
  loadContent,
  loadSubscribers,
  resetContent,
  saveContent
} from '@/services/cnkDb'

defineEmits(['open-site'])

const storedPassword = window.sessionStorage.getItem('cnk-admin-password') || ''
const isAuthenticated = ref(Boolean(storedPassword))
const isLoading = ref(true)
const settings = ref({})
const events = ref([])
const selectedEventId = ref('')
const draft = ref(null)
const message = ref('')
const password = ref('')
const loginError = ref('')
const subscribers = ref([])
const adminPassword = ref(storedPassword)

const sortedEvents = computed(() => {
  return [...events.value].sort((first, second) => {
    const firstValue = `${first.date || '0000-00-00'}T${first.time || '00:00'}`
    const secondValue = `${second.date || '0000-00-00'}T${second.time || '00:00'}`
    const dateResult = secondValue.localeCompare(firstValue)

    if (first.date && second.date && dateResult !== 0) {
      return dateResult
    }

    return (Number(second.number) || 0) - (Number(first.number) || 0)
  })
})

const tagsText = computed(() => {
  return draft.value?.tags?.join(', ') || ''
})

onMounted(() => {
  if (isAuthenticated.value) {
    loadAdminContent().catch(() => {
      logout()
      isLoading.value = false
    })
    return
  }

  isLoading.value = false
})

function login() {
  loginError.value = ''
  adminPassword.value = password.value

  loadAdminContent()
    .then(() => {
      window.sessionStorage.setItem('cnk-admin-password', adminPassword.value)
      isAuthenticated.value = true
      password.value = ''
    })
    .catch(() => {
      adminPassword.value = ''
      isLoading.value = false
      loginError.value = 'Nespravne heslo alebo nedostupne API.'
    })
}

function logout() {
  window.sessionStorage.removeItem('cnk-admin-password')
  isAuthenticated.value = false
  password.value = ''
  adminPassword.value = ''
  loginError.value = ''
}

async function loadAdminContent() {
  isLoading.value = true
  const content = await loadContent()
  settings.value = clone(content.settings)
  events.value = clone(content.events)
  subscribers.value = await loadSubscribers(adminPassword.value)
  selectEvent(sortedEvents.value[0]?.id)
  isLoading.value = false
}

function clone(value) {
  return JSON.parse(JSON.stringify(value))
}

function selectEvent(eventId) {
  const event = events.value.find((item) => item.id === eventId)

  selectedEventId.value = eventId || ''
  draft.value = event ? clone(event) : null
  message.value = ''
}

function addEvent() {
  const nextNumber = Math.max(0, ...events.value.map((event) => Number(event.number) || 0)) + 1
  const event = createEventDraft(nextNumber)

  events.value = [event, ...events.value.map((item) => ({ ...item, featured: false }))]
  selectEvent(event.id)
  message.value = 'Novy event je pripraveny. Po upravach ho uloz.'
}

async function saveCurrent() {
  if (!draft.value) {
    await saveContent(settings.value, events.value, adminPassword.value)
    message.value = 'Zmeny ulozene.'
    return
  }

  const normalizedDraft = normalizeEvent(draft.value)
  let nextEvents = events.value.filter((event) => event.id !== normalizedDraft.id)

  if (normalizedDraft.featured) {
    nextEvents = nextEvents.map((event) => ({ ...event, featured: false }))
  }

  events.value = [normalizedDraft, ...nextEvents]
  await saveContent(settings.value, events.value, adminPassword.value)
  selectEvent(normalizedDraft.id)
  message.value = 'Zmeny ulozene do API/databazy.'
}

async function deleteCurrent() {
  if (!draft.value || !window.confirm('Naozaj vymazat tento event?')) {
    return
  }

  events.value = events.value.filter((event) => event.id !== draft.value.id)

  if (!events.value.some((event) => event.featured) && events.value[0]) {
    events.value[0].featured = true
  }

  await saveContent(settings.value, events.value, adminPassword.value)
  selectEvent(sortedEvents.value[0]?.id)
  message.value = 'Event bol vymazany.'
}

async function resetDatabase() {
  if (!window.confirm('Obnovit obsah na pociatocne data?')) {
    return
  }

  await resetContent(adminPassword.value)
  await loadAdminContent()
  message.value = 'Databaza bola resetovana.'
}

async function removeSubscriber(email) {
  await deleteSubscriber(email, adminPassword.value)
  subscribers.value = await loadSubscribers(adminPassword.value)
}

function exportSubscribers() {
  const rows = ['email,createdAt']
  subscribers.value.forEach((subscriber) => {
    rows.push(`${subscriber.email},${subscriber.createdAt || ''}`)
  })

  const blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')

  link.href = url
  link.download = 'cnk-subscribers.csv'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

function formatTimestamp(value) {
  if (!value) {
    return 'Neznamy datum'
  }

  const date = new Date(value)
  const pad = (part) => String(part).padStart(2, '0')

  return `${pad(date.getDate())}.${pad(date.getMonth() + 1)}.${date.getFullYear()} ${pad(
    date.getHours()
  )}:${pad(date.getMinutes())}`
}

function normalizeEvent(event) {
  const isTba = Boolean(event.isTba)

  return {
    ...event,
    isTba,
    number: Number(event.number) || 0,
    talks: isTba
      ? []
      : (event.talks || []).filter((talk) => talk.title || talk.speaker || talk.abstract),
    demoPoints: isTba ? [] : (event.demoPoints || []).filter(Boolean),
    tags: (event.tags || []).filter(Boolean)
  }
}

function updateTags(inputEvent) {
  draft.value.tags = inputEvent.target.value
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean)
}

function addTalk() {
  draft.value.talks.push({
    title: '',
    speaker: '',
    abstract: ''
  })
}

function removeTalk(index) {
  draft.value.talks.splice(index, 1)
}

function addDemoPoint() {
  draft.value.demoPoints.push('')
}

function removeDemoPoint(index) {
  draft.value.demoPoints.splice(index, 1)
}
</script>

<style scoped>
.admin-login {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 24px;
  background:
    linear-gradient(135deg, rgba(72, 252, 250, 0.12), transparent 46%),
    #050a30;
  color: #162329;
}

.login-box {
  display: grid;
  gap: 14px;
  width: min(100%, 420px);
  padding: 30px;
  border: 2px solid #48fcfa;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 0 40px rgba(72, 252, 250, 0.18);
}

.login-box p {
  margin: 0;
  color: #4d5a60;
  line-height: 1.55;
}

.login-error {
  color: #b5332a !important;
  font-weight: 800;
}

.admin-page {
  min-height: 100vh;
  background: #eef1f0;
  color: #162329;
}

.admin-topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  gap: 20px;
  align-items: center;
  justify-content: space-between;
  padding: 18px clamp(18px, 4vw, 48px);
  border-bottom: 1px solid rgba(22, 35, 41, 0.12);
  background: rgba(238, 241, 240, 0.94);
  backdrop-filter: blur(14px);
}

.eyebrow {
  margin: 0 0 8px;
  color: #007c7a;
  font-size: 0.78rem;
  font-weight: 900;
  letter-spacing: 0;
  text-transform: uppercase;
}

h1,
h2,
p {
  overflow-wrap: anywhere;
}

h1 {
  margin: 0;
  font-size: clamp(1.8rem, 4vw, 3.2rem);
  letter-spacing: 0;
}

h2 {
  margin: 0;
  font-size: 1.35rem;
  letter-spacing: 0;
}

.top-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

button,
input,
select,
textarea {
  font: inherit;
}

button {
  border-radius: 8px;
  font-weight: 800;
  cursor: pointer;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.48;
}

.primary-button,
.ghost-button,
.danger-button,
.icon-button {
  min-height: 42px;
  border: 0;
  padding: 0 14px;
}

.primary-button {
  background: #162329;
  color: #ffffff;
}

.ghost-button {
  border: 1px solid rgba(22, 35, 41, 0.18);
  background: #ffffff;
  color: #162329;
}

.danger-button {
  background: #b5332a;
  color: #ffffff;
}

.icon-button {
  width: 42px;
  padding: 0;
  background: #007c7a;
  color: #ffffff;
  font-size: 1.4rem;
  line-height: 1;
}

.text-button {
  border: 0;
  background: transparent;
  color: #b5332a;
  padding: 0;
}

.admin-loading {
  display: grid;
  min-height: 70vh;
  place-items: center;
  font-weight: 800;
}

.admin-layout {
  display: grid;
  grid-template-columns: minmax(240px, 340px) minmax(0, 1fr);
  gap: 22px;
  padding: 22px clamp(18px, 4vw, 48px) 48px;
}

.event-list {
  position: sticky;
  top: 112px;
  align-self: start;
  display: grid;
  gap: 10px;
  max-height: calc(100vh - 136px);
  overflow: auto;
  padding: 16px;
  border: 1px solid rgba(22, 35, 41, 0.12);
  border-radius: 8px;
  background: #ffffff;
}

.list-header {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.event-list > button:not(.icon-button) {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 4px 10px;
  width: 100%;
  padding: 12px;
  border: 1px solid rgba(22, 35, 41, 0.12);
  background: #f8f8f6;
  color: #162329;
  text-align: left;
}

.event-list > button.active {
  border-color: #007c7a;
  background: #e3f4ef;
}

.event-list span {
  color: #007c7a;
  font-weight: 900;
}

.event-list small {
  grid-column: 2;
  color: #5e6d73;
  font-weight: 800;
}

.editor {
  display: grid;
  gap: 18px;
}

.status-message {
  padding: 14px 16px;
  border-radius: 8px;
  background: #e3f4ef;
  color: #0b5f5b;
  font-weight: 800;
}

.editor-section {
  padding: clamp(18px, 3vw, 28px);
  border: 1px solid rgba(22, 35, 41, 0.12);
  border-radius: 8px;
  background: #ffffff;
}

.section-title {
  margin-bottom: 18px;
}

.split-title {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  justify-content: space-between;
}

.form-grid {
  display: grid;
  gap: 16px;
}

.two-columns {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.full-span {
  grid-column: 1 / -1;
}

label {
  display: grid;
  gap: 8px;
  color: #4d5a60;
  font-size: 0.9rem;
  font-weight: 800;
}

input,
select,
textarea {
  width: 100%;
  border: 1px solid rgba(22, 35, 41, 0.18);
  border-radius: 8px;
  background: #ffffff;
  color: #162329;
  padding: 11px 12px;
  font-weight: 600;
}

textarea {
  resize: vertical;
}

.checkbox-row {
  grid-template-columns: auto 1fr;
  align-items: center;
}

.checkbox-row input {
  width: 18px;
  height: 18px;
}

.repeaters {
  display: grid;
  gap: 14px;
}

.repeater {
  display: grid;
  gap: 14px;
  padding: 16px;
  border: 1px solid rgba(22, 35, 41, 0.12);
  border-radius: 8px;
  background: #f8f8f6;
}

.repeater-header,
.demo-row {
  display: flex;
  gap: 14px;
  align-items: center;
  justify-content: space-between;
}

.demo-editor {
  display: grid;
  gap: 10px;
}

.demo-row input {
  flex: 1;
}

.subscriber-list {
  display: grid;
  gap: 10px;
}

.subscriber-row {
  display: flex;
  gap: 16px;
  align-items: center;
  justify-content: space-between;
  padding: 14px;
  border: 1px solid rgba(22, 35, 41, 0.12);
  border-radius: 8px;
  background: #f8f8f6;
}

.subscriber-row div {
  display: grid;
  gap: 4px;
}

.subscriber-row span,
.empty-state {
  color: #5e6d73;
  font-weight: 700;
}

.tba-note p:not(.eyebrow) {
  max-width: 720px;
  margin: 10px 0 0;
  color: #5e6d73;
  line-height: 1.55;
}

.danger-zone {
  display: flex;
  gap: 20px;
  align-items: center;
  justify-content: space-between;
}

.danger-zone p:not(.eyebrow) {
  margin: 8px 0 0;
  color: #5e6d73;
}

@media (max-width: 980px) {
  .admin-layout,
  .two-columns {
    grid-template-columns: 1fr;
  }

  .event-list {
    position: static;
    max-height: 420px;
  }
}

@media (max-width: 660px) {
  .admin-topbar,
  .split-title,
  .danger-zone,
  .repeater-header,
  .demo-row {
    align-items: stretch;
    flex-direction: column;
  }

  .top-actions,
  .top-actions button {
    width: 100%;
  }
}
</style>
