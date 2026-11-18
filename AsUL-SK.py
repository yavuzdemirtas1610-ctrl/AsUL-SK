import os
import sys
import time
import tty
import termios
import select
import random
import urllib.request
import datetime

# Renk ve Terminal Kontrolleri (ANSI Kodları)
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
RESET = "\033[0m"
BOLD = "\033[1m"

# Gökkuşağı renk geçişleri (256-renk paleti)
RAINBOW_COLORS = [196, 202, 208, 214, 220, 226, 190, 154, 118, 46, 48, 50, 51, 45, 39, 33, 27, 21, 57, 93, 129, 165, 201]

# AsUL-SK Banner Tasarımı
BANNER_MAIN = [
    "╔═══╗╔═══╗╔╗ ╔╗╔╗        ╔═══╗╔╗ ╔╗",
    "║╔═╗║║╔═╗║║║ ║║║║        ║╔═╗║║║ ║║",
    "║║ ║║║╚══╗║║ ║║║║   ╔═══╗║╚══╗║╚═╝║",
    "║╚═╝║╚══╗║║║ ║║║║ ╔╗╚═══╝╚══╗║║╔═╗║",
    "║╔═╗║║╚═╝║║╚═╝║║╚═╝║     ║╚═╝║║║ ║║",
    "╚╝ ╚╝╚═══╝╚═══╝╚═══╝     ╚═══╝╚╝ ╚╝"
]

BANNER_HACK = [
    "╔═══╗╔═══╗╔╗ ╔╗╔╗   ╔═══╗╔╗ ╔╗   ╔╗ ╔╗╔═══╗╔═══╗╔╗ ╔╗  ╔════╗╔═══╗╔═══╗╔╗   ",
    "║╔═╗║║╔═╗║║║ ║║║║   ║╔═╗║║║ ║║   ║║ ║║║╔═╗║║╔═╗║║║ ║║  ║╔╗╔╗║║╔═╗║║╔═╗║║║   ",
    "║║ ║║║╚══╗║║ ║║║║   ║╚══╗║╚═╝║   ║╚═╝║║║ ║║║║ ╚╝║╚═╝║  ╚╝║║╚╝║║ ║║║║ ║║║║   ",
    "║╚═╝║╚══╗║║║ ║║║║ ╔╗╚══╗║║╔═╗║   ║╔═╗║║╚═╝║║║ ╔╗║╔═╗║    ║║  ║║ ║║║║ ║║║║ ╔╗",
    "║╔═╗║║╚═╝║║╚═╝║║╚═╝║║╚═╝║║║ ║║   ║║ ║║║╔═╗║║╚═╝║║║ ║║    ║║  ║╚═╝║║╚═╝║║╚═╝║",
    "╚╝ ╚╝╚═══╝╚═══╝╚═══╝╚═══╝╚╝ ╚╝   ╚╝ ╚╝╚╝ ╚╝╚═══╝╚╝ ╚╝    ╚╝  ╚═══╝╚═══╝╚═══╝"
]

# Global durum değişkenleri
running = True
in_submenu = False
current_banner = BANNER_MAIN
selected_index = 0
shift_offset = 0

MENU_ITEMS = [
    "1. Dosya Kontrol Etme (Eksik Kod / Sözdizimi)",
    "2. Dosya Güvenliği Analizi",
    "3. Site Güvenliği Kontrolü",
    "4. Hack Tool Bölgesi",
    "5. AsuL-AI (Yapay Zeka Asistanı)",
    "6. Quit (Çıkış)"
]

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
        if rlist:
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A':
                        return 'UP'
                    elif ch3 == 'B':
                        return 'DOWN'
            elif ch in ('w', 'W'):
                return 'UP'
            elif ch in ('s', 'S'):
                return 'DOWN'
            elif ch in ('\r', '\n'):
                return 'ENTER'
            elif ch == '\x03':
                return 'EXIT'
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return None

def render_screen():
    global shift_offset
    output = "\033[H"
    for line in current_banner:
        colored_line = ""
        for idx, char in enumerate(line):
            if char != " ":
                color_idx = (idx - shift_offset) % len(RAINBOW_COLORS)
                color_code = RAINBOW_COLORS[color_idx]
                colored_line += f"\033[38;5;{color_code}m{BOLD}{char}"
            else:
                colored_line += " "
        output += colored_line + RESET + "\033[K\n"
    
    output += "\033[38;5;240m" + "═" * 55 + RESET + "\033[K\n\n"

    if not in_submenu:
        output += f"  {BOLD}\033[38;5;250m[Yukarı/Aşağı Ok veya W/S ile gezin, Enter ile seçin]{RESET}\033[K\n\n"
        for i, item in enumerate(MENU_ITEMS):
            if i == selected_index:
                output += f"  \033[48;5;39m\033[38;5;16m{BOLD} ▶ {item} {RESET}\033[K\n"
            else:
                output += f"    \033[38;5;248m{item}{RESET}\033[K\n"
        
        for _ in range(8):
            output += "\033[K\n"

    sys.stdout.write(output)
    sys.stdout.flush()

def loading_bar(text, duration=1.5):
    steps = 25
    for i in range(steps + 1):
        percent = int((i / steps) * 100)
        bar = "█" * i + "░" * (steps - i)
        sys.stdout.write(f"\r  \033[38;5;51m{text} [\033[38;5;46m{bar}\033[38;5;51m] %{percent}{RESET}")
        sys.stdout.flush()
        time.sleep(duration / steps)
    print("\n")

def pause_and_return():
    print(f"\n  \033[38;5;226mAna menüye dönmek için ENTER tuşuna basın...{RESET}")
    input()

def check_file_syntax():
    print(f"  {BOLD}\033[38;5;51m[1] DOSYA KOD / EKSİK SATIR KONTROLCÜSÜ{RESET}")
    path = input("  Kontrol edilecek dosya yolunu girin (örn: test.py): ").strip()
    if not os.path.isfile(path):
        print(f"\n  \033[38;5;196m[HATA] '{path}' dosyası bulunamadı!{RESET}")
        pause_and_return()
        return

    loading_bar("Dosya satırları ve parantezler taranıyor")
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        lines = content.splitlines()

    issues = []
    if len(lines) == 0:
        issues.append("Dosya tamamen boş!")
    if content.count("(") != content.count(")"):
        issues.append(f"Eksik/Fazla parantez: '('={content.count('(')}, ')'={content.count(')')}")
    if content.count("{") != content.count("}"):
        issues.append(f"Eksik/Fazla süslü parantez: '{{'={content.count('{')}, '}}'={content.count('}')}")
    if content.count("[") != content.count("]"):
        issues.append(f"Eksik/Fazla köşeli parantez: '['={content.count('[')}, ']'={content.count(']')}")
    if "TODO" in content or "FIXME" in content:
        issues.append("Kod içinde tamamlanmamış 'TODO' veya 'FIXME' notları var.")

    print(f"  Toplam Satır Sayısı: {BOLD}{len(lines)}{RESET}")
    if not issues:
        print(f"  \033[38;5;46m[BAŞARILI] Kod temiz görünüyor, eksik blok bulunamadı!{RESET}")
    else:
        print(f"  \033[38;5;208m[UYARI] Tespit edilen eksikler:{RESET}")
        for iss in issues:
            print(f"   - {iss}")
    pause_and_return()

def check_file_security():
    print(f"  {BOLD}\033[38;5;51m[2] DOSYA GÜVENLİĞİ ANALİZİ{RESET}")
    path = input("  Taranacak dosya yolunu girin: ").strip()
    if not os.path.isfile(path):
        print(f"\n  \033[38;5;196m[HATA] Dosya bulunamadı!{RESET}")
        pause_and_return()
        return

    loading_bar("Zararlı imzalar ve şüpheli komutlar aranıyor")
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read().lower()

    danger_keywords = ["rm -rf", "eval(", "exec(", "os.system", "subprocess", "base64", "socket", "chmod 777"]
    found = [kw for kw in danger_keywords if kw in content]

    if found:
        print(f"  \033[38;5;196m[TEHLİKELİ / ŞÜPHELİ] Dosyada riskli ifadeler bulundu:{RESET}")
        print(f"  Bulunanlar: {', '.join(found)}")
        print("  Durum: GÜVENLİ DEĞİL (İncelemeden çalıştırmayın)")
    else:
        print(f"  \033[38;5;46m[TEMİZ] Zararlı bir komuta rastlanmadı. Dosya GÜVENLİ.{RESET}")
    pause_and_return()

def check_site_security():
    print(f"  {BOLD}\033[38;5;51m[3] SİTE GÜVENLİĞİ KONTROLÜ{RESET}")
    url = input("  Kontrol edilecek site adresi (örn: https://google.com): ").strip()
    if not url.startswith("http"):
        url = "https://" + url

    loading_bar("SSL sertifikası ve güvenlik başlıkları kontrol ediliyor")
    is_https = url.startswith("https://")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            headers = response.info()
            status = response.getcode()
            print(f"  Bağlantı Durumu: \033[38;5;46mAKTİF (HTTP {status}){RESET}")
            print(f"  HTTPS Şifreleme: {'\033[38;5;46mVAR (Güvenli)' if is_https else '\033[38;5;196mYOK (Güvensiz!)'}{RESET}")
            
            sec_headers = ["X-Frame-Options", "Strict-Transport-Security", "Content-Security-Policy"]
            missing = [h for h in sec_headers if h not in headers]
            
            if len(missing) <= 1 and is_https:
                print(f"\n  Sonuç: \033[38;5;46mBu site genel olarak GÜVENLİ görünüyor.{RESET}")
            else:
                print(f"\n  Sonuç: \033[38;5;208mDİKKAT! Eksik güvenlik duvarları var ({', '.join(missing)}).{RESET}")
    except Exception as e:
        print(f"  \033[38;5;196m[BAĞLANTI HATASI] Siteye ulaşılamadı veya geçersiz adres! ({e}){RESET}")
    pause_and_return()

def hack_tool_zone():
    global current_banner, in_submenu, shift_offset
    current_banner = BANNER_HACK
    os.system("clear")
    for _ in range(25):
        shift_offset = (shift_offset + 1) % len(RAINBOW_COLORS)
        render_screen()
        time.sleep(0.06)

    print(f"  {BOLD}\033[38;5;46m[AsUL-SK HACK TOOL SİMÜLASYON MODÜLÜ AKTİF]{RESET}\n")
    print("  1. Matrix IP İzleyici (Şaka Amaçlı)")
    print("  2. Uydu Bağlantısı Simülasyonu")
    print("  3. Ana Menüye Dön")
    
    choice = input("\n  Seçiminiz (1-3): ").strip()
    if choice == "1":
        print()
        for _ in range(15):
            fake_ip = f"{random.randint(11,250)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            ping = random.randint(12, 190)
            print(f"  \033[38;5;46m[TRACE] Hedef Düğüm: {fake_ip:<15} | Gecikme: {ping}ms | Şifre Çözüldü: ********{RESET}")
            time.sleep(0.15)
        print(f"\n  \033[38;5;226m[BİLGİ] Simülasyon tamamlandı. Hiçbir gerçek sisteme dokunulmadı :){RESET}")
        pause_and_return()
    elif choice == "2":
        loading_bar("NASA / Türksat uydularına bağlanılıyor", 2.0)
        print(f"  \033[38;5;46m[BAĞLANDI] Koordinatlar kilitlendi. Sistem emniyette!{RESET}")
        pause_and_return()
    current_banner = BANNER_MAIN

def asul_ai_chat():
    """5. Bölüm: AsuL-AI Akıllı Sohbet Asistanı (Asla 'iyi geceler' demez, her zaman merhaba der/akıllı yanıtlar verir)"""
    os.system("clear")
    print(f"  {BOLD}\033[38;5;51m[🤖 AsuL-AI - Akıllı Yapay Zeka Asistanı Aktif]{RESET}")
    print(f"  {BOLD}\033[38;5;248mMerhaba! Ben AsuL-AI. Kodlar, siber güvenlik veya herhangi bir konuda bana soru sorabilirsin.{RESET}")
    print(f"  {BOLD}\033[38;5;248m(Ana menüye dönmek için 'cikis' veya 'exit' yazabilirsin){RESET}\n" + "─" * 60)

    while True:
        try:
            q = input(f"\n  \033[38;5;226mSen:\033[0m ").strip()
            if q.lower() in ("cikis", "exit", "quit", "q"):
                print(f"\n  \033[38;5;46mAsuL-AI: Görüşürüz! Ana menüye dönüyorum.\033[0m")
                time.sleep(1)
                break
            
            if not q:
                continue

            # Akıllı Yanıt Üretme Mantığı (Asla iyi geceler demez, her zaman dinamik merhaba / akıllı yanıt verir)
            ql = q.lower()
            print(f"\n  \033[38;5;51mAsuL-AI düşünüyor...\033[0m", end="\r")
            time.sleep(0.6)

            if "merhaba" in ql or "selam" in ql:
                ans = "Merhaba! Sana nasıl yardımcı olabilirim? Bugün harika işler çıkarabiliriz!"
            elif "nasılsın" in ql or "nasıl gidiyor" in ql:
                ans = "Süperim! Kodlar akıyor, sistemler stabil. Sen nasılsın?"
            elif "hack" in ql or "siber" in ql or "güvenlik" in ql:
                ans = "Siber güvenlik harika bir alan! Menüdeki Hack Tool bölgesini veya Dosya Güvenliği analizini inceleyebilirsin."
            elif "python" in ql or "kod" in ql or "program" in ql:
                ans = "Python, terminal araçları yazmak için mükemmel bir dildir. Termux üzerinde harika projeler çıkarabilirsin."
            elif "adın ne" in ql or "sen kimsin" in ql:
                ans = "Ben AsuL-AI, AsUL-SK sisteminin akıllı yapay zeka asistanıyım!"
            else:
                # Genel akıllı alternatifler
                smart_replies = [
                    f"Harika bir konuya değindin! '{q}' hakkında sistem verilerini tarıyorum, bu konuyu derinlemesine inceleyebiliriz.",
                    f"Bunu düşündüğün iyi oldu. '{q}' analizi için uygun modülleri kullanabilir veya kod yazabiliriz.",
                    f"Anladım! '{q}' konusunda sana her zaman destek olmaya hazırım. Başka ne yapmak istersin?"
                ]
                ans = random.choice(smart_replies)

            print(f"  \033[38;5;46mAsuL-AI:\033[0m {ans}")

        except (KeyboardInterrupt, EOFError):
            break
    
    pause_and_return()

def main():
    global running, in_submenu, selected_index, shift_offset
    os.system("clear")
    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.flush()

    try:
        while running:
            shift_offset = (shift_offset + 1) % len(RAINBOW_COLORS)
            render_screen()
            
            key = get_key()
            if key == 'UP':
                selected_index = (selected_index - 1) % len(MENU_ITEMS)
            elif key == 'DOWN':
                selected_index = (selected_index + 1) % len(MENU_ITEMS)
            elif key == 'EXIT':
                running = False
            elif key == 'ENTER':
                if selected_index == 5:  # 6. Quit
                    running = False
                else:
                    in_submenu = True
                    os.system("clear")
                    render_screen()
                    if selected_index == 0:
                        check_file_syntax()
                    elif selected_index == 1:
                        check_file_security()
                    elif selected_index == 2:
                        check_site_security()
                    elif selected_index == 3:
                        hack_tool_zone()
                    elif selected_index == 4:
                        asul_ai_chat()
                    in_submenu = False
                    os.system("clear")
    finally:
        sys.stdout.write(SHOW_CURSOR + RESET)
        os.system("clear")
        print("AsUL-SK kapatıldı. Görüşmek üzere!")

if __name__ == "__main__":
    main()
              
