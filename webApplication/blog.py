from MySQLdb.cursors import Cursor
from flask import Flask, config, render_template, flash, redirect, url_for, session, logging, request, render_template
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
import os, io

#Kullanıcı giriş decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için lütfen giriş yapın.", "danger")
            return redirect(url_for("login"))
    return decorated_function

#Pdf Okutma
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
import io

class PdfReader:

    def __init__(self, pdfName):
        self.pdfName = pdfName
        self.yazarAdi = ''
        self.yazarNo = ''
        self.yazarOgretimTuru = ''
        self.dersAdi = ''
        self.projeOzeti = ''
        self.projeninTeslimEdildigiDonem = ''
        self.projeBasligi = ''
        self.anahtarKelimeler = ''
        self.danismanBilgileri = ''
        self.juriBilgileri = ''

    def pdf2txt(self, inPDFfile, outTXTFile):
        i = 0
        inFile = open(inPDFfile, 'rb')
        resMgr = PDFResourceManager()
        retData = io.StringIO()
        TxtConverter = TextConverter(resMgr, retData, laparams=LAParams())
        interpreter = PDFPageInterpreter(resMgr, TxtConverter)

        for page in PDFPage.get_pages(inFile):
            if i == 1 or i == 3 or i == 9:
                interpreter.process_page(page)
            i+=1

        txt = retData.getvalue()

        with open(outTXTFile, 'w', encoding='utf-8') as f:
            f.write(txt)

    def readPdf(self):

        inPDFfile = self.pdfName
        outTXTFile = 'deneme.txt'

        self.pdf2txt(inPDFfile, outTXTFile)

        with open('deneme.txt', 'r', encoding='utf-8') as file:
            data = file.read()
            data.splitlines()
            data = data.replace("\n", " ")
            data = data.replace("", "")

        x1 = 0

        #DERS ADI
        if "BİTİRME PROJESİ" in data:
            self.dersAdi += "BİTİRME PROJESİ"
            x1 = data.index("BİTİRME PROJESİ") + 15

        elif "ARAŞTIRMA PROBLEMLERİ" in data:
            self.dersAdi += "ARAŞTIRMA PROBLEMLERİ"
            x1 = data.index("ARAŞTIRMA PROBLEMLERİ") + 21


        #DANIŞMAN VE JÜRİ BİLGİLERİ
        x11 = data.index("Prof")
        data = data[x11:]


        #PROJENİN TESLİM EDİLDİĞİ DÖNEM
        x12 = data.index("Tezin") + 28
        tarih = 0
        yil = data[x12+3:x12+8]
        self.projeninTeslimEdildigiDonem += yil

        if data[x12:x12+1] == '0':
            tarih = (int)(data[x12+1:x12+2])
        else:
            tarih = (int)(data[x12:x12+2])

        if tarih < 2 and tarih > 8:
            self.projeninTeslimEdildigiDonem += 'GÜZ'
        else:
            self.projeninTeslimEdildigiDonem += 'BAHAR'


        #PROJE ÖZETİ
        x2 = data.index("ÖZET") + 4

        x3 = data.index("Anahtar  kelimeler")

        self.projeOzeti += data[x2:x3]
        self.projeOzeti = self.projeOzeti.strip(" ")


        #YAZAR BİLGİLERİ
        x4 = data.index("Adı Soyadı:") + 11
        x5 = data.index("İmza:")

        x20 = data.rfind("Adı Soyadı:") + 11
        x21 = data.rfind("İmza:")

        x13 = data.index("Öğrenci No:") + 11
        x22 = data.rfind("Öğrenci No:") + 11

        if x4==x20:
            self.yazarAdi += data[x4:x5]
            self.yazarAdi = self.yazarAdi.strip(" ")

            self.yazarNo += data[x13:x13+10]
            self.yazarNo = self.yazarNo.strip()

            if data[x13+6:x13+7] == '1':
                self.yazarOgretimTuru += ' Birinci Öğretim'
            else:
                self.yazarOgretimTuru += ' İkinci Öğretim'

            self.yazarOgretimTuru = self.yazarOgretimTuru.strip()

        else:
            #ilk öğrenci
            self.yazarAdi += data[x4:x5]
            self.yazarAdi = self.yazarAdi.strip(" ")

            x13 = data.index("Öğrenci No:") + 11

            self.yazarNo += data[x13:x13 + 10]
            self.yazarNo = self.yazarNo.strip()

            if data[x13 + 6:x13 + 7] == '1':
                self.yazarOgretimTuru += ' Birinci Öğretim'
            else:
                self.yazarOgretimTuru += ' İkinci Öğretim'

            self.yazarOgretimTuru = self.yazarOgretimTuru.strip()

            #ikinci öğrenci
            self.yazarAdi += data[x20:x21]
            self.yazarAdi = self.yazarAdi.strip(" ")

            self.yazarNo += data[x22:x22 + 10]

            if data[x22 + 6:x22 + 7] == '1':
                self.yazarOgretimTuru += ' Birinci Öğretim'
            else:
                self.yazarOgretimTuru += ' İkinci Öğretim'


        #PROJE BAŞLIĞI
        if x4==x20:
            x6 = data.index("İmza:…………………………………..") + 20
            x7 = data.index("ÖZET")
        else:
            x6 = data.rfind("İmza:…………………………………..") + 20
            x7 = data.index("ÖZET")

        self.projeBasligi += data[x6:x7]

        self.projeBasligi = self.projeBasligi.strip(" ")


        #UNKNOWN
        x8 = data.index("Prof.")

        data = data[x8:]
        data = data.strip(" ")


        #ANAHTAR KELİMELER
        x9 = data.index("Anahtar") + 20
        x10 = data.rfind(".")

        self.anahtarKelimeler += data[x9:x10]

        liste = [self.yazarAdi, self.yazarNo, self.yazarOgretimTuru, self.dersAdi, self.projeOzeti,
                     self.projeninTeslimEdildigiDonem, self.projeBasligi, self.anahtarKelimeler, self.danismanBilgileri, self.juriBilgileri]

        return liste

#Kullanıcı kayıt formu
class RegisterForm(Form):
    email = StringField("Email Adresi", validators=[validators.Email(message="Lütfen Geçerli Bir Email Adresi Giriniz")])
    password = PasswordField("Şifre", validators=[
        validators.DataRequired(message="Lütfen bir şifre belirleyin"),
        validators.EqualTo(fieldname="confirm", message="Parolanız uyuşmuyor")
    ])
    confirm = PasswordField("Şifre Doğrula")
    
#Kullanıcı giriş formu
class LoginForm(Form):
    email = StringField("Email Adresi")
    password = PasswordField("Şifre")
    
#Admin giriş formu
class AdminLoginForm(Form):
    email = StringField("Email Adresi")
    password = PasswordField("Şifre")
    
#Sorgu1 formu
class Sorgu1Form(Form):
    sorgu = StringField("Sorgu")
    
#Sorgu2 formu
class Sorgu2Form(Form):
    donem = StringField("Dönem")
    kullanici = StringField("Kullanıcı")
    ders = StringField("Ders")
    
    
app = Flask(__name__)
app.secret_key="yazlab3"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "website"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)  

#Ana sayfa
@app.route("/")
def index():
    return render_template("index.html") 

#Pdf sayfası
@app.route("/pdfs")
def pdfs():
    cursor = mysql.connection.cursor()
    
    sorgu = "select * from pdfs"
    
    result = cursor.execute(sorgu)
    
    if result > 0:
        pdfs = cursor.fetchall()
        return render_template("pdfs.html", pdfs = pdfs)
    else:
        return render_template("pdfs.html") 
    
#Detay sayfası
@app.route("/pdf/<string:id>")
def detail(id):
    cursor = mysql.connection.cursor()
    
    sorgu = "select * from pdfs where PdfId=%s"
    
    result = cursor.execute(sorgu, (id,))
    
    if result > 0:
        pdf = cursor.fetchone()
        return render_template("pdf.html", pdf = pdf)
    else:
        return render_template("pdf.html")
    
#Yönetim paneli
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "GET":
        cursor = mysql.connection.cursor()
        
        sorgu = "select * from users"
        
        result = cursor.execute(sorgu)
        
        if result > 0:
            users = cursor.fetchall()
            return render_template("dashboard.html", users = users)
        return render_template("dashboard.html")
    else:
        return redirect(url_for("adduser"))
    
#Kullanıcı Ekleme
@app.route("/adduser", methods=["GET", "POST"])
def adduser():
    form = RegisterForm(request.form)
    
    if request.method == "POST" and form.validate():
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)
        
        cursor = mysql.connection.cursor()
        
        sorgu = "insert into users (UserName, Password) values (%s, %s)"
        
        cursor.execute(sorgu, (email, password))
        mysql.connection.commit()
        
        cursor.close()
        
        flash("Başarıyla kayıt oldunuz!", "success")
        return redirect(url_for("dashboard"))
    else:
        return render_template("adduser.html", form=form)
    
#Kullanıcı silme
@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor = mysql.connection.cursor()
    
    sorgu = "delete from users where UserId = %s"
    cursor.execute(sorgu, (id,))
    
    mysql.connection.commit()
    
    flash("Kullanıcı silindi", "success")
    return redirect(url_for("dashboard"))

#Kullanıcı güncelleme
@app.route("/edit/<string:id>", methods=["GET", "POST"])
@login_required
def update(id):
    if request.method == "GET":
        cursor = mysql.connection.cursor()
        
        sorgu = "select * from users where UserId = %s"
        
        result = cursor.execute(sorgu, (id),)
        
        if result == 0:
            flash("Böyle bir kullanıcı yok", "danger")
            return redirect(url_for("dashboard"))
        else:
            user = cursor.fetchone()
            form = AdminLoginForm()
            
            form.email.data = user["UserName"]
            form.password.data = user["Password"]  
            
            return render_template("update.html", form = form)
        
    else:
        form = AdminLoginForm(request.form)
    
        newUsername = form.email.data
        newPassword = sha256_crypt.encrypt(form.password.data)
        
        sorgu2 = "update users set UserName=%s, Password=%s where UserId=%s"
        
        cursor = mysql.connection.cursor()
        
        cursor.execute(sorgu2, (newUsername, newPassword, id))
        
        mysql.connection.commit()
        
        flash("kullanıcı güncellendi", "success")
        
        return redirect(url_for("dashboard"))
        
#Pdf Ekleme
@app.route("/addpdf", methods=["GET", "POST"])
def addpdf():
    if request.method=="POST":
        file = request.files["file"]
        file.save(os.path.join("uploads", file.filename))
        
        pdfPath="C:\\Users\\JAN\\Desktop\\NEW PROJECT\\uploads\\"
        pdfName = file.filename
        pdfPath += pdfName
        
        deneme = PdfReader(pdfPath)
        list = deneme.readPdf()
        
        cursor = mysql.connection.cursor() 
        
        sorgu = "insert into pdfs(PdfName, UserEmail, AuthorName, AuthorNo, AuthorOgretimTuru, LessonName, ProjectSummary, ProjeninTeslimEdildigiDonem, ProjectTitle, Keywords, Consultants, Juries, PdfPath) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        
        cursor.execute(sorgu, (pdfName, session["email"], list[0], list[1], list[2], list[3], list[4], list[5], list[6], list[7], list[8], list[9], pdfPath))
               
        mysql.connection.commit()
           
        #cursor.close()
        
        flash("PDF başarıyla eklendi", "success")
        
        sorgu2 = "select * from pdfs where UserEmail = %s"
        
        result = cursor.execute(sorgu2, (session["email"],))

        if result > 0:
            pdfs = cursor.fetchall()
            return render_template("addpdf.html", pdfs = pdfs)
        else:
            return render_template("addpdf.html")    
    else:
        cursor = mysql.connection.cursor() 
        
        sorgu2 = "select * from pdfs where UserEmail = %s"
        
        result = cursor.execute(sorgu2, (session["email"],))

        if result > 0:
            pdfs = cursor.fetchall()
            return render_template("addpdf.html", pdfs = pdfs)
        else:
            return render_template("addpdf.html") 

#Sorgu1
@app.route("/sorgu1")
def sorgu1():
    return render_template("sorgu1.html")

#Sorgu1 Donem
@app.route("/searchdonem", methods=["GET", "POST"])
def sorgu1donem():
    form = Sorgu1Form(request.form)
    
    if request.method == "POST" and form.validate():
        data= form.sorgu.data
        
        cursor = mysql.connection.cursor()
        
        """if session["logged_in"]:
            sorgu = "select * from pdfs where ProjeninTeslimEdildigiDonem=%s and UserEmail=%s"
            result = cursor.execute(sorgu, (data, session["email"]))
        elif session["admin"]:
            sorgu = "select * from pdfs where ProjeninTeslimEdildigiDonem=%s"
            result = cursor.execute(sorgu, (data,))"""
            
        sorgu = "select * from pdfs where ProjeninTeslimEdildigiDonem=%s"
        result = cursor.execute(sorgu, (data,))
        
        if result > 0:
            datas = cursor.fetchall()
            return render_template("searchdonem.html", datas = datas, form=form)
        else:
            flash("Aranan koşullarda pdf bulunmamaktadır.", "danger")
            return render_template("searchdonem.html", form=form) 
            
    
    return render_template("searchdonem.html", form=form) 

#Sorgu1 Anahtar Kelimeler
@app.route("/searchanahtarkelimeler", methods=["GET", "POST"])
def sorgu1anahtarkelimeler():
    form = Sorgu1Form(request.form)
    
    if request.method == "POST" and form.validate():
        data = form.sorgu.data
        
        cursor = mysql.connection.cursor()
        
        """if session["logged_in"]:
            sorgu = "select * from pdfs where Keywords like '%" + data + "%' and UserEmail=%s"
            result = cursor.execute(sorgu, (session["email"],))
        elif session["admin"]:
            sorgu = "select * from pdfs where Keywords like '%" + data + "%'"
            result = cursor.execute(sorgu)"""
        
        sorgu = "select * from pdfs where Keywords like '%" + data + "%'"
        result = cursor.execute(sorgu)
        
        if result > 0:
            datas = cursor.fetchall()
            return render_template("searchanahtarkelimeler.html", datas = datas, form=form)
        else:
            flash("Aranan koşullarda pdf bulunmamaktadır.", "danger")
            return render_template("searchanahtarkelimeler.html", form=form) 
            
    
    return render_template("searchanahtarkelimeler.html", form=form) 

#Sorgu1 Proje Adı
@app.route("/searchprojeadi", methods=["GET", "POST"])
def sorgu1projeadi():
    form = Sorgu1Form(request.form)
    
    if request.method == "POST" and form.validate():
        data= form.sorgu.data
        
        cursor = mysql.connection.cursor()
        
        """if session["logged_in"]:
            sorgu = "select * from pdfs where ProjectTitle=%s and UserEmail=%s"
            result = cursor.execute(sorgu, (data, session["email"]))
        elif session["admin"]:
            sorgu = "select * from pdfs where ProjectTitle=%s"
            result = cursor.execute(sorgu, (data,))"""
            
        sorgu = "select * from pdfs where ProjectTitle=%s"
        result = cursor.execute(sorgu, (data,))
        
        if result > 0:
            datas = cursor.fetchall()
            return render_template("searchprojeadi.html", datas = datas, form=form)
        else:
            flash("Aranan koşullarda pdf bulunmamaktadır.", "danger")
            return render_template("searchprojeadi.html", form=form) 
            
    
    return render_template("searchprojeadi.html", form=form) 

#Sorgu1 Ders
@app.route("/searchders", methods=["GET", "POST"])
def sorgu1ders():
    form = Sorgu1Form(request.form)
    
    if request.method == "POST" and form.validate():
        data= form.sorgu.data
        
        cursor = mysql.connection.cursor()
        
        """if session["logged_in"]:
            sorgu = "select * from pdfs where LessonName=%s and UserEmail=%s"
            result = cursor.execute(sorgu, (data, session["email"]))
        elif session["admin"]:
            sorgu = "select * from pdfs where LessonName=%s"
            result = cursor.execute(sorgu, (data,))"""
            
        sorgu = "select * from pdfs where LessonName=%s"
        result = cursor.execute(sorgu, (data,))
        
        if result > 0:
            datas = cursor.fetchall()
            return render_template("searchders.html", datas = datas, form=form)
        else:
            flash("Aranan koşullarda pdf bulunmamaktadır.", "danger")
            return render_template("searchders.html", form=form) 
            
    
    return render_template("searchders.html", form=form) 

#Sorgu1 Yazar
@app.route("/searchyazar", methods=["GET", "POST"])
def sorgu1yazar():
    form = Sorgu1Form(request.form)
    
    if request.method == "POST" and form.validate():
        data= form.sorgu.data
        
        cursor = mysql.connection.cursor()
        
        """if session["logged_in"]:
            sorgu = "select * from pdfs where AuthorName=%s and UserEmail=%s"
            result = cursor.execute(sorgu, (data, session["email"]))
        elif session["admin"]:
            sorgu = "select * from pdfs where AuthorName=%s"
            result = cursor.execute(sorgu, (data,))"""
            
        sorgu = "select * from pdfs where AuthorName=%s"
        result = cursor.execute(sorgu, (data,))
        
        if result > 0:
            datas = cursor.fetchall()
            return render_template("searchyazar.html", datas = datas, form=form)
        else:
            flash("Aranan koşullarda pdf bulunmamaktadır.", "danger")
            return render_template("searchyazar.html", form=form) 
            
    
    return render_template("searchyazar.html", form=form) 

#Sorgu2
@app.route("/sorgu2", methods=["GET", "POST"])
def sorgu2():
    form = Sorgu2Form(request.form)
    
    if request.method == "POST" and form.validate():
        donem = form.donem.data
        kullanici = form.kullanici.data
        ders = form.ders.data
        
        cursor = mysql.connection.cursor()
        
        sorgu = "select * from pdfs where ProjeninTeslimEdildigiDonem=%s and UserEmail=%s and LessonName=%s"
        
        result = cursor.execute(sorgu, (donem, kullanici, ders))
        
        if result > 0:
            datas = cursor.fetchall()
            return render_template("sorgu2.html", datas = datas, form=form)
        else:
            flash("Aranan koşullarda pdf bulunmamaktadır.", "danger")
            return render_template("sorgu2.html", form=form) 
            
    
    return render_template("sorgu2.html", form=form) 

#Kayıt olma
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    
    if request.method == "POST" and form.validate():
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)
        
        cursor = mysql.connection.cursor()
        
        sorgu = "insert into users (UserName, Password) values (%s, %s)"
        
        cursor.execute(sorgu, (email, password))
        mysql.connection.commit()
        
        cursor.close()
        
        flash("Başarıyla kayıt oldunuz!", "success")
        return redirect(url_for("login"))
    else:
        return render_template("register.html", form=form)
    
#Giriş yapma
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    
    if request.method=="POST":
        email = form.email.data
        password_entered = form.password.data
        
        cursor = mysql.connection.cursor()
        
        sorgu = "select * from users where Username = %s"
        
        result = cursor.execute(sorgu, (email,))
        
        if result > 0:
            data = cursor.fetchone()
            real_password = data["Password"]
            
            if sha256_crypt.verify(password_entered, real_password):
                flash("Başarıyla giriş yapıldı", "success")
                
                session["logged_in"] = True
                session["email"] = email
                
                return redirect(url_for("addpdf"))
            else:
                flash("Parola yanlış", "danger")
                return redirect(url_for("login"))
        else:
            flash("Böyle bir kullanıcı bulunmamaktadır", "danger")
            return redirect(url_for("login"))
    
    return render_template("login.html", form=form)

#Admin giriş yapma
@app.route("/admin", methods=["GET", "POST"])
def admin():
    form = AdminLoginForm(request.form)
    
    if request.method=="POST":
        email = form.email.data
        password = form.password.data
        
        cursor = mysql.connection.cursor()
        
        sorgu = "select * from admin where AdminName = %s"
        
        result = cursor.execute(sorgu, (email,))
        
        if result > 0:
            data = cursor.fetchone()
            real_password = data["Password"]
            
            if password == real_password:
                flash("Başarıyla giriş yapıldı", "success")
                
                session["admin"] = True
                session["email"] = email
                
                return redirect(url_for("index"))
            else:
                flash("Parola yanlış", "danger")
                return redirect(url_for("admin"))
        else:
            flash("Böyle bir admin bulunmamaktadır", "danger")
            return redirect(url_for("admin"))
    
    return render_template("admin.html", form=form)

#Çıkış yapma
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)