// Конфигурация API
const API_URLS = {
    AUTH: 'http://127.0.0.1:8000/auth',
    VERIFY: 'http://127.0.0.1:8000/verify',
    REGISTER: 'http://127.0.0.1:8000/register',
    DIGITIZE: 'http://127.0.0.1:8001/process-document',
    GENERATE: 'http://127.0.0.1:8002/api/v1/extract_test',
    TESTS: 'http://127.0.0.1:8000/tests',
    EVALUATE: 'http://127.0.0.1:8002/api/v1/check_text'
};

// Глобальные переменные
let authToken = null;
let currentUser = null;
let currentTestId = null;

// DOM элементы
const authSection = document.getElementById('auth-section');
const dashboard = document.getElementById('dashboard');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const tabs = document.querySelectorAll('.tab');
const tabPanes = document.querySelectorAll('.tab-pane');
const fileNameSpan = document.getElementById('file-name');
const textFileNameSpan = document.getElementById('text-file-name');
const fileInput = document.getElementById('file-input');
const textFileInput = document.getElementById('text-file-input');
const digitizedResult = document.getElementById('digitized-result');
const evaluationResult = document.getElementById('evaluation-result');
const generationSection = document.getElementById('generation-section');
const testsList = document.getElementById('tests-list');
const userAvatar = document.getElementById('user-avatar');
const userName = document.getElementById('user-name');
const userEmail = document.getElementById('user-email');

// setLoading(false);

// Инициализация
document.addEventListener('DOMContentLoaded', () => {

    setLoading(false);

    checkAuth();

    // Обработчики файлов
    fileInput.addEventListener('change', (e) => {
        fileNameSpan.textContent = e.target.files[0]?.name || 'Выберите файл';
    });

    textFileInput.addEventListener('change', (e) => {
        textFileNameSpan.textContent = e.target.files[0]?.name || 'Или выберите файл';
    });

    // Обработчики вкладок
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Убрать активный класс со всех вкладок
            tabs.forEach(t => t.classList.remove('active'));
            tabPanes.forEach(p => p.classList.add('hidden'));

            // Добавить активный класс текущей вкладке
            tab.classList.add('active');

            // Показать соответствующий контент
            const tabId = tab.getAttribute('data-tab');
            document.getElementById(`${tabId}-tab`).classList.remove('hidden');

            // Загрузить тесты при переходе на вкладку
            if (tabId === 'tests') {
                loadTests();
            } else if (tabId === 'take-test') {
                // Логика загрузки теста для прохождения (если нужно)
            }
        });
    });
});

function initTestBuilder() {
    document.getElementById('test-builder-init-container').classList.add('hidden');
    document.getElementById('test-builder-form').classList.remove('hidden');
    resetTestBuilder();
}

function resetTestBuilder() {
    document.getElementById('test-title').value = '';
    document.getElementById('questions-container').innerHTML = '';
    addQuestion(); // Добавляем первый вопрос по умолчанию
    currentTestId = null;
}

function cancelTest() {
    if (confirm('Вы уверены, что хотите отменить создание теста? Все изменения будут потеряны.')) {
        document.getElementById('test-builder-form').classList.add('hidden');
        document.getElementById('test-builder-init').classList.remove('hidden');
        currentTestId = null;
    }

}

async function checkAuth() {
    const token = localStorage.getItem('authToken');

    if (token) {
        try {
            // Проверяем валидность токена
            const response = await fetch(API_URLS.VERIFY, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                authToken = token;
                const userEmail = localStorage.getItem('userEmail');
                currentUser = {
                    email: userEmail,
                    name: userEmail.split('@')[0]
                };

                // Обновляем UI
                authSection.classList.add('hidden');
                dashboard.classList.remove('hidden');
                userAvatar.textContent = currentUser.name.charAt(0).toUpperCase();
                userName.textContent = currentUser.name;
                userEmail.textContent = currentUser.email;
            } else {
                // Если токен невалиден, очищаем хранилище
                localStorage.removeItem('authToken');
                localStorage.removeItem('userEmail');
            }
        } catch (error) {
            console.error('Ошибка проверки токена:', error);
        }
    }
}

// Функции аутентификации
function showRegisterForm() {
    setLoading(false);
    loginForm.classList.add('hidden');
    registerForm.classList.remove('hidden');
}

function showLoginForm() {
    setLoading(false);
    registerForm.classList.add('hidden');
    loginForm.classList.remove('hidden');
}

async function register() {
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const confirmPassword = document.getElementById('reg-confirm-password').value;

    if (!email || !password) {
        alert('Email и пароль обязательны!');
        return;
    }

    if (password !== confirmPassword) {
        alert('Пароли не совпадают!');
        return;
    }

    try {
        const response = await fetch(API_URLS.REGISTER, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка регистрации');
        }

        alert('Регистрация успешна! Теперь вы можете войти');
        showLoginForm();
    } catch (error) {
        alert(`Ошибка регистрации: ${error.message}`);
    }
}

async function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;


    try {
        const response = await fetch(API_URLS.AUTH, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка авторизации');
        }

        const data = await response.json();
        authToken = data.access_token;
        currentUser = {
            email: email,
            name: email.split('@')[0]
        };

        localStorage.setItem('authToken', authToken);
        localStorage.setItem('userEmail', email);

        // Обновить UI
        authSection.classList.add('hidden');
        dashboard.classList.remove('hidden');
        userAvatar.textContent = currentUser.name.charAt(0).toUpperCase();
        userName.textContent = currentUser.name;
        userEmail.textContent = currentUser.email;

    } catch (error) {
        alert(`Ошибка авторизации: ${error.message}`);
    }
}

function setLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    if (show == true) {
        overlay.classList = 'loading-overlay';
    } else {
        overlay.classList = 'hidden';
    }
}

function logout() {
    setLoading(false);
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('userEmail');
    dashboard.classList.add('hidden');
    authSection.classList.remove('hidden');
    document.getElementById('email').value = '';
    document.getElementById('password').value = '';
}

// Основные функции приложения
async function digitize() {
    const file = fileInput.files[0];
    if (!file) {
        alert('Пожалуйста, выберите файл');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    setLoading(true);
    try {
        const response = await fetch(API_URLS.DIGITIZE, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error('Ошибка оцифровки файла');
        }

        const result = await response.json();
        digitizedResult.innerHTML = `<div class="digitized-text">${result.text}</div>`;
    } catch (error) {
        alert(`Ошибка: ${error.message}`);
        digitizedResult.innerHTML = '<div class="notification error">Ошибка при обработке файла</div>';
    } finally {
        setLoading(false);
    }
}

async function evaluateText() {
    const text = document.getElementById('text-input').value;
    if (!text) {
        alert('Пожалуйста, введите текст');
        return;
    }
    setLoading(true);
    try {
        const response = await fetch(API_URLS.EVALUATE, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ 'prompt': text })
        });

        if (!response.ok) {
            throw new Error('Ошибка оценки текста');
        }

        const result = await response.json();

        if (result.suitable == 'yes') {
            evaluationResult.innerHTML = `
                        <div class="notification success">
                            Текст подходит для создания теста! Причина: ${result.reason} символов
                        </div>
                    `;
            generationSection.classList.remove('hidden');
        } else {
            evaluationResult.innerHTML = `
                        <div class="notification error">
                            'Текст не подходит для создания теста! Причина ${result.reason}'
                        </div>
                    `;
            generationSection.classList.add('hidden');
        }
    } catch (error) {
        alert(`Ошибка: ${error.message}`);
        evaluationResult.innerHTML = '<div class="notification error">Ошибка оценки текста</div>';
    } finally {
        setLoading(false);
    }
}

async function generateTest() {
    const text = document.getElementById('text-input').value;
    setLoading(true);
    try {
        const response = await fetch(API_URLS.GENERATE, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ 'prompt': text })
        });

        if (!response.ok) {
            throw new Error('Ошибка генерации теста');
        }

        const test = await response.json();
        // currentTestId = test.id;

        // Переключиться на конструктор тестов
        tabs.forEach(t => t.classList.remove('active'));
        tabPanes.forEach(p => p.classList.add('hidden'));

        document.querySelector('[data-tab="builder"]').classList.add('active');
        document.getElementById('builder-tab').classList.remove('hidden');

        // Загрузить сгенерированный тест в конструктор
        loadTestIntoBuilder(test);

        // Показать уведомление
        evaluationResult.innerHTML = `
                    <div class="notification success">
                        Тест успешно сгенерирован! Теперь вы можете его отредактировать.
                    </div>
                `;

    } catch (error) {
        alert(`Ошибка: ${error.message}`);
        evaluationResult.innerHTML = '<div class="notification error">Ошибка генерации теста</div>';
    } finally {
        setLoading(false);
    }
}

async function takeTest(testId) {
    try {
        const response = await fetch(`${API_URLS.TESTS}/${testId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        if (!response.ok) throw new Error('Ошибка загрузки теста');
        const test = await response.json();
        
        // Сохраните тест в глобальной переменной
        window.currentTest = test;
        
        // Переключитесь на вкладку прохождения теста
        tabs.forEach(t => t.classList.remove('active'));
        tabPanes.forEach(p => p.classList.add('hidden'));
        document.querySelector('[data-tab="take-test"]').classList.add('active');
        document.getElementById('take-test-tab').classList.remove('hidden');
        
        renderTakeTest(test);
    } catch (error) {
        alert(`Ошибка: ${error.message}`);
    }
}

function renderTakeTest(test) {
    const container = document.getElementById('take-test-content');
    container.innerHTML = '';
    
    // Блок для результата
    const resultDiv = document.createElement('div');
    resultDiv.id = 'test-result';
    container.appendChild(resultDiv);
    
    // Заголовок теста
    const title = document.createElement('h3');
    title.textContent = test.title || 'Без названия';
    title.style.marginBottom = '20px';
    container.appendChild(title);
    
    // Вопросы
    test.questions.forEach((question, qIndex) => {
        const card = document.createElement('div');
        card.className = 'question-card';
        
        card.innerHTML = `
            <h4>Вопрос ${qIndex + 1}</h4>
            <p>${question.question}</p>
        `;
        
        // Варианты ответов
        question.ans.forEach((answer, aIndex) => {
            const answerDiv = document.createElement('div');
            answerDiv.className = 'answer-option';
            answerDiv.innerHTML = `
                <input type="radio" name="q${qIndex}" id="q${qIndex}-a${aIndex}" value="${answer}">
                <label for="q${qIndex}-a${aIndex}">${answer}</label>
            `;
            card.appendChild(answerDiv);
        });
        
        container.appendChild(card);
    });
    
    // Кнопка отправки
    const submitBtn = document.createElement('button');
    submitBtn.className = 'btn btn-success submit-results';
    submitBtn.textContent = 'Отправить ответы';
    submitBtn.onclick = () => submitAnswers(test.id);
    container.appendChild(submitBtn);
}

function submitAnswers(testId) {
    const questionsContainer = document.getElementById('take-test-content');
    const resultDiv = document.getElementById('test-result');
    const correctAnswers = window.currentTest.questions.map(q => q.correct);
    const userAnswers = [];
    
    // Сбор ответов пользователя
    questionsContainer.querySelectorAll('.question-card').forEach((card, index) => {
        const selected = card.querySelector(`input[name="q${index}"]:checked`);
        userAnswers.push(selected ? selected.value : null);
    });
    
    // Проверка наличия ответов
    if (userAnswers.every(answer => answer === null)) {
        alert('Выберите хотя бы один ответ');
        return;
    }
    
    setLoading(true);
    
    try {
        // Расчет результата
        let correctCount = 0;
        userAnswers.forEach((answer, index) => {
            if (answer === correctAnswers[index]) {
                correctCount++;
            }
        });
        const score = (correctCount / correctAnswers.length) * 100;
        
        // Отображение результата
        resultDiv.innerHTML = `
            <div class="notification success">
                <h4>Ваш результат: ${score.toFixed(2)}%</h4>
                <p>Правильных ответов: ${correctCount} из ${correctAnswers.length}</p>
            </div>
        `;
        
        // Подсветка правильных/неправильных ответов
        questionsContainer.querySelectorAll('.question-card').forEach((card, index) => {
            const options = card.querySelectorAll('.answer-option');
            options.forEach(option => {
                const radio = option.querySelector('input[type="radio"]');
                const label = option.querySelector('label');
                
                if (radio.value === correctAnswers[index]) {
                    label.style.color = 'green';
                    label.style.fontWeight = 'bold';
                }
                
                if (radio.checked) {
                    if (radio.value === correctAnswers[index]) {
                        label.style.backgroundColor = '#d4edda'; // Успешный ответ
                    } else {
                        label.style.backgroundColor = '#f8d7da'; // Ошибочный ответ
                    }
                }
            });
            
            // Блокировка дальнейших изменений
            const radios = card.querySelectorAll('input[type="radio"]');
            radios.forEach(radio => {
                radio.disabled = true;
            });
        });
        
        // Отключить кнопку отправки
        document.querySelector('.submit-results').disabled = true;
    } catch (error) {
        alert(`Ошибка: ${error.message}`);
    } finally {
        setLoading(false);
    }
}



async function loadTests() {
    // const token = localStorage.getItem('authToken');
    try {
        const response = await fetch(API_URLS.TESTS, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (!response.ok) {
            throw new Error('Ошибка загрузки тестов');
        }

        const data = await response.json(); // Получаем весь объект ответа
        const tests = data.tests; // Извлекаем массив тестов

        if (!tests || tests.length === 0) {
            testsList.innerHTML = '<div class="notification">У вас пока нет тестов</div>';
            return;
        }

        tests.sort((a, b) => {
            const dateA = new Date(a.test_metadata.created_at);
            const dateB = new Date(b.test_metadata.created_at);
            return dateB - dateA; // Для сортировки по убыванию (новые сначала)
        });

        testsList.innerHTML = '';
        tests.forEach(test => {
            // Извлекаем метаданные теста
            const metadata = test.test_metadata;

            // Создаем элемент теста
            const testElement = document.createElement('div');
            testElement.className = 'card';

            // Используем данные из метаданных
            testElement.innerHTML = `
                <div class="card-header">
                    <div class="card-title">${metadata.title || 'Без названия'}</div>
                    <div class="card-actions">
                        <button onclick="takeTest('${test.id}')">▶️ Пройти</button>
                        <button onclick="editTest('${test.id}')">✏️</button>
                        <button onclick="deleteTest('${test.id}')">🗑️</button>
                    </div>
                </div>
                <div>${metadata.questions_count || 0} вопросов</div>
                <div>Создан: ${metadata.created_at ? new Date(metadata.created_at).toLocaleDateString() : 'дата неизвестна'}</div>
            `;

            testsList.appendChild(testElement);
        });

    } catch (error) {
        testsList.innerHTML = `
            <div class="notification error">
                Ошибка загрузки тестов: ${error.message}
            </div>
        `;
    }
}

function loadTestIntoBuilder(test) {
    document.getElementById('test-builder-init').classList.add('hidden');
    document.getElementById('test-builder-form').classList.remove('hidden');
    document.getElementById('test-title').value = test.title;
    const container = document.getElementById('questions-container');
    container.innerHTML = '';

    test.questions.forEach((question, index) => {
        const questionElement = document.createElement('div');
        questionElement.className = 'question-item';
        questionElement.innerHTML = `
            <div class="form-group">
                <label>Вопрос ${index + 1}</label>
                <textarea class="form-control" placeholder="Текст вопроса">${question.question}</textarea>
            </div>
            <div class="form-group">
                <label>Варианты ответов</label>
                <div id="answers-${index}"></div>
            </div>
        `;
        container.appendChild(questionElement);

        const answersContainer = document.getElementById(`answers-${index}`);
        // Группа радиокнопок с уникальным именем для вопроса
        const radioGroupName = `correct-answer-${index}`;

        question.ans.forEach((answerText, ansIndex) => {
            const answerElement = document.createElement('div');
            answerElement.className = 'answer-item';

            // Проверяем, совпадает ли ответ с правильным вариантом
            const isChecked = answerText === question.correct;

            answerElement.innerHTML = `
                <input type="text" class="form-control" value="${answerText}" placeholder="Ответ ${ansIndex + 1}">
                <input type="radio" name="${radioGroupName}" ${isChecked ? 'checked' : ''}>
                <span>Правильный ответ</span>
            `;
            answersContainer.appendChild(answerElement);
        });
    });
    document.getElementById('test-builder-init-container').classList.add('hidden');
}

function addQuestion() {
    const container = document.getElementById('questions-container');
    const count = container.children.length;
    const questionId = Date.now();

    const questionElement = document.createElement('div');
    questionElement.className = 'question-item';
    questionElement.innerHTML = `
                <div class="card-header">
                    <div class="card-title">Вопрос ${count + 1}</div>
                    <div class="card-actions">
                        <button onclick="this.closest('.question-item').remove()">🗑️</button>
                    </div>
                </div>
                <div class="form-group">
                    <textarea class="form-control" placeholder="Текст вопроса"></textarea>
                </div>
                <div class="form-group">
                    <label>Варианты ответов (выберите один правильный)</label>
                    ${Array.from({ length: 4 }, (_, i) => `
                        <div class="answer-item">
                            <input type="text" class="form-control" placeholder="Ответ ${i + 1}">
                            <input type="radio" name="correct-${questionId}"> Правильный
                        </div>
                    `).join('')}
                </div>
            `;
    container.appendChild(questionElement);
}

async function saveTest() {
    const title = document.getElementById('test-title').value;
    if (!title) {
        alert('Введите название теста');
        return;
    }

    var questions = [];
    const questionElements = document.querySelectorAll('.question-item');
    // console.log(questionElements)
    questionElements.forEach((qElement, index) => {
        const text = qElement.querySelector('textarea').value;
        var answers = [];
        var correct_ans = "";
        qElement.querySelectorAll('.answer-item').forEach(aElement => {
            const answerText = aElement.querySelector('input[type="text"]').value;
            answers.push(answerText);
            if (aElement.querySelector('input[type="radio"]').checked) {
                correct_ans = aElement.querySelector('input[type="text"]').value;
            }
        });

        questions.push({
            question: text,
            ans: answers,
            correct: correct_ans
        });
    });

    const testData = {
        title,
        questions
    };

    // console.log(testData)

    try {
        const method = currentTestId ? 'PUT' : 'POST';
        const url = currentTestId ? `${API_URLS.TESTS}/${currentTestId}` : API_URLS.TESTS;

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(testData)
        });

        if (!response.ok) {
            throw new Error('Ошибка сохранения теста');
        }

        alert('Тест успешно сохранен!');
        loadTests(); // Обновить список тестов
        currentTestId = null;

    } catch (error) {
        alert(`Ошибка сохранения теста: ${error.message}`);
    }
}

function cancelTest() {
    if (confirm('Вы уверены, что хотите отменить создание теста? Все изменения будут потеряны.')) {

        document.getElementById('test-builder-form').classList.add('hidden');
        document.getElementById('test-builder-init-container').classList.remove('hidden');
        document.getElementById('question-container').innerHTML = '';
        currentTestId = null;
    }
}

async function editTest(testId) {
    // Здесь должна быть реализация загрузки теста из API
    // Для примера создадим тест-заглушку
    try {
        const method = 'GET';
        const url = `${API_URLS.TESTS}/${testId}`;

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
        });

        if (!response.ok) {
            throw new Error('Ошибка сохранения теста');
        }

        tabs.forEach(t => t.classList.remove('active'));
        tabPanes.forEach(p => p.classList.add('hidden'));

        document.querySelector('[data-tab="builder"]').classList.add('active');
        document.getElementById('builder-tab').classList.remove('hidden');
        // console.log);
        const test = await response.json();
        // Загрузить тест в конструктор
        currentTestId = testId;
        loadTestIntoBuilder(test);

    } catch (error) {
        alert(`Ошибка редактирования теста: ${error.message}`);
    }



    // Переключиться на конструктор

}

async function deleteTest(testId) {
    if (!confirm('Вы уверены, что хотите удалить этот тест?')) return;

    try {
        const response = await fetch(`${API_URLS.TESTS}/${testId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (!response.ok) {
            throw new Error('Ошибка удаления теста');
        }

        loadTests(); // Обновить список тестов

    } catch (error) {
        alert(`Ошибка удаления теста: ${error.message}`);
    }
}
// Добавьте в конец скрипта
document.getElementById('text-input').addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});