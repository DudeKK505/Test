import os
import sys
import webview
import threading
import uuid
import logging
import requests
import asyncio
import json
import sqlite3
import ql_scraper
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect
from playwright.sync_api import sync_playwright 
import main
import test

# --- KONFIGURACJA LOGOWANIA ---
if not os.path.exists('logs'): 
    os.makedirs('logs')

logging.basicConfig(
    level=logging.INFO, 
    filename="logs/app_log.log", 
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("app_main")

if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
    app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'), static_folder=os.path.join(basedir, 'static'))
else:
    app = Flask(__name__)

tasks = {}
app_state = {"works": False, "found": False}
user_name = 'Nieznany'

# [TUTAJ TWOJE FUNKCJE run_stealth_auth, root, perform_login POZOSTAJĄ DOKŁADNIE TAKIE SAME]
# Wklej je bez zmian...

@app.route('/start_tpt_scrape', methods=['POST'])
def start_tpt_scrape():
    # Zabezpieczamy tworzenie tabeli timeoutem i WAL
    try:
        with sqlite3.connect('ship.db', timeout=30) as conn:
            conn.execute('PRAGMA journal_mode=WAL;')
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tpt (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    time TEXT,
                    count INTEGER
                )
            ''')
            conn.commit()
    except Exception as e:
        logger.error(f"Błąd inicjalizacji bazy: {e}")

    data = request.get_json(force=True)
    schedule = data.get('schedule', [])

    logger.info(f"Otrzymano schedule do przetworzenia: {schedule}")

    try:
        # Czekamy na zakończenie scrapowania
        asyncio.run(test.uruchom_tpt_rownolegle(schedule))
        
        results = []
        total_sum = 0
        
        # Otwieramy bazę z timeoutem, żeby nie było błędu Locked
        with sqlite3.connect('ship.db', timeout=30) as conn:
            conn.execute('PRAGMA journal_mode=WAL;')
            cursor = conn.cursor()
            
            for x in schedule:
                # Bierzemy najświeższy wpis dla danej daty (w razie duplikatów)
                cursor.execute("SELECT count FROM tpt WHERE time=? AND date=? ORDER BY id DESC LIMIT 1", (x['time'], x['date']))
                row = cursor.fetchone()
                
                # ZABEZPIECZENIE: Jeśli row to None (nic nie zapisano)
                if row is not None:
                    count_val = int(row[0])
                else:
                    count_val = 0
                    logger.warning(f"Brak danych w bazie dla {x['date']} {x['time']} po scrapowaniu!")
                
                # POPRAWKA: Dodano 'count', żeby Twój JS mógł to odczytać
                results.append({
                    "date": x['date'],
                    "time": x['time'],
                    "count": count_val 
                })
                total_sum += count_val
        
        return jsonify({
            'status': 'completed', 
            'result': {
                'schedule': results,  
                'total': total_sum    
            }
        })
    except Exception as e:
        logger.error(f"BŁĄD KRYTYCZNY API /start_tpt_scrape: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

# [RESZTA TWOICH ENDPOINTÓW BEZ ZMIAN (logout, start_scrape, etc.)]
