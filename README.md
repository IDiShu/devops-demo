# DevOps CI/CD с Docker и Kubernetes

Этот проект демонстрирует полный цикл CI/CD с использованием **Docker**, **Kubernetes (Minikube)** и **GitHub Actions** с автодеплоем в кластер.

## 📂 Структура проекта

```
k8s-demo/
 ├── .github/workflows/     # CI/CD pipeline
 ├── k8s/                   # Kubernetes манифесты (base + overlays)
 ├── mydocker/              # Docker приложение (app.py / Dockerfile / compose)
 ├── tls.crt / tls.key      # TLS сертификат для ingress
```

## 🚀 Что реализовано

* Build & Push Docker image в Docker Hub при **git push**
* Авто деплой в Kubernetes через self-hosted GitHub Runner
* Kustomize overlays: **dev** и **prod**
* StatefulSet PostgreSQL с PVC/PV
* Traefik ingress + HTTPS

## 🛠 Технологии

* **Docker / Docker Hub**
* **Kubernetes + Minikube + kubectl + kustomize**
* **GitHub Actions (self-hosted runner)**
* **Kustomize overlays** (dev/prod)

## 📦 CI Pipeline (`build.yml`)

* логин в Docker Hub
* сборка Docker образа из `/mydocker`
* пуш в `DOCKERHUB_USERNAME/devops-demo:latest`

## 🚢 CD Pipeline (`deploy-dev.yml`)

* sed → обновление image тегов
* `kubectl apply -k ./k8s/overlays/dev`
* ожидание деплоя через rollout

## ✅ Результат

Полностью рабочий **CI/CD с GitHub → Kubernetes**, без ручного деплоя.
Просто пушишь в `master` → **приложение само обновляется в Minikube**.

---

Добавить раздел «Установка и запуск»?

## 📥 Установка и подготовка окружения (пошагово для новичка)

Ничего не пропускаем, всё делаем по порядку — просто копируй и выполняй команды.
Полностью автоматизируем процесс от создания репозитория до первого автодеплоя.

### Шаг 0 — GitHub репозиторий

Создайте публичный репозиторий, обязательно с файлом README.

### Шаг 1 — Docker Hub

Создание учётки и токена для пуша образов.

### Шаг 2 — GitHub PAT с правами `repo` и `workflow`

Используется как пароль при `git push`.

### Шаг 3 — Инициализация проекта и первый push

```bash
git init
git remote add origin https://github.com/USER/devops-demo.git
git add .
git commit -m "initial commit"
git push -u origin master
```

### Шаг 4 — Добавление secrets в GitHub

`DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`

### Шаг 5 — CI: `.github/workflows/build.yml`

Сборка и публикация Docker-образа.

### Шаг 6 — Подключение self-hosted GitHub Runner

Устанавливается прямо на Ubuntu с Minikube.

### Шаг 7 — CD workflow: авторазвёртывание в Kubernetes

```yaml
kubectl apply -k ./k8s/overlays/dev
kubectl rollout status ...
```

## ⚠️ Типовые ошибки и решения

* `ImagePullBackOff` — приватный образ или неправильный тег
* `permission denied` — перенеси kubeconfig из root → user
* патчи не срабатывают — следи за `nameSuffix`

## 📂 Пример структуры проекта

```
k8s-demo/
 ├── .github/workflows/deploy.yml
 ├── k8s/
 │   ├── base/
 │   └── overlays/
 │        ├── dev/
 │        └── prod/
```

CI/CD **всегда запускается внутри** `k8s-demo`, поэтому в workflow нельзя писать путь `k8s-demo/k8s/...`, только `./k8s/...`.

---

## 📄 Пример GitHub Actions (deploy.yml)

```yaml
name: Deploy to Kubernetes (Dev)
...
```

(будет развёрнуто ниже автоматически)

---

## ✅ Финальный результат

GitHub Actions полностью автоматизирует деплой приложения в Kubernetes при каждом пуше в master.

---

Если нужно — добавлю секцию "Как проверить работу (curl + ingress + traefik)".

---

# 🔥 ПОЛНЫЙ ГАЙД ДЛЯ ПОЛНОГО НОВИЧКА (ДЕЛАЙ ШАГ ЗА ШАГОМ, НЕ ПЕРЕСКАКИВАЙ)

⚠️ Представь, что ты вообще НИЧЕГО не знаешь. Здесь всё объяснено так, чтобы было невозможно запутаться.
⚠️ Просто выполняй шаги последовательно. Не думай, просто делай.

---

## ШАГ 0 — СОЗДАЁМ РЕПОЗИТОРИЙ НА GITHUB

(этот шаг обязателен, без него вообще ничего не будет работать)

1. Открой сайт: **[https://github.com](https://github.com)**
2. Нажми сверху кнопку **New → Create new repository**
3. Заполни:

   * **Repository name:** `devops-demo`
   * **Public** ← ОБЯЗАТЕЛЬНО (чтобы Docker Hub работал без ошибок)
   * ✅ **галочку «Add a README file» ОБЯЗАТЕЛЬНО включить**
4. Нажми **Create repository**

✅ Готово. У тебя теперь есть пустой репозиторий. Мы будем в него пушить код.

(дальше я продолжу ШАГ 1 — Docker Hub, полностью по твоему файлу, в стиле как сейчас)

Отлично, продолжаем.

---

## ШАГ 1 — СОЗДАЁМ АККАУНТ И ТОКЕН В DOCKER HUB (ОБЯЗАТЕЛЬНО)

Docker Hub — это место, куда GitHub Actions будет отправлять (публиковать) твой Docker-образ.

### 1.1. Заходим на Docker Hub

Открываем сайт: **[https://hub.docker.com](https://hub.docker.com)**

* Если у тебя уже есть аккаунт — просто войди
* Если НЕТ — нажми **Sign up** и зарегистрируйся (это бесплатно)

### 1.2. Создаём токен (как пароль для GitHub Actions)

1. Нажми на аватарку в правом верхнем углу → **Account Settings**
2. Слева выбери **Security → New Access Token**
3. Назови токен, например: `gha-push`
4. Нажми **Create**
5. Очень важно: **СКОПИРУЙ токен** — если закроешь окно, второй раз не покажут

✅ Готово. Мы сохранили токен — скоро его вставим в GitHub.

---

## (готов перейти к ШАГУ 2 — GitHub Token, как в твоём тексте)

## ШАГ 2 — СОЗДАЁМ GITHUB TOKEN (PAT) С ПРАВАМИ `repo` И `workflow`

Этот токен нужен, чтобы GitHub разрешил нам пушить код и запускать GitHub Actions.
Без него CI/CD НЕ ЗАРАБОТАЕТ.

### 2.1. Открываем настройки GitHub

1. Зайди на [https://github.com](https://github.com)
2. ВПРАВО ВВЕРХУ нажми на аватар → **Settings**
3. В ЛЕВОМ МЕНЮ ЛИСТАЕМ ВНИЗ → **Developer settings**
4. Далее → **Personal access tokens → Tokens (classic)**
5. Нажимаем **Generate new token → Generate new token (classic)**

### 2.2. Заполняем форму

* **Note** → напиши: `ci-workflow`
* ВАЖНО: включи галочки ✅

  * `repo`
  * `workflow` ← БЕЗ НЕЁ AUTO-DEPLOY НЕ ЗАРАБОТАЕТ!

Нажимаем **Generate token** и СРАЗУ КОПИРУЕМ токен.
➡️ Как и в Docker Hub — второй раз GitHub его НЕ ПОКАЖЕТ.

✅ Отлично! Теперь у нас есть 2 секрета: Docker Hub Token и GitHub Token. Мы вставим их позже в репозиторий.

---

**## ШАГ 3 — ПЕРВЫЙ PUSH ПРОЕКТА В GITHUB
Теперь мы загрузим весь ваш проект в GitHub вручную.

### 3.1. Переходим в папку проекта на Ubuntu

```bash
cd ~/k8s-demo
```

(именно туда, где лежат папки `k8s/`, `mydocker/`, `.github/` и т.д.)

### 3.2. Выполняем команды ПО ОДНОЙ (в точности):

```bash
git init
git remote add origin https://github.com/ТВОЙ_USERNAME/devops-demo.git
git add .
git commit -m "initial commit"
git push -u origin master
```

### 3.3. ВОЗМОЖНЫЙ ВОПРОС: "Author identity unknown"

Решение (выполнить и повторить commit):

```bash
git config --global user.email "ТВОЙ_EMAIL@пример.com"
git config --global user.name "ТВОЙ_GITHUB_USERNAME"
```

### 3.4. При push GitHub попросит ЛОГИН + ПАРОЛЬ

* Логин = твой логин GitHub (в точности, с учётом заглавных букв)
* Пароль = **GitHub Token из ШАГА 2**, НЕ пароль от аккаунта

✅ Если видишь `Enumerating objects...`, `Writing objects...`, `branch 'master' set up to track` — значит ВСЁ УСПЕШНО.

---

## ШАГ 4 — ПОДКЛЮЧАЕМ Docker Hub К GitHub (SECRETS)

Теперь мы подключим Docker Hub токены напрямую в репозиторий.

1. Открой GitHub → зайди в свой **репозиторий** (devops-demo)
2. Вверху нажми **Settings**
3. Слева → **Secrets and variables → Actions**
4. Нажми зелёную кнопку **New repository secret**

Создаём ДВА секрета:

* `DOCKERHUB_USERNAME` → твой логин Docker Hub
* `DOCKERHUB_TOKEN` → тот токен, что создали в ШАГЕ 1.2

✅ ГОТОВО. Docker Hub подключён.

---

## ШАГ 5 — СОЗДАЁМ CI (BUILD & PUSH DOCKER IMAGE)

Мы создаём файл: `.github/workflows/build.yml`

```bash
mkdir -p .github/workflows
nano .github/workflows/build.yml
```

Вставляем ПОЛНОСТЬЮ (не менять):

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: ["master", "main"]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v6
        with:
          context: ./mydocker
          push: true
          tags: |
            ${{ secrets.DOCKERHUB_USERNAME }}/devops-demo:latest
```

СОХРАНЯЕМ: `CTRL + O → ENTER → CTRL + X`

---

(готов перейти к ШАГУ 6 — заливка папки mydocker, CI запуск и далее до конца)

---

## ШАГ 6 — ЗАЛИВАЕМ ПАПКУ `mydocker` В РЕПОЗИТОРИЙ

Если папка `mydocker` лежит вне `k8s-demo`, перенесём её внутрь:

```bash
cd ~
mv mydocker ~/k8s-demo/
cd ~/k8s-demo
ls -la
```

Теперь заливаем её в GitHub:

```bash
git add mydocker -f
git commit -m "add mydocker folder"
git push
```

✅ Папка `mydocker` теперь загружена в репозиторий.

---

## ШАГ 7 — ЗАПУСКАЕМ CI (ПЕРВУЮ СБОРКУ DOCKER IMAGE)

```bash
git add .
git commit -m "add CI workflow"
git push
```

GitHub начнёт сборку образа → зайди во вкладку **Actions**.
Если видишь `Build and Push Docker Image` → значит CI работает.

---

## ШАГ 8 — СОЗДАЁМ ФАЙЛ ДЛЯ АВТОДЕПЛОЯ В KUBERNETES

```bash
nano .github/workflows/deploy-dev.yml
```

Вставляем ПОЛНОСТЬЮ:

```yaml
name: Deploy to Kubernetes (Dev)

on:
  workflow_dispatch:
  push:
    branches: ["master"]

jobs:
  deploy:
    runs-on: self-hosted
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Set image tag (latest always)
        run: |
          sed -i 's|image: .*$|image: yourname/devops-demo:latest|g' ./k8s/overlays/dev/kustomization.yaml || true
      - name: Apply Kustomize dev
        run: |
          kubectl apply -k ./k8s/overlays/dev
      - name: Wait for rollout
        run: |
          kubectl rollout status deploy/hello-deployment-dev --timeout=120s
```

Сохраняем и пушим:

```bash
git add .github/workflows/deploy-dev.yml
git commit -m "add deploy workflow"
git push
```

---

## ШАГ 9 — НАСТРАИВАЕМ SELF-HOSTED GITHUB RUNNER НА УБУНТУ

На GitHub → Repo → Settings → Actions → Runners → New self-hosted runner → Linux → x64

```bash
cd ~/k8s-demo
mkdir actions-runner && cd actions-runner
curl -o actions-runner.tar.gz -L https://github.com/actions/runner/releases/download/v2.321.0/actions-runner-linux-x64-2.321.0.tar.gz
tar xzf actions-runner.tar.gz
./config.sh --url https://github.com/ТВОЙ_USERNAME/devops-demo --token xxxxxxxxxxx
./run.sh
```

✅ Если увидел `Listening for Jobs` — runner ЗАПУЩЕН. НЕ ЗАКРЫВАЙ этот терминал.

---

## ШАГ 10 — ЗАПУСК ДЕПЛОЯ ВРУЧНУЮ

Открой GitHub → твой репозиторий → вкладка **Actions**

Найди workflow: **Deploy to Kubernetes (Dev)**

Справа будет кнопка **“▶ Run workflow”** — нажми её

Просто подтверди запуск (ничего не меняем)

Runner сейчас «слушает», и как только ты нажмёшь — он **в реальном времени** начнёт деплой в твой Kubernetes.

Если вылезет ошибка `permission denied` — **это нормальная ошибка**, причина проста:
GitHub Runner запущен как **обычный пользователь**, а kubectl и minikube настроены на **root (/root/.minikube/)**, поэтому → **права доступа запрещены (permission denied)**.

Чтобы её исправить в терминале (НЕ в runner) выполняем:

```bash
sudo cp /root/.kube/config /home/user/.kube/config
sudo chown user:user /home/user/.kube/config
```

Это перенесёт и передаст права на kubeconfig твоему пользователю.

ПРОВЕРЯЕМ:

```bash
kubectl get pods -A
```

Если команда сработала БЕЗ `sudo` — всё ✅

Теперь в GitHub Actions нажимаем **Re-run jobs → deploy**

После этого (если всё ОК) — обновляем код деплоя вручную:

```bash
sudo nano .github/workflows/deploy.yml
```

Вставляем (заменяем полностью):

```yaml
name: Deploy to Kubernetes (Dev)

on:
  workflow_dispatch:   # запуск вручную
  push:
    branches: ["master"]   # автоматически при пуше в master

jobs:
  deploy:
    runs-on: self-hosted   # запускается на твоём локальном runner-е

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set image tag (latest always)
        run: |
          sed -i 's|image: .*$|image: yourname/devops-demo:latest|g' ./k8s/overlays/dev/kustomization.yaml || true

      - name: Apply Kustomize dev
        run: |
          kubectl apply -k ./k8s/overlays/dev

      - name: Wait for rollout
        run: |
          kubectl rollout status deploy/hello-deployment-dev --timeout=120s
```

Мы должны обязательно быть в папке **k8s-demo/**

```bash
git add mydocker
git commit -m "add Kubernetes"
git push
```

---

## ✅ ФИНАЛЬНЫЙ РЕЗУЛЬТАТ

Ты сделал ПОЛНЫЙ CI/CD:

* Git push в master → Собирается Docker image → Автодеплой в Minikube
* Больше никаких ручных `kubectl apply`
* Всё автоматизировано

---
