# Создать образ на основе базового слоя,
# который содержит файлы ОС и интерпретатор Python 3.9.
FROM python:3.11

# Переходим в образе в директорию /app: в ней будем хранить код проекта.
# Если директории с указанным именем нет, она будет создана. 
# Название директории может быть любым.
WORKDIR /app
# Дальнейшие инструкции будут выполняться в директории /app

# Скопировать с локального компьютера файл зависимостей
# в текущую директорию (текущая директория — это /app).
COPY requirements.txt .

# Выполнить в текущей директории команду терминала
# для установки зависимостей.
RUN pip install gunicorn

RUN pip install -r requirements.txt --no-cache-dir

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable



# set display port to avoid crash
ENV DISPLAY=:99

# Скопировать всё необходимое содержимое 
# той директории локального компьютера, где сохранён Dockerfile,
# в текущую рабочую директорию образа — /app.
COPY . .

# При старте контейнера запустить сервер разработки.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "engineering_tools.wsgi"] 