from phBot import *
import ctypes, time, QtBind, os, subprocess, urllib.request, json


_n = 'AntBot teleport Trade'
_v = '26.0' 
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


_u32 = ctypes.windll.user32
_u = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS1h7zFy9nH68Dij7bAJutZ0DuYJj1zV9jet8rhAnAMqAcKhmrHoctKjd5uToJor1zV291zCUi4cyrh/pub?output=csv"
_folder_path = os.path.join(os.getcwd(), "Plugins", "TradeHide_Configs")


if not os.path.exists(_folder_path):
    os.makedirs(_folder_path)

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

def _log(m): QtBind.append(gui, lstLogs, f"[{time.strftime('%H:%M:%S')}] {m}")


def _process_click(entry_str):
    try:
        if "[OFF]" in entry_str: return
        parts = entry_str.split("] ")[1]
        name, res = parts.split(" | ")
        
        
        
        rw, rh = map(int, res.split('x'))
        cx = int(rw * (640 / 1366))
        cy = int(rh * (419 / 768))
        
        hw = find_sro(f"[NewEvolust] {name}")
        if hw:
            lp = (cy << 16) | (cx & 0xFFFF)
            _u32.PostMessageW(hw, 0x0201, 0x0001, lp) # Botão Esquerdo Down
            time.sleep(0.1)
            _u32.PostMessageW(hw, 0x0202, 0, lp)      # Botão Esquerdo Up
            _log(f"✔ Auto-Agree: {name} em ({cx},{cy})")
    except Exception as e: _log(f"❌ Erro clique: {str(e)}")

def handle_joymax(opcode, data):
    if opcode == 0x190A:
        if not _auth: return True
        time.sleep(0.1) 
        for entry in QtBind.getItems(gui, lstChars):
            if "[ON]" in entry:
                _process_click(entry)
    return True


def load_accounts():
    QtBind.clear(gui, lstChars)
    if os.path.exists(_folder_path):
        for f in os.listdir(_folder_path):
            if f.endswith(".json"):
                try:
                    with open(os.path.join(_folder_path, f), "r") as file:
                        d = json.load(file)
                        st = "[ON]" if d.get("enabled", True) else "[OFF]"
                        QtBind.append(gui, lstChars, f"{st} {d['name']} | {d['res']}")
                except: pass

def btnAdd_clicked():
    if not _auth: return
    n, r = QtBind.text(gui, txtNewChar), QtBind.text(gui, txtNewRes).lower()
    if n and "x" in r:
        try:
            with open(os.path.join(_folder_path, f"{n}.json"), "w") as f:
                json.dump({"name": n, "res": r, "enabled": True}, f)
            load_accounts()
            _log(f"💾 Conta {n} salva.")
        except Exception as e: _log(f"❌ Erro ao salvar: {str(e)}")

def btnToggle_clicked():
    sel = QtBind.text(gui, lstChars)
    if sel:
        try:
            name = sel.split("] ")[1].split(" | ")[0]
            p = os.path.join(_folder_path, f"{name}.json")
            data = {}
            with open(p, "r") as f: data = json.load(f)
            data["enabled"] = not data.get("enabled", True)
            with open(p, "w") as f: json.dump(data, f)
            load_accounts()
            _log(f"🔄 {name} alterado.")
        except Exception as e: _log(f"❌ Erro ao alternar: {str(e)}")

def btnDel_clicked():
    sel = QtBind.text(gui, lstChars)
    if sel:
        try:
            name = sel.split("] ")[1].split(" | ")[0]
            os.remove(os.path.join(_folder_path, f"{name}.json"))
            load_accounts()
            _log(f"🗑️ {name} removido.")
        except: pass

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
log(f"[{_n}] v{_v} Iniciado.")
