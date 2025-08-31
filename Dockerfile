FROM python:3.13-alpine

RUN echo "http://mirrors.tuna.tsinghua.edu.cn/alpine/v3.22/main" > /etc/apk/repositories \
    && echo "http://mirrors.tuna.tsinghua.edu.cn/alpine/v3.22/community" >> /etc/apk/repositories \
    && apk update \
    && apk upgrade \
    && apk add --no-cache gcc musl-dev libffi-dev
WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]