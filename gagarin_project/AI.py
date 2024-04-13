import requests
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import nltk
import urllib.parse
import joblib
from googleapiclient.discovery import build

# Загрузка необходимых ресурсов для nltk
nltk.download('punkt')
nltk.download('stopwords')

# Препроцессинг данных
def preprocess_text(text):
    text = text.lower()
    text = text.replace('\n', ' ')
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('russian'))
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)

# Функция для получения ссылек на статьи через Google Custom Search API
def get_links_google(query, api_key, cx):
    url = f"https://www.googleapis.com/customsearch/v1?q={urllib.parse.quote(query)}&key={api_key}&cx={cx}"
    response = requests.get(url)
    data = response.json()
    links = [item['link'] for item in data.get('items', [])]
    return links

# Функция для получения ссылок на видеоролики через YouTube Data API
def search_youtube_videos(query, api_key, max_results=5):
    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.search().list(
        part='snippet',
        q=query,
        type='video',
        maxResults=max_results
    )
    
    response = request.execute()
    videos = response['items']
    
    video_links = []
    for video in videos:
        video_id = video['id']['videoId']
        video_link = f'https://www.youtube.com/watch?v={video_id}'
        video_links.append(video_link)
    
    return video_links

# Модифицированная функция рекомендации статей с добавлением поиска ссылок в интернете
def recommend_articles_with_links(topic_label, query, api_key, cx, preprocessed_articles, kmeans):
    article_indices = [i for i, label in enumerate(kmeans.labels_) if label == topic_label]
    recommended_article_link = None
    recommended_video_link = None
    for i in article_indices:
        topic = preprocessed_articles[i]
        if topic == preprocess_text(query):
            print("Тема найдена в файле data_set.txt из первого файла.")
            return recommended_article_link, recommended_video_link
    links = get_links_google(query, api_key, cx)
    for link in links:
        if "article" in link or "post" in link or "blog" in link:
            if not recommended_article_link:
                recommended_article_link = link
        elif "youtube.com" in link:
            if not recommended_video_link:
                recommended_video_link = link
    return recommended_article_link, recommended_video_link

# Загрузка данных из первого файла
data_file_path = r"C:\Users\ivano\OneDrive\Рабочий стол\gagarin_khakaton\gagarin_project\data_set\data_set.txt"
youtube_api_key = ""  # Вставьте ваш ключ YouTube API здесь
try:
    with open(data_file_path, "r", encoding="utf-8") as file:
        articles_data = file.read()

    # Предобработка данных из первого файла
    preprocessed_articles = [preprocess_text(paragraph) for paragraph in articles_data.splitlines() if paragraph.strip()]

    # Векторизация текста с использованием TF-IDF из первого файла
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(preprocessed_articles)

    # Кластеризация статей и видеороликов по темам с использованием K-means из первого файла
    kmeans = KMeans(n_clusters=10, random_state=30)
    kmeans.fit(X)

    # Оценка качества кластеризации из первого файла
    silhouette_avg_1 = silhouette_score(X, kmeans.labels_)
    print("Средняя оценка силуэта из первого файла:", silhouette_avg_1)
    print("Количество статей в data-set:", len(preprocessed_articles))
    # Пример использования модели
    user_subject = input("Введите предмет: ")
    user_topic = input("Введите тему: ")
        
    # API ключ и идентификатор поисковой системы Google Custom Search
    api_key = ""
    cx = ""

    # Функция для предсказания темы по введенным данным пользователя
    def predict_topic(user_input):
        user_input_processed = preprocess_text(user_input)
        user_input_vectorized = vectorizer.transform([user_input_processed])
        cluster_label = kmeans.predict(user_input_vectorized)[0]
        return cluster_label

    # Проверяем, есть ли введенная тема в файле data_set.txt из первого файла
    if user_topic in articles_data:
        print("Тема найдена в файле data_set.txt из первого файла.")
        preprocessed_user_topic = preprocess_text(user_topic)
        user_topic_index = [i for i, line in enumerate(preprocessed_articles) if line == preprocessed_user_topic]
        if user_topic_index: 
            predicted_label = kmeans.labels_[user_topic_index[0]]
            print("Предсказанная тема:", predicted_label)
    else:
        print("Тема не найдена в файле data_set.txt из первого файла.")
        predicted_label = predict_topic(user_topic)
        recommended_article_link, recommended_video_link = recommend_articles_with_links(predicted_label, user_topic, api_key, cx, preprocessed_articles, kmeans)
        # Поиск статьи и видеоролика
        if recommended_article_link or recommended_video_link:
            print("Да конечно вот самые лучшие статьи, видеоролики, курсы по мнению пользователей статья:", recommended_article_link if recommended_article_link else 'None', "видеоролик:", recommended_video_link if recommended_video_link else 'None')
        else:
            print("Статьи и видеоролики на данную тему не найдены.")

        
        # Поиск видеороликов на YouTube
        if recommended_video_link is None:
            video_query = user_topic  # Можно использовать другой запрос
            youtube_video_links = search_youtube_videos(video_query, youtube_api_key)
            print("Найденные видеоролики YouTube:")
            for link in youtube_video_links:
                print(link) 

except FileNotFoundError:
    print("Файл data_set.txt из первого файла не найден. Будет выполнен поиск в интернете.")

# Сохранение и загрузка модели
def save_model(model, filename):
    joblib.dump(model, filename)

def load_model(filename):
    return joblib.load(filename)

# Функция для обновления модели с новыми данными
def update_model(new_data, model):
    # Предобработка новых данных
    preprocessed_new_data = [preprocess_text(paragraph) for paragraph in new_data.splitlines() if paragraph.strip()]
    # Добавление новых данных к текущим данным
    preprocessed_articles.extend(preprocessed_new_data)
    # Переобучение модели на обновленных данных
    X_updated = vectorizer.fit_transform(preprocessed_articles)
    model.fit(X_updated)
    return model

# Загрузка данных из файла
def load_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# Загрузка текущей модели или создание новой, если она отсутствует
def load_or_create_model(model_file):
    try:
        return load_model(model_file)
    except FileNotFoundError:
        model = KMeans(n_clusters=40, random_state=50)
        model.fit(X)
        save_model(model, model_file)
        return model

# Загрузка данных из файла
# Загрузка данных из файла
articles_data = load_data(data_file_path)

# Предобработка данных из файла
preprocessed_articles = [preprocess_text(paragraph) for paragraph in articles_data.splitlines() if paragraph.strip()]

# Загрузка или создание модели
kmeans = load_or_create_model("model.pkl")

# Обновление модели с новыми данными
kmeans = update_model(articles_data, kmeans)

# Сохранение обновленной модели
save_model(kmeans, "model.pkl")
