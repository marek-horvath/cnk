# CNK API

Male Python stdlib API pre Cloud Native Kosice.

Endpointy:

- `GET /api/health`
- `GET /api/content`
- `PUT /api/content` with `X-Admin-Password`
- `POST /api/reset` with `X-Admin-Password`
- `POST /api/subscribers`
- `GET /api/subscribers` with `X-Admin-Password`
- `DELETE /api/subscribers/{email}` with `X-Admin-Password`

Konfiguracia:

```bash
CNK_HOST=127.0.0.1
CNK_PORT=3001
CNK_DATA_DIR=/var/lib/cnk-api
CNK_DB_PATH=/var/lib/cnk-api/cnk.sqlite3
CNK_ADMIN_PASSWORD=...
```

Nasadenie na VPS:

- systemd service: `cnk-api`
- interne API: `http://127.0.0.1:3005/api`
- verejne API: `https://cnk-api.167.233.132.16.sslip.io/api`
- SQLite DB: `/var/lib/cnk-api/cnk.sqlite3`
- aplikacia: `/opt/cnk-api`
- logy: `journalctl -u cnk-api -n 100 --no-pager`
