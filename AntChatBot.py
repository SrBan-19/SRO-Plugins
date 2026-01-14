from phBot import *
import ctypes, time, QtBind, os, subprocess, urllib.request, json

_n = 'Trade Hide Premium Pro'
_v = '25.5'  
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
                    log(f"[{_n}] Nova atualização encontrada: {remote_version}. Baixando...")
                    with open(_plugin_path, "w", encoding='utf-8') as f:
                        f.write(remote_code)
                    log(f"[{_n}] Plugin atualizado com sucesso! Reinicie o phBot ou dê Reload.")
                    return True
    except: pass
    return False

check_for_updates()

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
btnTest = QtBind.createButton(gui, "btnTest_clicked", " TESTAR POSIÇÃO ", 235, 195)

QtBind.createLabel(gui, "Script de Rota:", 15, 250)
cmbScripts = QtBind.createCombobox(gui, 15, 265, 150, 20)
QtBind.append(gui, cmbScripts, "Hotan x Jangan")
QtBind.append(gui, cmbScripts, "Constantinopla x Hotan")
QtBind.append(gui, cmbScripts, "Jangan x Constantinopla")
btnStartRoute = QtBind.createButton(gui, "btnStartRoute_clicked", " INICIAR ROTA ", 170, 263)

def _log(m): QtBind.append(gui, lstLogs, f"[{time.strftime('%H:%M:%S')}] {m}")

def _force_click(entry_str, move_mouse=True):
    try:
        name, res = entry_str.split("] ")[1].split(" | ")
        rw, rh = map(int, res.split('x'))
        cx, cy = int(rw * 0.4685), int(rh * 0.5455)
        hw = find_sro(f"[NewEvolust] {name}")
        if hw:
            if move_mouse:
                rect = ctypes.wintypes.RECT()
                _u32.GetWindowRect(hw, ctypes.byref(rect))
                _u32.SetCursorPos(rect.left + cx, rect.top + cy)
            lp = (cy << 16) | (cx & 0xFFFF)
            # Envia o clique de forma forçada
            _u32.PostMessageW(hw, 0x0201, 0x0001, lp) # WM_LBUTTONDOWN
            time.sleep(0.05)
            _u32.PostMessageW(hw, 0x0202, 0, lp)      # WM_LBUTTONUP
            _log(f"🎯 Clique em {name}")
    except: pass

# --- CORREÇÃO DO OPCODE AQUI ---
def handle_joymax(opcode, data):
    # Alterado de 0x3053 para 0x190A (Opcode de Confirmação/Agree)
    if opcode == 0x190A: 
        if not _auth: return True
        # Tenta aceitar via pacote primeiro (Invisível)
        inject_joymax(0x190A, b'\x01', False)
        
        # Delay necessário para o jogo processar a janela visualmente
        time.sleep(1.0) 
        
        # Executa o clique visual em todas as janelas marcadas como [ON]
        for entry in QtBind.getItems(gui, lstChars):
            if "[ON]" in entry:
                _force_click(entry, move_mouse=True)
    return True

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

# --- Restante das funções permanecem as mesmas ---
def btnStartRoute_clicked():
    if not _auth: return
    sel = QtBind.text(gui, cmbScripts)
    files = {"Hotan x Jangan": "tradecompleta.txt", "Constantinopla x Hotan": "const_hotan.txt", "Jangan x Constantinopla": "jangan_const.txt"}
    filename = files.get(sel)
    if filename:
        path = os.path.join(os.getcwd(), filename)
        if not os.path.exists(path): path = os.path.join(os.getcwd(), "Config", filename)
        if os.path.exists(path):
            set_training_script(path)
            start_bot()
            _log(f"🚀 Rota {sel} Iniciada!")

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
    n, r = QtBind.text(gui, txtNewChar), QtBind.text(gui, txtNewRes)
    if n and "x" in r:
        with open(os.path.join(_folder_path, f"{n}.json"), "w") as f:
            json.dump({"name": n, "res": r, "enabled": True}, f)
        load_accounts()

def btnTest_clicked():
    sel = QtBind.text(gui, lstChars)
    if sel: _force_click(sel, move_mouse=True)

def btnCapture_clicked():
    hw = find_sro("[NewEvolust]")
    if hw:
        ln = _u32.GetWindowTextLengthW(hw)
        b = ctypes.create_unicode_buffer(ln + 1)
        _u32.GetWindowTextW(hw, b, ln + 1)
        if " " in b.value: QtBind.setText(gui, txtNewChar, b.value.split(" ", 1)[1])

load_accounts()
log(f"Dev: SrBan - Versão {_v} | Auto-Update Ativo.")

