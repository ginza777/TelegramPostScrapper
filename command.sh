#!/bin/bash



# Systemd xizmatlarini qayta boshlash
sudo systemctl daemon-reload

# Celery xizmatini qayta boshlash
sudo systemctl enable celery_ads_manager_worker
sudo systemctl start celery_ads_manager_worker
sudo systemctl restart celery_ads_manager_worker
sudo systemctl status celery_ads_manager_worker



# Celery beat xizmatini qayta boshlash (agar kerak bo'lsa)
sudo systemctl enable celery_ads_manager_beat
sudo systemctl start celery_ads_manager_beat
sudo systemctl restart celery_ads_manager_beat
sudo systemctl status celery_ads_manager_beat




# Telegram_ads.socket va telegram_ads.service xizmatlarini qayta boshlash
sudo systemctl restart TelegramParser.socket
sudo systemctl restart TelegramParser.service

# client.service xizmatini qayta boshlash (agar kerak bo'lsa)
#sudo systemctl restart client.service

# Nginx konfiguratsiyasini tekshirish va Nginx ni qayta boshlash
sudo nginx -t && sudo systemctl restart nginx


sudo systemctl status celery_ads_manager_worker
sudo systemctl status celery_ads_manager_beat