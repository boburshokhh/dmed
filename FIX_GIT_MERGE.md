# Решение проблемы Git merge - расходящиеся ветки

## Проблема
Git видит расходящиеся ветки (divergent branches) и требует указать стратегию слияния.

## Решение на сервере

### Вариант 1: Merge (рекомендуется)

```bash
cd /var/www/dmed

# Выполнить merge с явным указанием стратегии
git pull origin main --no-rebase

# Если возникнут конфликты, разрешите их и сделайте:
# git add .
# git commit
```

### Вариант 2: Rebase (если хотите линейную историю)

```bash
cd /var/www/dmed

# Выполнить rebase
git pull origin main --rebase

# Если возникнут конфликты:
# 1. Разрешите конфликты вручную
# 2. git add .
# 3. git rebase --continue
```

### Вариант 3: Принять изменения из удаленной ветки (если локальные изменения не важны)

```bash
cd /var/www/dmed

# Сохранить текущее состояние (на всякий случай)
git stash

# Принудительно обновить до состояния удаленной ветки
git fetch origin main
git reset --hard origin/main
```

### Вариант 4: Настроить стратегию по умолчанию

```bash
cd /var/www/dmed

# Настроить merge как стратегию по умолчанию
git config pull.rebase false

# Теперь можно просто делать pull
git pull origin main
```

## Рекомендуемая последовательность (если файлы уже удалены локально)

```bash
cd /var/www/dmed

# 1. Удалить файлы, которые были удалены в удаленной ветке
git rm FIX_UBUNTU_QRCODE.sh check_qr_logs.sh diagnose_qrcode_styled.py fix_gunicorn_venv.sh 2>/dev/null || true

# 2. Настроить стратегию merge
git config pull.rebase false

# 3. Выполнить pull с merge
git pull origin main --no-edit

# 4. Если все прошло успешно, можно запушить изменения
git push origin main
```
