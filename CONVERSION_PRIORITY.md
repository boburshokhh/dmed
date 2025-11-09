# Приоритет методов конвертации DOCX в PDF

## Изменения

Теперь на **Windows** приоритет отдается `docx2pdf` вместо WeasyPrint, что:
- ✅ Устраняет проблемы с предупреждениями GLib-GIO
- ✅ Обеспечивает лучшую совместимость с Windows
- ✅ Использует нативные возможности Windows для конвертации

## Порядок методов конвертации

### На Windows:
1. **docx2pdf** (приоритет) - использует Microsoft Word через COM
2. LibreOffice (если установлен)
3. mammoth + weasyprint (fallback)
4. docx2pdf (fallback, если первый вызов не сработал)

### На Linux:
1. **LibreOffice** (приоритет) - лучший вариант для Linux
2. mammoth + weasyprint (fallback)
3. docx2pdf (не работает на Linux)

## Требования

### Для Windows:
```bash
pip install docx2pdf pywin32
```

**Важно:** `pywin32` необходим для работы `docx2pdf` на Windows.

### Для Linux:
```bash
sudo apt-get install -y libreoffice libreoffice-writer
```

## Преимущества docx2pdf на Windows

1. **Нет проблем с GLib-GIO** - не использует GTK/GLib
2. **Лучшее качество конвертации** - использует нативный Word
3. **Быстрее** - прямая конвертация без промежуточных форматов
4. **Надежнее** - меньше зависимостей

## Проверка установки

Проверьте, что `docx2pdf` доступен:
```python
from docx2pdf import convert
# Если импорт прошел успешно - все готово
```

Проверьте, что `pywin32` установлен:
```python
import pythoncom
# Если импорт прошел успешно - все готово
```

## Логи

При конвертации вы увидите:
```
[INFO] Используем docx2pdf для конвертации (Windows)...
[OK] DOCX успешно конвертирован в PDF через docx2pdf: ...
```

Если `docx2pdf` недоступен, система автоматически попробует другие методы.




