<template>
  <div>
    <!-- Navigation (Dark Background) -->
    <nav class="nav">
      <div class="nav-logo">
        <img src="@/assets/logo.png" alt="Logo" />
      </div>
      <ul class="nav-menu">
        <li><a href="#hero">Home</a></li>
        <li><a href="#sessions">Sessions</a></li>
        <li><a href="#speaker">Speaker</a></li>
        <li><a href="#location">Location</a></li>
      </ul>
      <div class="nav-mobile">
        <i class="fa fa-bars"></i>
      </div>
    </nav>

    <!-- Hero Section (Dark Background) -->
    <section id="hero" class="hero">
      <div class="hero-container">
        <h2>Cloud Native Kosice Meetup #7 – Kicking Off 2025 in Style!</h2>
        <p class="hero-date">Next Meetup: <strong>March 14, 2025 (17:00 – 21:00)</strong></p>
        <p class="hero-place">Aurora, Letná 9, TUKE, Košice</p>
        <p class="hero-description">
          Join us for an exciting evening diving deep into API security with hands-on demos, live configurations, and expert discussions. Whether you’re a seasoned professional or just getting started with cloud-native technologies, there’s something for everyone!
        </p>
      </div>
    </section>

    <!-- Sessions Section (White Background) -->
    <section id="sessions" class="sessions">
      <div class="sessions-container">
        <h2>What to Expect</h2>
        <p>
          💥 Special guest Immanuel Fodor, Product Manager at Traefik Labs, brings his unique know-how to Košice!
          <br />
          🛡️🔥 Get ready for an extra deep dive into API security, hands-on demos, live configurations, and discussions with experts!
        </p>
        <ul class="session-list">
          <li>
            <strong>Session 1:</strong> Deep dive into security principles, attack vectors, and defense strategies.
          </li>
          <li>
            <strong>Session 2:</strong> Practical walkthroughs with demos, live configurations, and best practices.
          </li>
        </ul>
        <h3>You Will Learn To:</h3>
        <ul class="session-list">
          <li>Protect APIs from OWASP Top 10 threats and emerging risks</li>
          <li>Deploy a cloud-native WAF for lightweight yet effective protection</li>
          <li>Integrate security into API governance for seamless compliance</li>
          <li>Scale APIs securely without sacrificing performance</li>
          <li>Configure everything as code with GitOps principles</li>
        </ul>
      </div>
    </section>

    <!-- Speaker Section (White Background) -->
    <section id="speaker" class="speaker">
      <div class="speaker-container">
        <h2>Speaker Bio: Immanuel Fodor</h2>
        <p>
          👨‍💻🎙️ Immanuel Fodor, Product Manager at Traefik Labs, is a Certified Kubernetes Administrator who lives and breathes DevOps.
          With 14 years of experience, he excels at simplifying complex engineering concepts and making them accessible.
        </p>
        <p>
          Don’t miss this chance to level up your cloud-native skills and leave with the knowledge to secure your APIs immediately.
          Meetup will be in English.
        </p>
      </div>
    </section>

    <!-- Location Section (Dark Background) -->
    <section id="location" class="location">
      <div class="location-container">
        <h2>Location & Time</h2>
        <p>
          Aurora, Letná 9, TUKE, Košice
          <br />
          Duration: 4 hours
          <br />
          Meetup will be in English.
        </p>
        <p>
          #CloudNativeKosice #APIsecurity #TraefikLabs #Meetup #GitOps
        </p>
      </div>
    </section>

    <!-- Footer (Dark Background) -->
    <footer class="footer">
      <div class="footer-container">
        <div class="footer-left">
          <a href="https://marek-horvath.github.io/portfolio/" target="_blank" rel="noopener noreferrer">
            Created by Marek Horvath
          </a>
        </div>
        <div class="footer-right">
          <i class="fa fa-linkedin"></i>
          <i class="fa fa-facebook"></i>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
// Vue logic can be added here if needed.
</script>

<style>
/* 1) Import Mokoto font (Place Mokoto.ttf in src/assets/fonts/) */
@font-face {
  font-family: 'Mokoto';
  src: url('@/assets/fonts/Mokoto.ttf') format('truetype');
  font-weight: normal;
  font-style: normal;
}

/* 2) Global Settings */
body {
  margin: 0;
  font-family: 'Mokoto', Arial, sans-serif;
  background-color: #050a30; /* Dark background globally */
  color: #48fcfa; /* Light text on dark background */
}

a {
  text-decoration: none;
  color: inherit;
}

img {
  max-width: 100%;
  display: block;
}

ul {
  margin: 0;
  padding: 0;
}

li {
  list-style: none;
}

/* 3) Navigation */
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
  height: 40px;
}

.nav-menu {
  display: flex;
  gap: 30px;
}

.nav-menu li {
  cursor: pointer;
  font-weight: 500;
}

.nav-mobile {
  display: none;
}

/* 4) Hero Section (Dark Background) */
.hero {
  background-color: #050a30;
  padding: 60px 10%;
  text-align: center;
}

.hero-container {
  max-width: 800px;
  margin: 0 auto;
}

.hero h2 {
  margin: 0;
  font-size: 2.5em;
  margin-bottom: 20px;
}

.hero-date,
.hero-place {
  font-size: 1.2em;
  margin-bottom: 10px;
  font-weight: bold;
}

.hero-description {
  margin-top: 20px;
  line-height: 1.6;
}

/* 5) Sessions Section (White Background) */
.sessions {
  background-color: #ffffff;
  color: #050a30;
  padding: 60px 10%;
}

.sessions-container {
  max-width: 900px;
  margin: 0 auto;
  text-align: center;
}

.sessions-container h2 {
  font-size: 2em;
  margin-bottom: 30px;
}

.session-list {
  margin: 20px 0;
  padding-left: 20px;
  text-align: left;
}

/* 6) Speaker Section (White Background) */
.speaker {
  background-color: #ffffff;
  color: #050a30;
  padding: 60px 10%;
}

.speaker-container {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

.speaker-container h2 {
  font-size: 2em;
  margin-bottom: 20px;
}

/* 7) Location Section (Dark Background) */
.location {
  background-color: #050a30;
  padding: 60px 10%;
  text-align: center;
}

.location-container {
  max-width: 800px;
  margin: 0 auto;
}

.location h2 {
  font-size: 2em;
  margin-bottom: 20px;
}

/* 8) Footer */
.footer {
  background-color: #050a30;
  padding: 20px 10%;
  color: #48fcfa;
}

.footer-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
}

.footer-left a {
  font-size: 0.9em;
}

.footer-right i {
  font-size: 1.5em;
  margin: 0 5px;
  cursor: pointer;
}

/* 9) Responsiveness */
@media (max-width: 768px) {
  .nav-menu {
    display: none;
  }
  .nav-mobile {
    display: block;
  }
  .footer-container {
    flex-direction: column;
    text-align: center;
  }
}
</style>
