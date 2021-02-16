## Django Frameworkida qilingan loyihamizni Debian/Ubuntu 20.04 serveriga joylash, Postgres, Nginx, Gunicorn paketlarini sozlash va ishga tushurish

ESLATMA:
  - Loyiha nomi `project_name`
  - Ma'lumotlar bazasining nomi  `database_name`
  - Ma'lumotlar bazasining foydalanuvchisining ismi  `user_name`
  - Ma'lumotlar bazasining paroli  `password`
  - Ubuntu foydalanuvchi nomi `sammy`
Ushbu o'zgaruvchilar orniga uzingizni ma'lumotlaringizni kiriting!!!
```
**Ushbu qollanmada men quyidagi loyihadan foydalanaman, sizning loyihangizni tuzilishi menikidan farq qilishi mumkin**
├── projectname
	├── appname
	│	├── __init__.py
	│	├── admin.py
	│	├── apps.py
	│	├── models.py
	│	├── views.py
	│	└── urls.py
	├── projectname
	│	├── __init__.py
	│	├── settings.py
	│	├── urls.py
	│	└── wsgi.py
	├── templates
	├── static
	├── media
	├── manage.py
	└── requirements.txt

```
Ushbu qollanmani root foydalanuvchi sifatida bajarish tavsiya etilmaydi, Foydalanuvchi [yaratish va unga sudo huquqini](https://www.digitalocean.com/community/tutorials/how-to-create-a-new-sudo-enabled-user-on-ubuntu-20-04-quickstart) berish. 
### Kerakli paketlarni o'rnatish
```sh
$ sudo apt update
$ sudo apt install -y python-pip python-dev libpq-dev vim git htop postgresql postgresql-contrib nginx redis-server
```
### PostgreSQL ni sozlash
Oldin ma'lumotlar bazasini va shu ma'lumotlar bazasidan foydalanuvchi yaratib olamiz.

PostgreSQL ma'lumotlar bazasini o'rnatgandan so'ng PostgreSQL ma'lumotlar bazasi postgresql nomli foydalanuvchi yaratadi, biz ma'lumotlar bazasini sozlashda o'sha foydalanuvchidan foydalanamiz, biz `sudo` komandasi `-u` parametri bilan foydalanuvchi nomini kiritishimiz kerak
```
$ sudo -u postgres psql
```
Ma'lumotlar bazasini yaratib olamiz.
```
postgres=# CREATE DATABASE database_name;
```
Yaratilgan ma'lumotlar bazasidan foydalanuvchi yaratamiz.
```sh
postgres=# CREATE USER user_name WITH PASSWORD 'password';
```
Ma'lumotlar bazasini sozlab olamiz
   - Kodirofkani utf8 ga o'zgartiramiz
   - Tranzaktsiyalarni kutilmagan ma'lumotlar bazasi foydalanuvchisidan cheklab qoyamiz
   - Timezone ni UTC ga o'zgartirish (agarda siz loyihangizni boshqa UTC ishlatsangiz shunga o'zgartirish tavsfiya etiladi)
```sh
postgres=# ALTER ROLE user_name SET client_encoding TO 'utf8'; 
postgres=# ALTER ROLE user_name SET default_transaction_isolation TO 'read committed'; 
postgres=# ALTER ROLE user_name SET timezone TO 'UTC';
```
Foydalanuvchiga ma'lumotlar bazasini boshqarishga huquq berish
```sh
postgres=# GRANT ALL PRIVILEGES ON DATABASE user_name TO database_name; 
```
Endi PostgreSQL dan chiqamiz.
```sh
postgres=# \q
```
### Loyihani git repositoriyasidan yuklab olish
```sh
$ git clone your_repository_link
```
### Virtual muhit
Birinchi navbatda [Virtual muhitni](https://docs.python.org/3/library/venv.html) yaratib olamiz.
```sh
$ cd my_project
$ python3 -m venv venv
```
Virtual muhitni aktivatsiya qilish va kerakli kutubxonalarni o'rnatish
```sh
$ . venv/bin/activate && pip3 insatll -r requirements.txt
```
Agarda siz loyihangizda boshqa qo'shimcha kutubxonalarni ishlatgan bolsangiz requirements.txt ga qo'shib qo'yishingiz kerak bo'ladi
### Loyihani sozlash
Loyihamizni serverda ishga tushurish uchun oldin loyihani sozlab olishimiz kerak, loyiha sozlamari `settings.py` faylida joylashishi bilsangiz kerak? xa albatta bilasiz degan ummida man, `ALLOWED_HOSTS` ro'yhatimizda loyihani ishga tushirilgan server IP va domen nomlarini kiritishimiz kerak bu Django loyihamiz qaysi serverdan kelgan xabarlarga javob qaytarishi bilishi uchun kerak bo'ladi.
```python
ALLOWED_HOSTS = ['your_server_domain_or_IP', 'second_domain_or_IP']
```
Ma'lumotlar bazasini sozlamarini saqlaydigan dictga o'zgartirish kirishimiz kerak, ya'ni qaysi ma'lumotlar bazasiga ulanish, ma'lumotlar bazasini foydalanuvchising ismi va paroli, ma'lumotlar bazasimiz qaysi port da ishlab turganini kiritishimiz kerak
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'database_name',
        'USER': 'user_name',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```
Statik fayllarni qaerga jo'ylashtirish keraklini bildiradigan o'zgaruvchi yaratishimiz kerak, django loyihamizni localhost da ishlatganimizda bu o'zgaruvchi kerak bolmaydi chunki `DEBUG=True` holatda statik fayllarni django qayta ishlaydi `DEBUG=False` xolatda esa statik fayllarni Nginx(proxy-server) qayta ishlaydi.
settings.py faylni oxiriga `STATIC_ROOT` o'zgaruvchi elon qilamiz va `BASE_DIR` (loyihamiz joylashgan joy) ga statik fayllarni saqlash uchun mo'ljallangan `staticfiles` nomli directoriyani qo'shib qoyamiz
```python
STATIC_ROOT = BASE_DIR / 'staticfiles'
```
Migratsiyalarni yaratib ularni ma'lumotlar bazamizga saqlaymiz, `python3 manage.py makemigrations` komandasi modelimizni holatini migratsiya faylida saqlab qoyadi va `python3 manage.py migrate` komandasi esa migratsiya fayllarini ma'lumotlar bazamizga saqlaydi
```sh
(venv)$ python3 manage.py makemigrations
(venv)$ python3 manage.py migrate
```
Endilikda admin paneliga kira olishimiz uchun superuser yaratib olamiz.
```sh
(venv)$ python3 manage.py createsuperuser
```
Nginxga statik fayllarni qaysi direktoriya(papkada) dan izlash keraklikini ko'rsatishimiz uchun statik fayllarni bir joyga jamlab olamiz. 
```sh
(venv)$ python3 manage.py collectstatic
```
Va nihoyat biz loyihamizni tog'ri sozlaganimizni bilishimiz uchun loyihani ishga tushirib ko'rishimiz mumkin
```sh
python3 manage.py runserver 0.0.0.0:8000
```
Brauzeringizda server ipisiga 8000-portni qo'shib yozib tekshirib ko'rishingiz mumkin
example: server_ip:8000
Tushunarliki bunday qilib loyihani ishlatib qoyib bolmaydi chunki loyihamizni real serverga  joylaganimizda `DEBUG=FALSE` bo'lishi kerak bu foydalanuvchiga loyihamizda yuz bergan xatoliklarni ko'rsatmaslikimiz uchun kerak.
Virtual muhitni deaktivatsiya qilishimizdan oldin gunicorn kelgan habarlga javob qayta olishini tekshirib ko'rishimiz kerak, biz loyihamiz katalogiga kirib, `gunicorn` yordamida loyihaning WSGI modulini yuklashga urinib ko'ramiz:
```sh
cd ~/myproject
gunicorn --bind 0.0.0.0:8000 myproject.wsgi 
```
Bu komanda orqali Gunicorn orqali Django loyihamizni ishga tushiramiz.Orqaga qaytib loyihamiz ko'rsatilgan ip orqali ishlayotganini qayta sinab ko'rishingiz mumkin. CTRL+C tugmachasini bosib gunicorn ni toxtatib virtual muhitni deaktivatsiya qilamiz.
```sh
(venv)$ deactivate
```
### Gunicorn ni sozlash
Django Loyihamizni serverda ishlatib qoyishimiz uchun [Nginx](https://nginx.org/ru/) va [Gunicorn](https://gunicorn.org/) dan foydalanamiz
Gunicorn uchun systemd ni sozlab olishimiz kerak, systemd Linux xizmatlarini ishga tushurish/boshqarish uchun qulay tizim hisoblanadi.
```
$ sudo nano /etc/systemd/system/gunicorn.service
```
Yuqoridaki komanda orqali `/etc/systemd/system/` katoligida gunicorn.service faylini yaratamiz, va quyidaki sozlamarni kiritib `ctrl+x+y+y+ENTER` tugmachasini bosamiz.
```commandline
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=sammy
Group=www-data
WorkingDirectory=/home/sammy/myproject
ExecStart=/home/sammy/myproject/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/sammy/myproject/myproject.sock myproject.wsgi:application

[Install]
WantedBy=multi-user.target
```
  - `[Unit]` bo'limida biz qanday xizmat uchun sozlamar kirityapganimizni va qachon ishga tushirilishi keraklikni kiritamiz.
  - `[Service]` bo'limida foydalanuvchi nomini va qaysi guruhga mansub ekanligini kiritamiz, nginx va gunicorn muloqat qila olishi uchun foydalanuvchi guruhi sifatida `www-data` ni kiritamiz. `WorkingDirectory` da qaysi direktoriyada ishlashni bildirishimiz uchun kerak bo'ladi, `ExecStart` esa qaysi komanda orqali ishga tushirimiz keraklikini kiritamiz.
  - `[Install]` bo'limi nimaga keraklikini uzim ham bilmaymiz ammo buni yozmasak ishlamaydida))
Endi systemctl komandasi orqali yuqorida yozgan xizmatimizni ishga tushiramiz va OS qayta ishga tushgan paytida avtomatik tarzda ishga tushirilishi keraklikini aytamiz.
```sh
$ sudo systemctl start gunicorn
$ sudo systemctl enable gunicorn
```
Endi Gunicorn ni holatini tekshirib ko'ramiz
```sh
$ sudo systemctl status gunicorn
```
Qollanmani davom ettirishdan oldin gunicorn holati aktiv ekanligiga ishonch hosil qiling!!!
Agarda siz biron bir sabablarga ko'ra gunicorn loglarini ko'rmoqchi bolsangiz quyidaki komanda orqali buni amalga oshirishingiz mumkin
```sh
$ sudo journalctl -u gunicorn
```
`gunicorn.service` fayliga o'zgarish kiritsangiz gunicorn daemoni va gunicorn xizmatini qayta ishga tushurishingiz kerak boladi
```sh
$ sudo systemctl daemon-reload 
$ sudo systemctl restart gunicorn 
```
Agarda Gunicorn ishlayotgan bo'lsa loyihangiz katoligida `myproject.sock` fayli paydo bo'ladi!!!
### Nginxni sozlash
Loyihamiz uchun Nginx sozlamarini saqlaydigan yangi fayl yaratamiz. 
```sh
$ sudo nano /etc/nginx/sites-available/myproject 
```
Va quyidaki sozlamarni nusxasini ko'chirib olamiz
```editorconfig
server {
    server_name server_domain_or_IP;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        alias /home/sammy/myproject/staticfiles/;
    }    
    location /media/ {
        alias /home/sammy/myproject/media/;
    }
    location / {
        include proxy_params;
        proxy_pass http://unix:/home/sammy/myproject/myproject.sock;
    }
}
```
Endi biz yuqoridaki sozlamarni saytlar katalogiga bog'lab uni faollashtiramiz:
```sh
$ sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled 
```
Nginx sozlamalarini kiritishda sintaksis xatolik qilmaganimizni quyidaki komanda orqali tekshirishimiz mumkin.
```sh
$ sudo nginx -t
```
Agar xatoliklar yo'q bolsa Nginx qayta ishga tushuring.
```sh
$ sudo systemctl restart nginx 
```
Va nihoyat serverni sozlab boldik!!! Siz brauzeringizda server IP si yo'ki domenini kiritib buni tekshirib ko'rishingiz mumkin, ha aytkancha serveringiz uchun [SSL sertifikat olish](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-20-04)ni unitmang
