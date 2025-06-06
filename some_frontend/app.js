const API_URLS = {
            AUTH: 'http://127.0.0.1:8000/auth',
            REGISTER: 'http://127.0.0.1:8000/register', // Новый эндпоинт для регистрации
            DIGITIZE: 'http://your-digitizer/digitize',
            GENERATE: 'http://your-test-generator/generate'
        };

        let authToken = null;

        // Переключение между формами
        function showRegisterForm() {
            document.getElementById('login-form').classList.add('hidden');
            document.getElementById('register-form').classList.remove('hidden');
        }

        function showLoginForm() {
            document.getElementById('register-form').classList.add('hidden');
            document.getElementById('login-form').classList.remove('hidden');
        }

        // Функция регистрации
        async function register() {
            const password = document.getElementById('reg-password').value;
            const confirmPassword = document.getElementById('reg-confirm-password').value;
            const email = document.getElementById('reg-email').value;

            // Валидация
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
                    body: JSON.stringify({ 
                        email, 
                        password
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Ошибка регистрации');
                }

                const data = await response.json();
                alert('Регистрация успешна! Теперь вы можете войти');
                showLoginForm();
            } catch (error) {
                alert(`Ошибка регистрации: ${error.message}`);
            }
        }

        // Остальные функции (login, digitize, generateTest) остаются как были
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
                authToken = data.acces_token;
                document.getElementById('auth-section').classList.add('hidden');
                document.getElementById('main-section').classList.remove('hidden');
            } catch (error) {
                alert(`Ошибка авторизации: ${error.message}`);
            }
        }

        async function digitize() {
            const text = document.getElementById('text-input').value;
            
            try {
                const response = await fetch(API_URLS.DIGITIZE, {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`
                    },
                    body: JSON.stringify({ text })
                });
                
                const result = await response.json();
                document.getElementById('digitized-result').innerHTML = `
                    <h4>Результат:</h4>
                    <p>${result.digitizedText}</p>
                `;
            } catch (error) {
                alert('Ошибка оцифровки');
            }
        }

        async function generateTest() {
            try {
                const response = await fetch(API_URLS.GENERATE, {
                    method: 'GET',
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                
                const test = await response.json();
                document.getElementById('test-result').innerHTML = `
                    <h4>Тест:</h4>
                    <pre>${JSON.stringify(test, null, 2)}</pre>
                `;
            } catch (error) {
                alert('Ошибка генерации теста');
            }
        }

        // Функция выхода
        function logout() {
            authToken = null;
            document.getElementById('main-section').classList.add('hidden');
            document.getElementById('auth-section').classList.remove('hidden');
            document.getElementById('username').value = '';
            document.getElementById('password').value = '';
        }