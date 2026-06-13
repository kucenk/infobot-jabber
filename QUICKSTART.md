# 🚀 Quick Start Guide - InfoBot Jabber

## Instalasi Cepat (5 Menit)

### 1. Clone Repository
```bash
git clone https://github.com/kucenk/infobot-jabber.git
cd infobot-jabber
```

### 2. Setup Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Buat Direktori Penting
```bash
mkdir -p logs config data
```

### 4. Konfigurasi Bot
```bash
cp config/config.example.yaml config/config.yaml
nano config/config.yaml
```

**Edit bagian ini dengan data Anda:**
```yaml
bot:
  jid: "infobot@jabber.ru"        # Ganti dengan JID bot Anda
  password: "password123"          # Ganti dengan password
  
openweather:
  api_key: "your_api_key_here"    # Daftar di openweathermap.org

rooms:
  - name: "devroom@conference.jabber.ru"  # Ruangan target
    admin_jid: "admin@jabber.ru"           # Admin JID
```

### 5. Test Run Bot
```bash
python3 main.py
```

Jika berhasil, Anda akan melihat:
```
✅ InfoBot connected and running
✅ Joined room: devroom@conference.jabber.ru as InfoBot
```

**Tekan `Ctrl+C` untuk stop**

---

## Setup Systemd (Untuk Production)

### 1. Buat User Bot
```bash
sudo useradd -m -s /bin/bash infobot
```

### 2. Copy Service File
```bash
sudo cp systemd/infobot.service /etc/systemd/system/
sudo systemctl daemon-reload
```

### 3. Enable & Start Service
```bash
sudo systemctl enable infobot
sudo systemctl start infobot
sudo systemctl status infobot
```

### 4. Monitor Bot
```bash
# Real-time logs
sudo journalctl -u infobot -f

# Atau dari file
tail -f logs/infobot.log
```

---

## Perintah Bot Dasar

Ketik di chat room:

```
!help              - Bantuan lengkap
!cuaca Jakarta     - Cuaca di Jakarta
!gempa             - Gempa terkini
!server            - Status server
!ping              - Cek koneksi
!uptime            - Uptime server
```

---

## Troubleshooting

### Bot tidak bisa connect
```bash
# Check config
cat config/config.yaml

# Check Python modules
python3 -c "import slixmpp; print('OK')"
```

### API OpenWeather tidak kerja
- Daftar di https://openweathermap.org
- Daftar API key gratis
- Update di config/config.yaml

### Bot tidak join room
- Verifikasi format JID: `room@conference.server.com`
- Pastikan bot terdaftar di server XMPP
- Check firewall rules

---

## Informasi Lebih Lanjut

- Lihat `README.md` untuk dokumentasi lengkap
- Lihat `config/config.example.yaml` untuk semua opsi konfigurasi
- BMKG API: https://data.bmkg.go.id
- OpenWeather: https://openweathermap.org

---

**Happy botting! 🤖**
