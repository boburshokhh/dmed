# Документация API DMED Backend

## Базовый URL

**Продакшен:** `https://dmed.gubkin.uz/`

---

## Описание

DMED Backend - это REST API для создания, верификации и управления медицинскими документами (справки о временной нетрудоспособности). Система автоматически генерирует PDF и DOCX документы с QR-кодами и PIN-кодами для верификации подлинности.

---

## Основные эндпоинты

### 1. Создание документа

**POST** `/create-document`

Создает новый медицинский документ с автоматической генерацией номера документа, PIN-кода и UUID.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "patient_name": "ИВАНОВ ИВАН ИВАНОВИЧ",
  "gender": "Erkak",
  "age": "25",
  "jshshir": "12345678901234",
  "address": "г. Ташкент, ул. Примерная, д. 1",
  "attached_medical_institution": "4 - sonli oilaviy poliklinika",
  "diagnosis": "ОРВИ",
  "diagnosis_icd10_code": "J00",
  "final_diagnosis": "Острая респираторная вирусная инфекция",
  "final_diagnosis_icd10_code": "J00",
  "organization": "O'zbekiston Respublikasi Sog'liqni saqlash vazirligi",
  "doctor_name": "ПЕТРОВ ПЕТР ПЕТРОВИЧ",
  "doctor_position": "Терапевт",
  "department_head_name": "СИДОРОВ СИДОР СИДОРОВИЧ",
  "days_off_from": "2024-11-08",
  "days_off_to": "2024-11-15",
  "issue_date": "2024-11-08"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "document_id": 123,
  "doc_number": "№ 01ВШ 081125200",
  "pin_code": "8307",
  "download_url": "/download/123",
  "docx_url": "/download-docx/123",
  "convert_docx_to_pdf_url": "/convert-docx-to-pdf/123"
}
```

**Response (500 Error):**
```json
{
  "success": false,
  "error": "Описание ошибки"
}
```

**Пример запроса (cURL):**
```bash
curl -X POST https://dmed.gubkin.uz/create-document \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "ИВАНОВ ИВАН ИВАНОВИЧ",
    "gender": "Erkak",
    "age": "25",
    "diagnosis": "ОРВИ",
    "doctor_name": "ПЕТРОВ ПЕТР ПЕТРОВИЧ"
  }'
```

---

### 2. Верификация документа по PIN-коду

**POST** `/verify-pin`

Проверяет PIN-код и возвращает полную информацию о документе.

**Request Body:**
```json
{
  "pin_code": "8307"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "document": {
    "id": 123,
    "doc_number": "№ 01ВШ 081125200",
    "patient_name": "ИВАНОВ ИВАН ИВАНОВИЧ",
    "gender": "Erkak",
    "age": "25",
    "jshshir": "12345678901234",
    "address": "г. Ташкент, ул. Примерная, д. 1",
    "attached_medical_institution": "4 - sonli oilaviy poliklinika",
    "diagnosis": "ОРВИ",
    "diagnosis_icd10_code": "J00",
    "final_diagnosis": "Острая респираторная вирусная инфекция",
    "final_diagnosis_icd10_code": "J00",
    "organization": "O'zbekiston Respublikasi Sog'liqni saqlash vazirligi",
    "issue_date": "08.11.2024 14:30",
    "doctor_name": "ПЕТРОВ ПЕТР ПЕТРОВИЧ",
    "doctor_position": "Терапевт",
    "department_head_name": "СИДОРОВ СИДОР СИДОРОВИЧ",
    "days_off_period": "08.11.2024 - 15.11.2024",
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "pdf_url": "https://dmed.gubkin.uz/download/123,
    "docx_url": "https://dmed.gubkin.uz/download-docx/123"
  }
}
```

**Response (404 Not Found):**
```json
{
  "success": false,
  "error": "Документ не найден"
}
```

**Пример запроса (cURL):**
```bash
curl -X POST https://dmed.gubkin.uz/verify-pin \
  -H "Content-Type: application/json" \
  -d '{"pin_code": "8307"}'
```

---

### 3. Скачивание PDF документа

**GET** `/download/<doc_id>`

Скачивает PDF версию документа по ID.

**Пример:**
```
GET https://dmed.gubkin.uz/download/123
```

**Response:**
- **200 OK:** PDF файл (application/pdf)
- **404 Not Found:** Текстовая ошибка

**Пример запроса (cURL):**
```bash
curl -O https://dmed.gubkin.uz/download/123
```

---

### 4. Скачивание DOCX документа

**GET** `/download-docx/<doc_id>`

Скачивает DOCX версию документа по ID.

**Пример:**
```
GET https://dmed.gubkin.uz/download-docx/123
```

**Response:**
- **200 OK:** DOCX файл (application/vnd.openxmlformats-officedocument.wordprocessingml.document)
- **404 Not Found:** Текстовая ошибка

---

### 5. Конвертация DOCX в PDF

**GET** `/convert-docx-to-pdf/<doc_id>`

Конвертирует DOCX документ в PDF и возвращает PDF файл.

**Пример:**
```
GET https://dmed.gubkin.uz/convert-docx-to-pdf/123
```

**Response:**
- **200 OK:** PDF файл
- **404 Not Found:** JSON с ошибкой
- **500 Error:** JSON с ошибкой

---

### 6. Просмотр документа (веб-страница)

**GET** `/document/<doc_id>`

Открывает веб-страницу с информацией о документе.

**Пример:**
```
GET https://dmed.gubkin.uz/document/123
```

**Response:**
- **200 OK:** HTML страница
- **404 Not Found:** Текстовая ошибка

---

### 7. Просмотр документа по номеру

**GET** `/document/<doc_number>`

Открывает веб-страницу с информацией о документе по номеру документа.

**Пример:**
```
GET https://dmed.gubkin.uz/document/№ 01ВШ 081125200
```

---

### 8. Страница верификации

**GET** `/verify`

Открывает веб-страницу для ввода PIN-кода и верификации документа.

**Пример:**
```
GET https://dmed.gubkin.uz/verify
```

---

### 9. Главная страница

**GET** `/`

Открывает главную страницу с формой создания документа.

**Пример:**
```
GET https://dmed.gubkin.uz/
```

---

## Форматы данных

### Даты

- **Формат отправки:** `YYYY-MM-DD` (например: `2024-11-08`)
- **Формат ответа:** `DD.MM.YYYY HH:MM` (например: `08.11.2024 14:30`)

### Номер документа

Автоматически генерируется в формате: `№ <PREFIX> <9-значный номер>`

Пример: `№ 01ВШ 081125200`

### PIN-код

4-значный числовой код для верификации документа.

Пример: `8307`

### UUID

Уникальный идентификатор документа в формате UUID v4.

Пример: `550e8400-e29b-41d4-a716-446655440000`

---

## Коды ошибок

| Код | Описание |
|-----|----------|
| 200 | Успешный запрос |
| 400 | Неверный запрос (отсутствуют обязательные поля) |
| 404 | Ресурс не найден (документ не существует) |
| 500 | Внутренняя ошибка сервера |

---

## Примеры использования

### JavaScript (Fetch API)

```javascript
// Создание документа
async function createDocument(data) {
  const response = await fetch('https://dmed.gubkin.uz/create-document', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
  });
  
  const result = await response.json();
  return result;
}

// Верификация по PIN-коду
async function verifyDocument(pinCode) {
  const response = await fetch('https://dmed.gubkin.uz/verify-pin', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ pin_code: pinCode })
  });
  
  const result = await response.json();
  return result;
}
```

### Python (requests)

```python
import requests

# Создание документа
def create_document(data):
    response = requests.post(
        'https://dmed.gubkin.uz/create-document',
        json=data
    )
    return response.json()

# Верификация по PIN-коду
def verify_document(pin_code):
    response = requests.post(
        'https://dmed.gubkin.uz/verify-pin',
        json={'pin_code': pin_code}
    )
    return response.json()
```

---

## Технические детали

- **Backend Framework:** Flask (Python)
- **Database:** PostgreSQL
- **Форматы документов:** PDF (ReportLab), DOCX (python-docx)
- **QR-коды:** qrcode library
- **Аутентификация:** PIN-код (4 цифры)

---

## Важные замечания

1. **PIN-код** - единственный способ верификации документа. Сохраняйте его при создании документа.

2. **QR-код** на документе содержит ссылку на страницу верификации (`/verify`).

3. Документы автоматически генерируются в форматах **PDF** и **DOCX**.

4. Все даты должны быть в формате **YYYY-MM-DD**.

5. Номер документа генерируется автоматически и уникален.

---

## Поддержка

При возникновении проблем или вопросов обращайтесь к разработчикам проекта.

---

**Версия API:** 1.0  
**Дата обновления:** Ноябрь 2024  
**Базовый URL:** https://dmed.gubkin.uz/

