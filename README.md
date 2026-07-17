# mstserver
MASTOWLAR SERVER; sistem izleme, dosya yönetimi ve web terminali sunan hafif ve güvenli bir sunucu panelidir. 🚀

## 🏡 Kullanım Alanları (Ev & İş Yerleri)

MASTOWLAR Enterprise Server v2.0, esnek ve kaynak tüketmeyen mimarisi sayesinde hem kişisel hem de profesyonel ortamlarda güvenle kullanılabilir:

* **Ev Kullanıcıları İçin (Personal/Home Lab):** Evinizdeki eski bir bilgisayarı veya sunucuyu multimedya deposu ya da kişisel sunucu olarak kullanıyorsanız; panele evdeki diğer bilgisayarlardan veya telefonlardan bağlanarak sistem sıcaklığını/durumunu izleyebilir, içerideki dosyalarınızı kolayca yönetebilirsiniz.
* **İş Yerleri İçin (SMB / Enterprise Office):** Küçük ve orta ölçekli ofislerde, yerel ağda (LAN) çalışan dosya sunucularınızı (File Server) veya şirket içi test makinelerinizi teknik ekibin tarayıcı üzerinden uzaktan yönetmesini, dosya transferi yapmasını ve gerektiğinde güvenli terminal komutları çalıştırmasını sağlar.

*Not: Güvenliğiniz için iş yeri ve ev ağlarında sistemi ilk kez başlattıktan sonra varsayılan yönetici şifresini değiştirmeyi unutmayınız.*

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
