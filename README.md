# InfoBot Jabber 🤖

Bot Jabber profesional untuk Armbian dengan fitur peringatan cuaca, gempa bumi, monitoring server, dan manajemen multi-ruangan.

## 📋 Fitur Utama

✅ **Koneksi XMPP Multi-Ruangan**
- Dukungan jabber.ru, jabber.de, dan XMPP server lainnya
- Otomatis join ke ruangan yang dikonfigurasi
- Status dynamic (online/away/dnd)

✅ **Peringatan Real-time**
- Notifikasi gempa bumi dari BMKG
- Data cuaca dari OpenWeather API
- Alert sistem dan peringatan kritis

✅ **Monitoring Server Armbian**
- CPU, RAM, Storage, Temperature monitoring
- Uptime dan sistem info
- Notifikasi otomatis saat resource critical

✅ **Manajemen Admin**
- Kontrol akses berbasis JID
- Konfigurasi per-ruangan
- Logging dan audit trail

✅ **Sambutan & Interaksi**
- Welcome message saat user join
- Activity detection dan status auto-update
- Response commands yang ekstensif

✅ **Konfigurasi Persistent**
- YAML-based config untuk setiap ruangan
- Penyimpanan settings di database SQLite
- Hot-reload tanpa restart

## 🔧 Instalasi

### Prerequisites
- Python 3.7+
- Armbian/Linux
- pip & venv

### Setup

```bash
# Clone repository
git clone https://github.com/kucenk/infobot-jabber.git
cd infobot-jabber

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Konfigurasi
cp config/config.example.yaml config/config.yaml
nano config/config.yaml

# Run
python3 main.py
```

## 📝 Konfigurasi

Lihat `config/config.example.yaml` untuk semua opsi konfigurasi.

```yaml
bot:
  nick: "InfoBot"
  jid: "infobot@jabber.ru"
  password: "your_password"
  
rooms:
  - name: "room1@conference.jabber.ru"
    nickname: "InfoBot"
    enable_weather: true
    enable_earthquake: true
    admin_jid: "admin@jabber.ru"
    language: "id"
```

## 🎯 Commands

```
!help              - Tampilkan bantuan
!cuaca [kota]      - Cek cuaca
!gempa             - Gempa terakhir
!server            - Status server
!status [msg]      - Update status
!admin [cmd]       - Admin commands (admin only)
!ping              - Cek koneksi
!uptime            - Uptime server
```

## 📊 Struktur Proyek

```
infobot-jabber/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── config/
│   ├── config.example.yaml # Template config
│   └── config.yaml         # Live config (git ignored)
├── bot/
│   ├── __init__.py
│   ├── core.py             # Bot core & XMPP logic
│   ├── handlers.py         # Message handlers
│   └── utils.py            # Helper functions
├── modules/
│   ├── weather.py          # OpenWeather API
│   ├── earthquake.py       # BMKG API
│   ├── monitoring.py       # Server monitoring
│   ├── database.py         # SQLite storage
│   └── notifications.py    # Alert system
├── systemd/
│   └── infobot.service     # Systemd service
├── logs/                   # Log files
├── data/                   # Database & persistent data
└── scripts/
    └── install.sh          # Installation script
```

## 🚀 Running as Service (Systemd)

```bash
sudo cp systemd/infobot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable infobot
sudo systemctl start infobot
sudo systemctl status infobot
```

## 📡 API & Data Sources

- **BMKG API**: https://data.bmkg.go.id (Gempa & Cuaca)
- **OpenWeather**: https://api.openweathermap.org (Cuaca Detail)
- **XMPP Servers**: jabber.ru, jabber.de, dan lainnya

## 🔐 Security

- JID-based admin authentication
- Encrypted password storage
- Input validation & sanitization
- Rate limiting untuk API calls

## 📝 Logging & Monitoring

```bash
# Lihat logs real-time
journalctl -u infobot -f

# Atau dari file
tail -f logs/infobot.log
```

## 🤝 Kontribusi

Silakan fork dan buat pull request untuk improvement.

## 📄 Lisensi

MIT License - Gratis untuk penggunaan komersial dan personal

## 👨‍💻 Author

**kucenk** - InfoBot Jabber Project

---

**Status**: Production Ready ✅ | **Last Updated**: 2026 | **Stability**: 24/7 Tested