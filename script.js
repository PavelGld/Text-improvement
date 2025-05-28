// Ожидаем полной загрузки DOM перед началом работы
document.addEventListener('DOMContentLoaded', () => {
    // Получаем ссылки на элементы DOM
    const sourceTextarea = document.getElementById('source-text');
    const targetTextarea = document.getElementById('target-text');
    const translateButton = document.getElementById('translate-button');
    const translationStyleSelect = document.getElementById('translation-style');
    const sourceLanguageInput = document.getElementById('source-language'); // Теперь это select
    const targetLanguageInput = document.getElementById('target-language'); // Теперь это select
    const llmModelSelect = document.getElementById('llm-model');

    // Получаем все кнопки копирования
    const copyButtons = document.querySelectorAll('.copy-button');

    // Добавляем обработчик события клика на кнопку перевода
    translateButton.addEventListener('click', async () => {
        const sourceText = sourceTextarea.value;
        const selectedStyle = translationStyleSelect.value;
        const sourceLanguage = sourceLanguageInput.value; // Получаем значение из select
        const targetLanguage = targetLanguageInput.value; // Получаем значение из select
        const selectedModel = llmModelSelect.value;

        // Проверяем, введен ли текст для перевода
        if (sourceText.trim() === '') {
            targetTextarea.value = 'Пожалуйста, введите текст для перевода.';
            return;
        }

        // Устанавливаем статус "Перевожу..." в поле вывода
        targetTextarea.value = 'Перевожу...';

        try {
            // Отправляем POST запрос на бэкенд Flask для перевода
            const response = await fetch('http://127.0.0.1:5000/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: sourceText,
                    style: selectedStyle,
                    source_language: sourceLanguage,
                    target_language: targetLanguage,
                    model: selectedModel
                }),
            });

            // Проверяем статус ответа
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`Ошибка HTTP! Статус: ${response.status}. ${errorData.error || response.statusText}`);
            }

            // Парсим JSON ответ и отображаем переведенный текст
            const data = await response.json();
            targetTextarea.value = data.translatedText;

        } catch (error) {
            // Обрабатываем ошибки при запросе и отображаем их
            console.error('Ошибка при выполнении перевода:', error);
            targetTextarea.value = `Произошла ошибка при переводе: ${error.message}`;
        }
    });

    // Добавляем обработчики событий для кнопок копирования
    copyButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetId = button.dataset.target; // Получаем ID целевого текстового поля
            const targetTextarea = document.getElementById(targetId);
            
            if (targetTextarea) {
                // Копируем текст в буфер обмена
                navigator.clipboard.writeText(targetTextarea.value).then(() => {
                    // Можно добавить визуальную обратную связь, например, изменение текста кнопки
                    button.textContent = 'Скопировано!';
                    setTimeout(() => {
                        button.textContent = 'Копировать';
                    }, 1500); // Возвращаем исходный текст кнопки через 1.5 секунды
                }).catch(err => {
                    console.error('Ошибка при копировании текста: ', err);
                });
            }
        });
    });
}); 