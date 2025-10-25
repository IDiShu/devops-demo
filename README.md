----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
✅ Пример структуры папок

k8s-demo/
 ├── .github/workflows/deploy.yml
 ├── k8s/
 │    ├── base/
 │    └── overlays/
 │         ├── dev/
 │         │    ├── kustomization.yaml
 │         │    ├── replicas-patch.yaml
 │         │    └── postgres-storage-patch.yaml
 │         └── prod/

Тут стоит обратить внимание что CI/CD запускается всегда внутри k8s-demo, поэтому путь в GitHub Actions не должен содержать k8s-demo
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

📄 Примеры содержимого файлов

Папка - .github/workflows/deploy.yml


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
          sed -i 's|image: .*$|image: idishui/devops-demo:latest|g' ./k8s/overlays/dev/kustomization.yaml || true

      - name: Apply Kustomize dev
        run: |
          kubectl apply -k ./k8s/overlays/dev

      - name: Wait for rollout
        run: |
          kubectl rollout status deploy/hello-deployment-dev --timeout=120s

Папка - k8s/base/overlays/dev/kustomization.yaml


apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../../base                 # включаем все ресурсы из базовой директории

nameSuffix: "-dev"             # добавляем суффикс имён для ресурса (например, StatefulSet "postgres" -> "postgres-dev")

labels:                        # добавляем метки ко всем ресурсам этого оверлея
  - includeSelectors: true
    includeTemplates: true
    pairs:
      env: development         # метка окружения

patches:                       # патчи для изменения базовых ресурсов
  - path: replicas-patch.yaml
    target:
      kind: StatefulSet
      name: postgres
  - path: postgres-storage-patch.yaml
    target:
      kind: StatefulSet
      name: postgres


Папка - k8s/base/overlays/dev/replicas-patch.yaml


*Вставь тут пример который нужен, потому что у нейронки его нет, или я не нашёл*

Папка - k8s/base/overlays/dev/postgres-storage-patch.yaml


*Сейм с этим, может это просто стандартные патчи, но я не знаю*
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Типовые проблемы и быстрые фиксы для них


1) ImagePullBackOff

Образ приватный?

Для Docker Hub: сделай образ публичным ИЛИ создай imagePullSecret и пропиши его в Deployment (spec.template.spec.imagePullSecrets).

Неверный тег? Проверь, что build запушил именно :SHA и что патч действительно подставил его.

2) kubectl not found на раннере

Поставь kubectl на VM и убедись, что $KUBECONFIG настроен (чтобы kubectl get pods работал без sudo). В Модуле 2 мы работать с kubectl уже умели.

3) Нет доступа к Ingress

Проверь kubectl get svc -n traefik (NodePort выставлен, порт верный) и /etc/hosts с hello-dev.local (делали в Модуле 4).

curl -I -H "Host: hello-dev.local" http://<VM_IP>:<NodePort>.

4) Патчи Kustomize «не попадают»

Если используешь nameSuffix в overlays, таргет в patches.target.name должен ссылаться на базовое имя ресурса (без суффикса). Мы именно это разбирали, когда чинили postgres[-prod] в StatefulSet патчах.

5) Rollout висит

kubectl describe pod ... → ищи Events.

Проверь readiness/liveness (можно добавить простые пробы в Deployment)

6) При выполнении команды git commit -m "initial commit" может выбить "Author identity unknown"
В этом случае надо выполнить 2 команды
git config --global user.email "you@example.com" твой реально существующий @mail
git config --global user.name "Your Name" имя твоего аккаунта в GitHub
Это надо для того чтобы Git знал кто ты для коммита
В итоге при выполнении команды должно быть на подобии этого:
 
user@user:~/k8s-demo$ git commit -m "initial commit"
[master (root-commit) d57c06a] initial commit 
14 files changed, 254 insertions(+) 
create mode 100644 k8s/base/deployment.yaml 
create mode 100644 k8s/base/ingress.yaml 
create mode 100644 k8s/base/kustomization.yaml 
create mode 100644 k8s/base/postgres-pv-pvc.yaml 
create mode 100644 k8s/base/postgres-statefulset.yaml 
create mode 100644 k8s/base/service.yaml 
create mode 100644 k8s/overlays/dev/kustomization.yaml 
create mode 100644 k8s/overlays/dev/postgres-storage-patch.yaml 
create mode 100644 k8s/overlays/dev/replicas-patch.yaml 
create mode 100644 k8s/overlays/prod/kustomization.yaml 
create mode 100644 k8s/overlays/prod/postgres-storage-patch.yaml 
create mode 100644 k8s/overlays/prod/replicas-patch.yaml 
create mode 100644 tls.crt 
create mode 100644 tls.key

7) при выполнении команды git push может выдать ошибку "failed to push some refs to 'https://github.com/ТВОЙ_USERNAME/devops-demo.git'"
Это означает что при создании токена GitHub не выставили нужные галочки:
✅ repo

✅ workflow ← очень важно!
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Сейчас ШАГ 0: создаём репозиторий на GitHub

Открывай GitHub в браузере → github.com → кнопка New (или Create new repository)
И сделай простой репозиторий с такими параметрами:

Repository name: например devops-demo

Description можно оставить пустым

✅ Public (проще, не надо настраивать SSH keys или PAT)

✅ Поставь галочку Add a README file, чтобы не был пустой

→ Нажми Create repository
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Шаг 1: Docker Hub

Создай/зайди в Docker Hub

Открой hub.docker.com → Sign up / Sign in.

Создай токен доступа

Профиль (иконка вверху) → Account Settings → Security → New Access Token.

Назови, например: gha-push → Create → Скопируй значение токена (потом не покажут!).
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Шаг 2: создаём GitHub Token 

Зайди в GitHub → справа сверху на аватар → Settings

Слева внизу → Developer settings

→ Personal access tokens → Tokens (classic)

Нажми Generate new token → Generate new token (classic)

Назови: ci-workflow

Поставь галочку repo и workflow ← очень важно!

Пролистай вниз → Generate token

СКОПИРУЙ токен (как с Docker Hub — потом не покажут!)

И снова используешь команду

git push -u origin master

Логин остался таким же, а паролем является сгенерированный токен

Если галочку workflow пропустили, то надо создать новый токен с уже включённой галочкой и выполнить эти команды

git remote set-url origin https://github.com/ТВОЙ_USERNAME/devops-demo.git
git push -u origin master

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Шаг 3 Создание GitHub-репозитория

user@user:~$ tree . 
├── k8s-demo 
│   ├── k8s 
│   │   ├── base 
│   │   │   ├── deployment.yaml 
│   │   │   ├── ingress.yaml 
│   │   │   ├── kustomization.yaml 
│   │   │   ├── postgres-pv-pvc.yaml 
│   │   │   ├── postgres-statefulset.yaml 
│   │   │   └── service.yaml 
│   │   └── overlays 
│   │   ├── dev 
│   │   │   ├── kustomization.yaml 
│   │   │   ├── postgres-storage-patch.yaml 
│   │   │   └── replicas-patch.yaml 
│   │   └── prod 
│   │   ├── kustomization.yaml 
│   │   ├── postgres-storage-patch.yaml 
│   │   └── replicas-patch.yaml 
│   ├── tls.crt 
│   └── tls.key 
├── minikube-linux-amd64 
└── mydocker 
├── app.py 
├── docker-compose.yml 
├── Dockerfile 
└── start.sh

cd ~/k8s-demo

Потом выполни строго по очереди:

git init
git remote add origin https://github.com/ТВОЙ_USERNAME/ТВОЙ_REPO.git
git add .
git commit -m "initial commit"
git push -u origin master   # если не сработает — заменим на main

При выполнении команды "git push -u origin master" GitHub запросит логин и пароль
Логин такой же как у аккаунта на GitHub (чувствителен к синтаксису, если логин с большими буквами, а написал только маленькими, то не сработает)
Паролем будет являться не пароль от GitHub аккаунта, а GitHub Personal Access Token (PAT).

Должно выйти на подобии: 
user@user:~/k8s-demo$ git push -u origin master 
Username for 'https://github.com': ТВОЙ_USERNAME 
Password for 'https://ТВОЙ_USERNAME@github.com':(тут должен быть твой токен, но в целях безопасности он не отображается)
Enumerating objects: 21, done. 
Counting objects: 100% (21/21), done. 
Delta compression using up to 2 threads 
Compressing objects: 100% (21/21), done. 
Writing objects: 100% (21/21), 5.24 KiB | 1.75 MiB/s, done. 
Total 21 (delta 2), reused 0 (delta 0), pack-reused 0 
remote: Resolving deltas: 100% (2/2), done. 
remote: 
remote: Create a pull request for 'master' on GitHub by visiting: 
remote: https://github.com/ТВОЙ_USERNAME/devops-demo/pull/new/master 
remote: To https://github.com/ТВОЙ_USERNAME/devops-demo.git * [new branch] master -> master 
branch 'master' set up to track 'origin/master'.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Шаг 4 — подключаем Docker Hub к GitHub через Secrets

Открой в браузере GitHub → твой репозиторий → вкладка Settings (⚙️ вверху).

Дальше:

Settings → слева меню → Secrets and variables → Actions → кнопка New repository secret

И создаём 2 секрета: 

DOCKERHUB_USERNAME с твоим логином Docker Hub

DOCKERHUB_TOKEN токен который ты скопировал в шаге 1
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Шаг 5 — создаём GitHub Actions workflow (build & push Docker image)

нужно будет создать файл в репозитории:

/.github/workflows/build.yml

Исполнять команды надо из ~/k8s-demo

Чтобы увидеть папку .github надо ввести эту команду

ls -la

На Ubuntu (внутри папки проекта), просто выполни:

mkdir -p .github/workflows
sudo nano .github/workflows/build.yml

И в открывшемся редакторе вставляешь:
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

После чего нажимаешь
 
CTRL + O  (чтобы сохранить)
ENTER
CTRL + X  (чтобы выйти)
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Шаг 6 — заливаем папку mydocker в GitHub

перенос mydocker (если он находится вне репозитория ~/k8s-demo/)

cd ~
mv mydocker ~/k8s-demo/
cd ~/k8s-demo
ls -la


cd ~/k8s-demo
git add mydocker -f
git commit -m "add mydocker folder"
git push

-f на всякий случай, если внутри есть .gitignore

(Branch надо сменить с main на master в вашем репозитории который вы создали в GitHub)
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Шаг 7 — запуск CI

git add .
git commit -m "add CI workflow"
git push

Это запустит GitHub Actions — он начнёт автоматически собирать Docker image и отправлять его на Docker Hub

Должно выйти на подобии:
git push -u origin master 
Enumerating objects: 6, done. 
Counting objects: 100% (6/6), done. 
Delta compression using up to 2 threads 
Compressing objects: 100% (3/3), done. 
Writing objects: 100% (5/5), 735 bytes | 735.00 KiB/s, done. 
Total 5 (delta 0), reused 0 (delta 0), pack-reused 0 
To https://github.com/ТВОЙ_USERNAME/devops-demo.git d57c06a..aeea628 master -> master 
branch 'master' set up to track 'origin/master'.

Перед тем как продолжить, быстрый контрольный вопрос (чтобы не потерять 30 минут на ошибке впереди):

➡️ Minikube / Kubernetes сейчас ЗАПУЩЕН на твоей Ubuntu?
То есть если ты прямо сейчас в Ubuntu выполнишь:

kubectl get pods -A

Как должно примерно выглядеть:

user@user:~/k8s-demo$ sudo kubectl get pods -A
NAMESPACE     NAME                                           READY   STATUS             RESTARTS           AGE
default       hello-deployment-5894f8884c-2slpj              1/1     Running            1 (4h19m ago)      23h
default       hello-deployment-dev-5d6f77cb87-5lp8j          1/1     Running            0                  3h
default       hello-deployment-prod-5894f8884c-8d9mb         1/1     Running            0                  82m
default       postgres-0                                     1/1     Running            0                  159m
default       postgres-1                                     0/1     CrashLoopBackOff   22 (3m51s ago)     91m
default       postgres-dev-0                                 1/1     Running            0                  158m
default       postgres-prod-0                                1/1     Running            0                  74m
default       postgres-prod-1                                1/1     Running            0                  75m
kube-system   coredns-66bbc9577-npcb8                        1/1     Running            2 (4h19m ago)      41h
kube-system   etcd-user                                      1/1     Running            2 (4h19m ago)      41h
kube-system   kube-apiserver-user                            1/1     Running            2 (4h19m ago)      41h
kube-system   kube-controller-manager-user                   1/1     Running            2 (4h19m ago)      41h
kube-system   kube-proxy-wbhjv                               1/1     Running            2 (4h19m ago)      41h
kube-system   kube-scheduler-user                            1/1     Running            2 (4h19m ago)      41h
kube-system   storage-provisioner                            1/1     Running            4 (4h11m ago)      41h
traefik       traefik-6886846958-rsbmh                       1/1     Running            1 (22h ago)        23h

— ты должен увидеть работающий кластер (Traefik, PostgreSQL и т.д.)
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Шаг 8 — создаём Deploy Workflow

sudo nano .github/workflows/deploy-dev.yml

В открывшемся редакторе вставляем данный код:

name: Deploy to Kubernetes (Dev)

on:
  workflow_dispatch:   # запуск вручную
  push:
    branches: ["master"]   # автоматически при пуше в master

jobs:
  deploy:
    runs-on: self-hosted   # будет выполняться на твоей Ubuntu (runner)
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set image tag (latest always)
        run: |
          sed -i 's|image: .*$|image: idishui/devops-demo:latest|g' ./k8s-demo/k8s/overlays/dev/kustomization.yaml || true

      - name: Apply Kustomize dev
        run: |
          kubectl apply -k ./k8s-demo/k8s/overlays/dev

      - name: Wait for rollout
        run: |
          kubectl rollout status deploy/hello-deployment --timeout=120s

Сохраняем файл и выполняем данные команды:

git add .github/workflows/deploy-dev.yml
git commit -m "add deploy workflow"
git push
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Шаг 9 — открываем GitHub Runner установщик

На GitHub зайди:

Repo → Settings → слева Actions → Runners → New self-hosted runner → Linux → x64

cd ~/k8s-demo
mkdir actions-runner && cd actions-runner
curl -o actions-runner.tar.gz -L https://github.com/actions/runner/releases/download/v2.321.0/actions-runner-linux-x64-2.321.0.tar.gz
tar xzf actions-runner.tar.gz 

После распаковки — проверь, что появился config.sh:

ls -la 

config.sh на месте, всё распаковалось правильно.

При создании New self-hosted runner внизу есть конфиг которы выглядит примрно так:./config.sh --url https://github.com/ТВОЙ_USERNAME/devops-demo --token xxxxxxxxxxx

Этот конфиг мы копируем и вставляем в терминал (стоит обратить внимание что данную команду мы выполняем в user@user:~/k8s-demo/actions-runner)

./config.sh --url https://github.com/ТВОЙ_USERNAME/devops-demo --token xxxxxxxxxxx

После того как команда закончится успешно (GitHub напишет √ Runner successfully configured):

выполни последнюю команду сразу:

./run.sh

Когда увидишь:

√ Connected to GitHub
Listening for Jobs (если видите эту команду, то это означает что runner запущен ✅)

На все предложения мы соглашаемся с помощью ENTER

user@user:~/k8s-demo/actions-runner$ ./run.sh 

√ Connected to GitHub 

Current runner version: '2.321.0' 
2025-10-25 13:16:02Z: Listening for Jobs 
2025-10-25 13:16:05Z: Running job: deploy 
Runner update in progress, do not shutdown runner. 
Downloading 2.329.0 runner 2025-10-25 13:16:16Z: Job deploy completed with result: Failed

runner успешно подключён и работает, это нормально
То, что он сам решил обновиться — это нормально, GitHub runner так и делает.
Но первый job (deploy) упал, потому что мы запустили его ещё до подготовки 
Это не ошибка, всё идёт правильно.

Должно выйти примерно так:
Waiting for current job finish running. 
Generate and execute update script. 
Runner will exit shortly for update, should be back online within 10 seconds. 
Runner update process finished. 
Runner listener exit because of updating, re-launch runner after successful update 
Update finished successfully. Restarting runner... 

√ Connected to GitHub 

Current runner version: '2.329.0' 
2025-10-25 13:16:51Z: Listening for Jobs

НЕ ЗАКРЫВАЙТЕ терминал после начала работы runner, просто откройте новый терминал
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Шаг 10 — запуск деплоя вручную

Открой GitHub → твой репозиторий → вкладка Actions

Найди workflow: Deploy to Kubernetes (Dev)

Справа будет кнопка “▶ Run workflow” — нажми её

Просто подтверди запуск (ничего не меняем)

Runner сейчас «слушает», и как только ты нажмёшь — он В РЕАЛЬНОМ ВРЕМЕНИ начнёт деплой в твой Kubernetes.

Если вылезет ошибка permission denied это нормальная ошика, причина проста:GitHub Runner запущен как обычный пользователь, а kubectl и minikube настроены на root (/root/.minikube/), поэтому → права доступа запрещены (permission denied).

Чтобы её исправить в терминале (не с runner) выполняем команды

sudo cp /root/.kube/config /home/user/.kube/config
sudo chown user:user /home/user/.kube/config

Это перенесёт и передаст права на kubeconfig твоему обычному пользователю.

Для проверки сработало ли, выполняем данную команду:

kubectl get pods -A

И если она работает без sudo, поздравляю, проблема решена

Жми Re-run jobs → deploy в GitHub Actions

Далее пишем

sudo nano .github/workflows/deploy.yml

И в открывшемся редакторе вставляем данный код:

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
          sed -i 's|image: .*$|image: idishui/devops-demo:latest|g' ./k8s/overlays/dev/kustomization.yaml || true

      - name: Apply Kustomize dev
        run: |
          kubectl apply -k ./k8s/overlays/dev

      - name: Wait for rollout
        run: |
          kubectl rollout status deploy/hello-deployment-dev --timeout=120s

Мы должны обязательно быть в папке k8s-demo/

git add mydocker
git commit -m "add Kubernetes"
git push
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
✅ Вывод

Твой CI/CD pipeline сработал потому что теперь:

kubectl apply -k ./k8s/overlays/dev попал в реальную директорию,

образ подставляется в нужный файл,

rollout следит за нужным деплоем с -dev суффиксом.

Ты всё правильно сделал под конец. И теперь у тебя есть рабочий GitHub Actions автодеплой в Kubernetes 👏
