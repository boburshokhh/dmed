// Функция закрытия модального окна
function closeModal() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('resultModal'));
    if (modal) {
        modal.hide();
    }
    document.getElementById('documentForm').reset();
}

// Функция автозаполнения формы
function autoFillForm() {
    // Тестовые данные для автозаполнения
    const testData = {
        patient_name: 'ИВАНОВ ИВАН ИВАНОВИЧ',
        gender: 'Erkak',
        age: '25 yosh',
        jshshir: '51506056600101',
        address: 'Город Ташкент, Мирзо-Улугбекский район, улица Амира Темура, дом 15',
        attached_medical_institution: '4-sonli oilaviy poliklinika',
        diagnosis: 'Острый трахеит',
        diagnosis_icd10_code: 'J04.1',
        final_diagnosis: 'Острый трахеит',
        final_diagnosis_icd10_code: 'J04.1',
        organization: '4 - sonli oilaviy poliklinika',
        doctor_name: 'USENOVA N.U.',
        doctor_position: 'Terapevt',
        department_head_name: 'ABDURAIMOVA T.T.',
        days_off_from: '2025-10-27',
        days_off_to: '2025-10-31',
        issue_date: '2025-02-10'
    };

    // Заполняем все поля формы
    const form = document.getElementById('documentForm');
    
    // Заполняем текстовые поля
    Object.keys(testData).forEach(key => {
        const input = form.querySelector(`[name="${key}"]`);
        if (input) {
            input.value = testData[key];
        }
    });


    // Показываем уведомление (адаптивное)
    showNotification('✅ Форма заполнена тестовыми данными!');

    // Прокручиваем к началу формы
    form.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Функция показа уведомления
function showNotification(message) {
    const notification = document.createElement('div');
    const isMobile = window.innerWidth <= 768;
    notification.style.cssText = `
        position: fixed;
        top: ${isMobile ? '10px' : '20px'};
        ${isMobile ? 'left: 10px; right: 10px;' : 'right: 20px;'}
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: ${isMobile ? '12px 16px' : '15px 20px'};
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        font-size: ${isMobile ? '13px' : '14px'};
        font-weight: 500;
        text-align: center;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    // Удаляем уведомление через 3 секунды
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Функция сбора данных формы
function collectFormData() {
    const formData = new FormData(document.getElementById('documentForm'));
    const data = {
        patient_name: formData.get('patient_name'),
        gender: formData.get('gender'),
        age: formData.get('age'),
        jshshir: formData.get('jshshir'),
        address: formData.get('address'),
        attached_medical_institution: formData.get('attached_medical_institution'),
        diagnosis: formData.get('diagnosis'),
        diagnosis_icd10_code: formData.get('diagnosis_icd10_code'),
        final_diagnosis: formData.get('final_diagnosis'),
        final_diagnosis_icd10_code: formData.get('final_diagnosis_icd10_code'),
        organization: formData.get('organization'),
        doctor_name: formData.get('doctor_name'),
        doctor_position: formData.get('doctor_position'),
        department_head_name: formData.get('department_head_name'),
        days_off_from: formData.get('days_off_from'),
        days_off_to: formData.get('days_off_to'),
        issue_date: formData.get('issue_date')
    };

    return data;
}

// Функция отправки формы
async function submitForm(data) {
    // Показываем загрузку
    document.getElementById('loading').classList.remove('d-none');
    document.getElementById('documentForm').classList.add('d-none');

    try {
        const response = await fetch('/create-document', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            showSuccessModal(result);
            console.log('Документ создан успешно!');
            console.log('Номер документа:', result.doc_number);
            console.log('PIN-код:', result.pin_code);
        } else {
            alert('Ошибка при создании документа: ' + result.error);
            console.error('Ошибка создания документа:', result.error);
        }
    } catch (error) {
        alert('Ошибка при отправке формы: ' + error.message);
    } finally {
        // Скрываем загрузку
        document.getElementById('loading').classList.add('d-none');
        document.getElementById('documentForm').classList.remove('d-none');
    }
}

// Функция показа модального окна успеха
function showSuccessModal(result) {
    // Заполняем модальное окно
    document.getElementById('resultDocNumber').textContent = result.doc_number;
    document.getElementById('resultPinCode').textContent = result.pin_code;
    document.getElementById('downloadLink').href = result.download_url;
    
    // Показываем модальное окно через Bootstrap API
    const modalElement = document.getElementById('resultModal');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
    
    // Сбрасываем форму при закрытии модального окна
    modalElement.addEventListener('hidden.bs.modal', function () {
        document.getElementById('documentForm').reset();
    }, { once: true });
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Обработчик отправки формы
    document.getElementById('documentForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = collectFormData();
        await submitForm(data);
    });
});

