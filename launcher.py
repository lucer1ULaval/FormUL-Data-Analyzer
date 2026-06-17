import sys
import os
import threading
import time
import urllib.request

if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
    work_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    work_dir = base_dir

os.chdir(work_dir)
sys.path.insert(0, base_dir)

_new_windows = []
_lock = threading.Lock()

def demander_nouvelle_fenetre():
    with _lock:
        _new_windows.append(True)

import builtins
builtins._demander_nouvelle_fenetre = demander_nouvelle_fenetre

def demarrer_dash():
    from app import app
    app.run(debug=False, host='127.0.0.1', port=8050)

threading.Thread(target=demarrer_dash, daemon=True).start()

# Attendre que Dash soit vraiment prêt
def attendre_serveur(timeout=30):
    for _ in range(timeout * 10):
        try:
            urllib.request.urlopen('http://127.0.0.1:8050', timeout=1)
            return True
        except Exception:
            time.sleep(0.1)
    return False

attendre_serveur()

import webview

def verifier_nouvelles_fenetres():
    while True:
        time.sleep(0.3)
        with _lock:
            if _new_windows:
                _new_windows.clear()
                webview.create_window(
                    'FormUL Analyzer — Vue détachée',
                    'http://127.0.0.1:8050/view',
                    width=1200, height=800,
                    resizable=True,
                )

threading.Thread(target=verifier_nouvelles_fenetres, daemon=True).start()

webview.create_window(
    'FormUL Analyzer',
    'http://127.0.0.1:8050',
    width=1400, height=900,
    min_size=(900, 600),
    resizable=True,
)

webview.start()