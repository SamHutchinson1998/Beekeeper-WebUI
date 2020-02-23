#! bin/bash

python /beekeeper_webui/manage.py collectstatic
sudo systemctl restart /etc/systemd/system/gunicorn.service
sudo systemctl restart gunicorn
sudo systemctl restart nginx