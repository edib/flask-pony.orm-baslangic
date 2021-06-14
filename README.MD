# Flask ve Pony ORM Basit Kullanıcı Girişi ve Makale Uygulaması

Mustafa Murat Coşkun'un [(40+ Saat) Python | Sıfırdan İleri Seviye Programlama (2020)](https://www.udemy.com/course/sifirdan-ileri-seviyeye-python/) Udemy eğitimindeki "Flask Framework ile Web Geliştirme Temelleri"ni "Pony ORM" ile yaptım. 


Gerekli paketleri kurun.
```
pip3 install flask
pip3 install WTForms
pip3 install pony
```

Aşağıdaki `SECRET KEY` ve `filename` değerlerini değiştirin.

```
app.config.update(dict(
    DEBUG = False,
    SECRET_KEY = 'secret_xxxx',
    PONY = {
        'provider': 'sqlite',
        'filename': 'dbname.db', 
        'create_db': True
    }
))
```
