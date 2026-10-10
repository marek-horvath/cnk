# Cloud Native Kosice

## Spustenie cez Docker na Windows

Predpokladom je nainstalovany a spusteny Docker Desktop. Po naklonovani
repozitara spustite dvojklikom `start.bat`. Skript pri prvom spusteni vytvori
lokalny `.env` s nahodnym admin heslom, zostavi kontajnery, pocka na ich
pripravenost a otvori aplikaciu na http://localhost:8080/.

Admin rozhranie je na http://localhost:8080/admin. Vygenerovane heslo najdete
v lokalnom subore `.env`, ktory sa neuklada do Git repozitara.

Aplikaciu zastavite dvojklikom na `stop.bat`. Databaza ostane zachovana v
Docker volume `cnk_data`. Na vymazanie dat nepouzivajte `docker compose down
-v`, pokial ich nechcete umyselne odstranit.

Zdrojovy kod je pripojeny do kontajnerov a frontend podporuje hot reload. Po
beznej zmene kodu preto nie je potrebny rebuild. Po zmene zavislosti alebo
Docker konfiguracie znovu spustite `start.bat`, pripadne:

```bash
docker compose up -d --build
```

Stav a logy je mozne skontrolovat prikazmi `docker compose ps` a
`docker compose logs -f`.

## Povodne lokalne spustenie

### Instalacia
```
npm install
```

### Development server s hot reloadom
```
npm run serve
```

### Produkcny build
```
npm run build
```

### Kontrola kodu
```
npm run lint
```
