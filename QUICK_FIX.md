# Быстрое решение проблемы конвертации DOCX в PDF

## Проблема
После деплоя на Linux сервер конвертация DOCX в PDF не работает (ошибка 500).

## Причина
Отсутствуют системные библиотеки для `weasyprint`, которые необходимы для конвертации DOCX в PDF на Linux.

## Решение (выполните на сервере)

### Шаг 1: Установите системные зависимости

**Для Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

**Для CentOS/RHEL:**
```bash
sudo yum install -y pango pango-devel harfbuzz cairo cairo-devel gdk-pixbuf2
```

### Шаг 2: Переустановите weasyprint
```bash
pip install --upgrade --force-reinstall weasyprint
```

### Шаг 3: Перезапустите приложение
```bash
# Если используете systemd:
sudo systemctl restart your-app-name

# Если используете gunicorn/uwsgi:
sudo systemctl restart gunicorn

# Или просто перезапустите процесс вручную
```

### Шаг 4: Проверьте работу
Попробуйте создать документ через веб-интерфейс. Если проблема сохраняется, проверьте логи:
```bash
# Логи systemd (для сервиса dmed)
sudo journalctl -u dmed -f

# Или последние 100 строк логов
sudo journalctl -u dmed -n 100

# Проверка статуса сервиса
sudo systemctl status dmed
```

**Если apt заблокирован:**
```bash
# Проверьте, какой процесс использует apt
ps aux | grep apt

# Подождите завершения процесса или проверьте через несколько секунд
# Обычно apt завершается автоматически
```

## Проверка установки

Выполните в Python:
```python
from weasyprint import HTML
HTML(string="<html><body>Test</body></html>").write_pdf("test.pdf")
```

Если файл `test.pdf` создался - все работает!

## Дополнительная информация

Подробные инструкции см. в файле `DEPLOYMENT.md`

