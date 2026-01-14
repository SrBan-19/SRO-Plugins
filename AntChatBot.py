from phBot import *
import ctypes, time, QtBind, os, subprocess, urllib.request, json

# --- CONFIGURAÇÕES DE VERSÃO E ATUALIZAÇÃO ---
_n = 'Trade Hide Premium Pro'
_v = '25.6' 
_update_url = "https://raw.githubusercontent.com/SrBan-19/SRO-Plugins/refs/heads/main/AntChatBot.py"
_plugin_path = os.path.join(os.getcwd(), "Plugins", "AntChatBot.py")

def check_for_updates():
    try:
        req = urllib.request.Request(_update_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            remote_code = response.read().decode('utf-8')
            if "_v = '" in remote_code:
                remote_version = remote_code.split("_v = '")[1].split("'")[0]
                if remote_version > _v:
                    log(f"[{_n}] Nova atualização: {remote_version}. Baixando...")
                    with open(_plugin_path, "w", encoding='utf-8') as f:
                        f.write(remote_code)
                    log(f"[{_n}] Plugin atualizado! Reinicie o phBot.")
                    return True
    except: pass
    return False

check_for_updates()

# --- VARIÁVEIS GLOBAIS ---
_u32 = ctypes.windll.user32
_u = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS1h7zFy9nH68Dij7bAJutZ0DuYJj1zV9jet8rhAnAMqAcKhmrHoctKjd5uToJor1zV291zCUi4cyrh/pub?output=csv"
_folder_path = os.path.join(os.getcwd(), "Plugins", "TradeHide_Configs")
if not os.path.exists(_folder_path): os.makedirs(_folder_path)

def get_hwid():
    try:
        c = subprocess.check_output('vol c:', shell=True).decode('cp850')
        return c.split()[-1].replace('-', '')
    except: return "ID_ERR"

_mid = get_hwid()
_auth = False
try:
    req = urllib.request.Request(_u, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=5) as r:
        if _mid in r.read().decode('utf-8'): _auth = True
except: pass

# --- INTERFACE ---
gui = QtBind.init(__name__, _n)
QtBind.createLabel(gui, f"HWID: {_mid} | v{_v}", 340, 5)
btnCapture = QtBind.createButton(gui, "btnCapture_clicked", " Capturar Janela ", 15, 25)
txtNewChar = QtBind.createLineEdit(gui, "", 140, 25, 90, 20)
txtNewRes = QtBind.createLineEdit(gui, "1366x768", 240, 25, 80, 20)
btnAdd = QtBind.createButton(gui, "btnAdd_clicked", " + ADICIONAR ", 330, 23)
lstChars = QtBind.createList(gui, 15, 80, 210, 110)
lstLogs = QtBind.createList(gui, 235, 80, 230, 110)
btnToggle = QtBind.createButton(gui, "btnToggle_clicked", " ATIVAR/DESATIVAR ", 15, 195)
btnDel = QtBind.createButton(gui, "btnDel_clicked", " REMOVER ", 15, 220)
btnTest = QtBind.createButton(gui, "btnTest_clicked", " TESTAR CLIQUE ", 235, 195)

def _log(m): QtBind.append(gui, lstLogs, f"[{time.strftime('%H:%M:%S')}] {m}")

# --- LÓGICA DE CLIQUE CALIBRADA ---
def _process_click(entry_str):
    try:
        if "[OFF]" in entry_str: return
        parts = entry_str.split("] ")[1]
        name, res = parts.split(" | ")
        rw, rh = map(int, res.split('x'))
        
        # CALIBRAÇÃO EXATA: 
        # Para 1366 -> 1366 * 0.46852 = 640
        # Para 768  -> 768 * 0.54557 = 419
        cx, cy = int(rw * 0.46852), int(rh * 0.54557)
        
        hw = find_sro(f"[NewEvolust] {name}")
        if hw:
            # Mover mouse real para conferência visual
            rect = ctypes.wintypes.RECT()
            _u32.GetWindowRect(hw, ctypes.byref(rect))
            _u32.SetCursorPos(rect.left + cx, rect.top + cy)
            
            # Envio do clique
            lp = (cy << 16) | (cx & 0xFFFF)
            _u32.PostMessageW(hw, 0x0201, 0x0001, lp) # Mouse Down
            time.sleep(0.1)
            _u32.PostMessageW(hw, 0x0202, 0, lp)      # Mouse Up
            _log(f"✔ Clique em ({cx}, {cy}) enviado para {name}")
    except: pass

def handle_joymax(opcode, data):
    if opcode == 0x190A:
        if not _auth: return True
        time.sleep(0.1) 
        for entry in QtBind.getItems(gui, lstChars):
            if "[ON]" in entry:
                _process_click(entry)
    return True

# --- FUNÇÕES DE SISTEMA ---
def find_sro(t):
    h = None
    def _e(hw, lp):
        nonlocal h
        ln = _u32.GetWindowTextLengthW(hw)
        if ln > 0:
            b = ctypes.create_unicode_buffer(ln + 1)
            _u32.GetWindowTextW(hw, b, ln + 1)
            if t in b.value: h = hw; return False
        return True
    _u32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(_e), 0)
    return h

def load_accounts():
    QtBind.clear(gui, lstChars)
    if os.path.exists(_folder_path):
        for f in os.listdir(_folder_path):
            if f.endswith(".json"):
                with open(os.path.join(_folder_path, f), "r") as file:
                    d = json.load(file)
                    st = "[ON]" if d.get("enabled", True) else "[OFF]"
                    QtBind.append(gui, lstChars, f"{st} {d['name']} | {d['res']}")

def btnAdd_clicked():
    n, r = QtBind.text(gui, txtNewChar), QtBind.text(gui, txtNewRes).lower()
    if n and "x" in r:
        with open(os.path.join(_folder_path, f"{n}.json"), "w") as f:
            json.dump({"name": n, "res": r, "enabled": True}, f)
        load_accounts()
        _log(f"💾 {n} salvo.")

def btnTest_clicked():
    sel = QtBind.text(gui, lstChars)
    if sel: _process_click(sel)

def btnCapture_clicked():
    hw = find_sro("[NewEvolust]")
    if hw:
        ln = _u32.GetWindowTextLengthW(hw)
        b = ctypes.create_unicode_buffer(ln + 1)
        _u32.GetWindowTextW(hw, b, ln + 1)
        if " " in b.value: 
            name = b.value.split(" ", 1)[1]
            QtBind.setText(gui, txtNewChar, name)

load_accounts()
log(f"[{_n}] v{_v} Dev: SrBan ---  AntBot.")
