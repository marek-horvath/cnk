import { defaultEvents, defaultSettings } from '@/data/defaultContent'

const API_BASE_URL =
  process.env.VUE_APP_API_BASE_URL || 'https://cnk-api.167.233.132.16.sslip.io/api'
const DB_NAME = 'cloud-native-kosice-content'
const DB_VERSION = 4
const EVENTS_STORE = 'events'
const SETTINGS_STORE = 'settings'
const SETTINGS_ID = 'site'
const LOAD_TIMEOUT_MS = 1800

let databasePromise

function clone(value) {
  return JSON.parse(JSON.stringify(value))
}

function requestToPromise(request) {
  return new Promise((resolve, reject) => {
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

function transactionDone(transaction) {
  return new Promise((resolve, reject) => {
    transaction.oncomplete = () => resolve()
    transaction.onerror = () => reject(transaction.error)
    transaction.onabort = () => reject(transaction.error)
  })
}

function putDefaultContent(transaction) {
  const eventsStore = transaction.objectStore(EVENTS_STORE)
  const settingsStore = transaction.objectStore(SETTINGS_STORE)

  eventsStore.clear()
  settingsStore.clear()
  settingsStore.put(clone(defaultSettings))
  defaultEvents.forEach((event) => {
    eventsStore.put(clone(event))
  })
}

function openDatabase() {
  if (databasePromise) {
    return databasePromise
  }

  databasePromise = new Promise((resolve, reject) => {
    const request = window.indexedDB.open(DB_NAME, DB_VERSION)

    request.onupgradeneeded = () => {
      const database = request.result
      const transaction = request.transaction

      if (!database.objectStoreNames.contains(EVENTS_STORE)) {
        database.createObjectStore(EVENTS_STORE, { keyPath: 'id' })
      }

      if (!database.objectStoreNames.contains(SETTINGS_STORE)) {
        database.createObjectStore(SETTINGS_STORE, { keyPath: 'id' })
      }

      if (transaction) {
        putDefaultContent(transaction)
      }
    }

    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })

  return databasePromise
}

function sortEvents(events) {
  return [...events].sort((first, second) => {
    const firstValue = `${first.date || '0000-00-00'}T${first.time || '00:00'}`
    const secondValue = `${second.date || '0000-00-00'}T${second.time || '00:00'}`
    const dateResult = secondValue.localeCompare(firstValue)

    if (first.date && second.date && dateResult !== 0) {
      return dateResult
    }

    return (Number(second.number) || 0) - (Number(first.number) || 0)
  })
}

function fallbackContent() {
  return {
    settings: clone(defaultSettings),
    events: sortEvents(defaultEvents)
  }
}

function withTimeout(promise, timeoutMs = LOAD_TIMEOUT_MS) {
  return Promise.race([
    promise,
    new Promise((_, reject) => {
      window.setTimeout(() => reject(new Error('Request timed out')), timeoutMs)
    })
  ])
}

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.adminPassword ? { 'X-Admin-Password': options.adminPassword } : {}),
      ...(options.headers || {})
    }
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `API request failed: ${response.status}`)
  }

  if (response.status === 204) {
    return null
  }

  return response.json()
}

async function seedIfEmpty() {
  const database = await openDatabase()
  const readTransaction = database.transaction(EVENTS_STORE, 'readonly')
  const count = await requestToPromise(readTransaction.objectStore(EVENTS_STORE).count())

  if (count > 0) {
    return
  }

  const transaction = database.transaction([EVENTS_STORE, SETTINGS_STORE], 'readwrite')
  putDefaultContent(transaction)
  await transactionDone(transaction)
}

async function loadContentFromLocalFallback() {
  await seedIfEmpty()

  const database = await openDatabase()
  const transaction = database.transaction([EVENTS_STORE, SETTINGS_STORE], 'readonly')
  const eventsRequest = transaction.objectStore(EVENTS_STORE).getAll()
  const settingsRequest = transaction.objectStore(SETTINGS_STORE).get(SETTINGS_ID)

  const [events, settings] = await Promise.all([
    requestToPromise(eventsRequest),
    requestToPromise(settingsRequest)
  ])

  return {
    settings: settings || clone(defaultSettings),
    events: sortEvents(events)
  }
}

export async function loadContent() {
  try {
    const content = await withTimeout(apiRequest('/content'))
    return {
      settings: content.settings || clone(defaultSettings),
      events: sortEvents(content.events || [])
    }
  } catch (error) {
    console.warn('Using local CNK content because API failed.', error)
  }

  try {
    return await loadContentFromLocalFallback()
  } catch (error) {
    console.warn('Using bundled CNK defaults because local fallback failed.', error)
    return fallbackContent()
  }
}

export async function saveContent(settings, events, adminPassword) {
  return apiRequest('/content', {
    method: 'PUT',
    adminPassword,
    body: JSON.stringify({
      settings,
      events: sortEvents(events)
    })
  })
}

export async function resetContent(adminPassword) {
  return apiRequest('/reset', {
    method: 'POST',
    adminPassword
  })
}

export async function loadSubscribers(adminPassword) {
  return apiRequest('/subscribers', {
    adminPassword
  })
}

export async function saveSubscriber(email) {
  const result = await apiRequest('/subscribers', {
    method: 'POST',
    body: JSON.stringify({ email })
  })

  return result.email
}

export async function deleteSubscriber(email, adminPassword) {
  const encodedEmail = encodeURIComponent(email)
  return apiRequest(`/subscribers/${encodedEmail}`, {
    method: 'DELETE',
    adminPassword
  })
}

export function createEventDraft(nextNumber) {
  return {
    id: `meetup-${Date.now()}`,
    number: nextNumber,
    title: `Cloud Native Kosice Meetup #${nextNumber}`,
    subtitle: 'Novy meetup',
    status: 'upcoming',
    featured: true,
    isTba: false,
    date: '',
    time: '17:00',
    venue: 'Aurora (5. floor), TUKE',
    address: 'Letna 9, Kosice',
    intro: '',
    summary: '',
    talks: [
      {
        title: '',
        speaker: '',
        abstract: ''
      },
      {
        title: '',
        speaker: '',
        abstract: ''
      }
    ],
    demoPoints: [''],
    tags: []
  }
}
