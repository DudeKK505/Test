# WMS-Plus
Struktura plików:

/opt/wms-overlay/
├── .env                <-- Hasła do WMS, klucz SQLCipher (chmod 600)
├── db/
│   └── wms_data.db     <-- Zaszyfrowany plik SQLite (poza webroot!)
├── scraper/            <-- Daemon
│   ├── main.py         <-- Pętla główna (zarządca modułów)
│   ├── logger.py       <-- Logowanie błędów do pliku
│   └── modules/        <-- Moduły per konkretne zadanie
│       ├── orders.py
│       ├── stocks.py
│       └── shipments.py
├── web/                <-- To, co widzi Nginx/Apache
│   ├── index.php       <-- Dashboard
│   ├── api.php         <-- Endpoint dla AJAX (pobiera z DB)
│   └── assets/         <-- JS, CSS (Vanilla JS + Ajax)
└── config/
    └── nginx.conf      <-- Whitelista IP i SSL

