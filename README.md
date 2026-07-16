# mstserver
MASTOWLAR SERVER; sistem izleme, dosya yönetimi ve web terminali sunan hafif ve güvenli bir sunucu panelidir. 🚀

# MASTOWLAR Enterprise Server v2.0 🚀

MASTOWLAR Enterprise Server, yerel ağınızdaki sistemleri tek bir merkezden izlemek, dosya sistemini yönetmek ve terminal komutlarını uzaktan güvenli bir şekilde çalıştırmak için geliştirilmiş hafif (lightweight), güvenli ve kurumsal düzeyde bir sunucu yönetim panelidir.

Flask mimarisi üzerine inşa edilen bu platform, modern ve karanlık temalı bir kullanıcı arayüzü (Dark Neon UI) sunarak sistem yöneticilerinin günlük operasyonlarını kolaylaştırır.

---

## 🔥 Temel Özellikler

* **📊 Anlık Sistem Analitiği:** CPU ve RAM kullanım oranlarını, yerel disklerin doluluk seviyelerini (C:, D: vb.) dinamik grafiklerle saniyeler içinde takip edin.
* **📁 Gelişmiş Dosya Sistemi Yöneticisi:** Sunucu üzerindeki diskler arasında gezinin, klasör/dosya oluşturun, dosyaları indirin veya yerel cihazınızdan sunucuya güvenli bir şekilde dosya yükleyin.
* **💻 Entegre Web Terminali:** Sunucu makinesinde çalıştırmak istediğiniz komutları tarayıcınız üzerinden doğrudan çalıştırın ve çıktıları anında gözlemleyin.
* **🔒 Yetkilendirme ve Kimlik Yönetimi:** İlk girişte varsayılan kimlik bilgileriyle güvenli giriş yapın; dilediğiniz an panel içerisinden yönetici kullanıcı adı ve şifresini güncelleyin.

---

## 🛠️ Kurulum ve Başlangıç

### 1. Gereksinimler
Projeyi çalıştırmadan önce sisteminizde Python x.x ve aşağıdaki kütüphanelerin kurulu olduğundan emin olun:

```bash
pip install flask psutil

Ardından kodun çalıştığı bilgisayar açık olduğu sürece yerel internetinizdeki 192.168.1.x:5000 adresinde çalışır aynı internete bağlı Olan tüm cihazlarda tarayıcınıza girerek 192.168.1.x:5000 adresinizi girerek ulaşabilirsiniz ve bilgisayarınızdaki dosyaları indirebilir cihazdan dosya aktarabilir bilgisayardaki dosyaları silebilirsiniz v.b birçok özellik sunmaktadır iyi kullanımlar.
