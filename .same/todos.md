# Harley Telegram Bot - Yapılacaklar

## Tamamlanan
- [x] Proje yapısını oluştur
- [x] Config modülünü oluştur
- [x] Core modüllerini oluştur (client, events)
- [x] Utils modüllerini oluştur (helpers, formatters)
- [x] Log Bot modülünü oluştur
- [x] Anti-Spam modülünü oluştur
- [x] Ana giriş noktasını (main.py) oluştur
- [x] Session generator script'i oluştur
- [x] Requirements, Procfile, runtime.txt oluştur
- [x] README.md oluştur
- [x] .env.example ve .gitignore oluştur

## Proje Yapısı
```
harley-telegram-bot/
├── main.py                    # Ana giriş noktası
├── src/
│   ├── config/settings.py     # Tüm ayarlar
│   ├── core/
│   │   ├── client.py          # Telegram client yönetimi
│   │   └── events.py          # Event tipleri
│   ├── modules/
│   │   ├── log_bot/           # Log Bot modülü
│   │   │   ├── handler.py     # Event handler'lar
│   │   │   ├── formatter.py   # Log formatters
│   │   │   └── actions.py     # Admin log action işleyicileri
│   │   └── anti_spam/         # Anti-Spam modülü
│   │       ├── handler.py     # Komut handler'lar
│   │       └── cleaner.py     # İstek temizleyici
│   └── utils/
│       ├── helpers.py         # Yardımcı fonksiyonlar
│       └── formatters.py      # Genel formatters
├── scripts/
│   └── generate_session.py    # Session oluşturucu
```
