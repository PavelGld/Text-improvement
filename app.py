# Импортируем необходимые библиотеки
import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Загружаем переменные окружения из файла .env
load_dotenv()

# Инициализируем Flask приложение
app = Flask(__name__)
# Включаем поддержку CORS для всех источников (для разработки)
CORS(app)

# Получение API ключа OpenRouter из переменных окружения
# Рекомендуется использовать переменные окружения для безопасного хранения ключей
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
# Добавляем получение OPENROUTER_BASE_URL из .env или используем значение по умолчанию
OPENROUTER_BASE_URL = os.environ.get('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')

# Проверка наличия API ключа при запуске
if not OPENROUTER_API_KEY:
    print("Ошибка: Переменная окружения 'OPENROUTER_API_KEY' не установлена.")
    print("Пожалуйста, установите ее перед запуском сервера.")
    # В реальном приложении здесь можно выйти или предпринять другие действия

# Определяем маршрут для обработки POST запросов на перевод
@app.route('/translate', methods=['POST'])
def translate_text():
    # Проверяем наличие API ключа перед обработкой запроса
    if not OPENROUTER_API_KEY:
        return jsonify({"error": "OpenRouter API key is not configured."}), 500

    # Получаем данные из JSON запроса от фронтенда
    data = request.json
    text_to_translate = data.get('text')
    style = data.get('style')
    source_language = data.get('source_language')
    target_language = data.get('target_language')
    selected_model = data.get('model', "google/gemini-2.0-flash-001") # Получаем выбранную модель, по умолчанию Gemini

    # Проверяем, что текст для перевода был предоставлен
    if not text_to_translate:
        return jsonify({"error": "No text provided for translation."}), 400

    # Формирование промпта в зависимости от стиля и выбранных языков
    # Используем коды языков (например, 'ru', 'en')
    style_instructions = {
        "formal": f"Переведи следующий текст с {source_language} на {target_language} в формальном стиле:",
        "informal": f"Переведи следующий текст с {source_language} на {target_language} в неформальном стиле:",
        "business": f"Переведи следующий текст с {source_language} на {target_language} в стиле делового письма:",
        "flirt": f"Переведи следующий текст с {source_language} на {target_language} в стиле флирта:"
    }

    # Системное сообщение для модели: указывает роль и общие инструкции
    # Изменено: добавляем в промпт инструкцию возвращать только один перевод и указываем языки
    system_message_content = f"Ты профессиональный переводчик. Переведи предоставленный текст с {source_language} на {target_language}. Предоставь только один вариант перевода без дополнительных комментариев или форматирования (например, списков)."
    
    # Пользовательское сообщение для модели: содержит текст для перевода и инструкции по стилю
    user_message_content = f"{style_instructions.get(style, f'Переведи следующий текст с {source_language} на {target_language}:')}\n\n{text_to_translate}\n\nПеревод:"

    # Используем LangChain для взаимодействия с OpenRouter
    try:
        # Инициализируем модель ChatOpenAI с параметрами от пользователя и ключом API
        llm = ChatOpenAI(
            model=selected_model,
            openai_api_key=OPENROUTER_API_KEY,
            openai_api_base=OPENROUTER_BASE_URL,
            temperature=0.7,
            # max_tokens=150, # Можно ограничить количество токенов, если нужно
            # headers={
            #    "HTTP-Referer": "ВАШ_URL_САЙТА", # Замените на URL вашего сайта, если есть
            #    "X-Title": "AI Translator App" # Замените на название вашего приложения
            # }
        )

        # Создаем список сообщений в формате, понятном LangChain и моделям (System, User)
        messages = [
            SystemMessage(content=system_message_content),
            HumanMessage(content=user_message_content)
        ]

        # Выполняем запрос к LLM
        response = llm.invoke(messages)

        # Извлекаем переведенный текст из ответа и удаляем лишние пробелы
        translated_text = response.content.strip()

        # Возвращаем переведенный текст в формате JSON
        return jsonify({"translatedText": translated_text})

    except Exception as e: # Перехватываем более общее исключение для обработки ошибок API или LangChain
        # Логируем ошибку на сервере
        print(f"Ошибка при выполнении запроса к LLM через LangChain: {e}")
        # Возвращаем ошибку фронтенду
        return jsonify({"error": f"Ошибка при выполнении запроса к API перевода: {e}"}), 500

# Точка входа для запуска приложения
if __name__ == '__main__':
    # Запуск Flask приложения
    # debug=True полезно для разработки, но должно быть отключено в production
    app.run(debug=True) 