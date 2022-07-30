[![pypi-total-downloads](https://img.shields.io/pypi/dm/mangadex-downloader?label=DOWNLOADS&style=for-the-badge)](https://pypi.org/project/mangadex-downloader)
[![python-ver](https://img.shields.io/pypi/pyversions/mangadex-downloader?style=for-the-badge)](https://pypi.org/project/mangadex-downloader)
[![pypi-release-ver](https://img.shields.io/pypi/v/mangadex-downloader?style=for-the-badge)](https://pypi.org/project/mangadex-downloader)

# mangadex-yükleyicisi

 [MangaDex](https://mangadex.org/)'ten manga yüklemek için komut satırı aracı, [Python](https://www.python.org/)'la yazılmıştır.

## İçindekiler

- [Ana Özellikler](#key-features)
- [Desteklenen Formatlar](#supported-formats)
- [Yükleme](#installation)
    - [Nasıl (PyPI)](#how-to-pypi)
    - [Nasıl (bundled executable)](#how-to-bundled-executable)
    - [Nasıl (Development version)](#how-to-development-version)
- [Kullanımı](#usage)
    - [Komut Satırı Arayüzü (PyPI version)](#command-line-interface-pypi-version)
    - [Komut Satırı Arayüzü (bundled executable version)](#command-line-interface-bundled-executable-version)
    - [Gömülü (API)](#embedding-api)
- [Notlar](#notes)
- [Bağışta bulunun ](#supporting)
- [Linkler](#links)
- [sorumluluk reddi beyanı](#disclaimer)

## Ana Özellikler <a id="key-features"></a>

- Mangadex'ten direk olarak mangayı yada bölümü direk indirin
- Manga yada listeyi kullanıcı kütüphanesinden indirin
- Toplu indirme desteği
- Eski mangadex bağlantısı desteği
- Tarama grupları filtresi desteği
- Doğrulayıcı desteği
- Kaç sayfa yada bölüm indireceğini yönet
- Sıkıştırılmış görüntü desteği
- HTTP / SOCKS proxy desteği
- Farklı dil desteği
- Farklı formatta kaydedebilme raw götü dosyası, PDF, Çizgi roman arşivi (.cbz) yada [Tachiyomi](https://github.com/tachiyomiorg/tachiyomi) lokal manga

***Ve oneshot bölümünü indirmeme özelliği***

## Desteklenen Formatlar <a id="supported-formats"></a>

Daha fazla bilgi için [Burayı okuyun](https://mangadex-dl.mansuf.link/en/latest/formats.html).

## Kurmak <a id="installation"></a>

Nelere ihtiyacınız var:

- Pip ile Python 3.8.x veya üzeri (Windows kullanıyorsanız, paket halindeki yürütülebilir dosyayı indirebilirsiniz. [Nasıl yükleyeceğinizi görün](#how-to-bundled-executable))

Hepsi bukadar.

### Nasıl (PyPI) <a id="how-to-pypi"></a>

Mangadex-downloader kurmak çok kolay, Gereksinimleriniz yeterli olduğu sürece.

```shell
# Windows için
py -3 -m pip install mangadex-downloader

# Linux / Mac OS için
python3 -m pip install mangadex-downloader
```

Şu şekilde de yükleyebilirsiniz.

- [Pillow](https://pypi.org/project/pillow/) PDF desteği ve herhangi bir "single" veya "volume" biçimi için
- [py7zr](https://pypi.org/project/py7zr/) cb7 desteği için

Yada isteğe bağlı olarak bu şekildede yükleyebilirsiniz

```shell
# Windows için
py -3 -m pip install mangadex-downloader[opsiyonel]

# Mac OS / Linux için
python3 -m pip install mangadex-downloader[opsiyonel]
```

Çok kolay, değil mi?

### Nasıl yapılır (bundled executable) <a id="how-to-bundled-executable"></a>

**NOT:** Bu indirme yöntemi sadece Windows için.

Bu paket bundled executable olduğundan, Python'un yüklenmesi gerekmez.

Adımlar:

- En son sürümü buradan indirebilirsiniz -> https://github.com/mansuf/mangadex-downloader/releases
- Dosyayı çıkartın.
- [Mangadex-downloader'ı çalıştırmak için bu talimatlara bakın](#command-line-interface-bundled-executable-version)

### Nasıl (Geliştirici versiyonu) <a id="how-to-development-version"></a>

**NOT:** Git'in yüklü olması gerekir. Eğer yoksa buradan kurabilirsiniz https://git-scm.com/.

```shell
git clone https://github.com/mansuf/mangadex-downloader.git
cd mangadex-downloader
python setup.py install
```

## Kullanımı <a id="usage"></a>

### Komut satırı arayüzü (PyPI sürümü) <a id="command-line-interface-pypi-version"></a>

```shell

mangadex-dl "MangDex linkini buraya yapıştırın" 
# yada
mangadex-downloader "MangDex linkini buraya yapıştırın" 

# "mangadex-dl" veya "mangadex-downloader" çalışmadıysa bunu kullanın

# Windows için
py -3 -m mangadex_downloader "MangDex linkini buraya yapıştırın" 

# Linux / Mac OS için
python3 -m mangadex_downloader "MangDex linkini buraya yapıştırın" 
```

### Komut satırı arayüzü (bundled executable versiyonu) <a id="command-line-interface-bundled-executable-version"></a>

- Mangadex-downloader'ı indirdiğiniz klasöre gidin
- "start cmd.bat" dosyasını açın (merak etmeyim, bu virüs değil bu sadece klasörden cmd açar)

![örnek başlat cmd](https://raw.githubusercontent.com/mansuf/mangadex-downloader/main/assets/example_start_cmd.png)

- Ardından mangadex-downloader'ı kullanmaya başlayın, aşağıdaki örneğe bakın:

```shell
mangadex-dl.exe "MangDex linkini buraya yapıştırın" 
```

![örnek kullanım_ayıklanabilir dosya](https://raw.githubusercontent.com/mansuf/mangadex-downloader/main/assets/example_usage_executable.png)

Daha fazla örnek kullanım için, [burayı oku](https://mangadex-dl.mansuf.link/en/latest/cli_usage.html)

CLI seçenekleri hakkında daha fazla bilgi için [burayı oku](https://mangadex-dl.mansuf.link/en/latest/cli_ref.html)

### Gömülü (API) <a id="embedding-api"></a>

```python
mangadex indiricisinden içe aktarma indirin

download("MangDex linkini buraya yapıştırın")
```

Daha fazla bilgi için, [burayı okuyun](https://mangadex-dl.mansuf.link/en/stable/usage_api.html)

## Notlar <a id="notes"></a>

### Pornografil ve Erotik içerik <a id="pornographic-and-erotica-content"></a>

Bu hatayı alıcaksınız `You are not allowed to see ..` pornografik ve erotik manga indirmeye çalışırken. 
Bunun nedeni, mangadex indiricisinin pornografik ve erotik mangalara katı kurallar uygulamasıdır.

Daha fazla bilgi için, [Burayı Kullanın](https://mangadex-dl.mansuf.link/en/latest/notes/pornographic.html)

## Bağışta bulunun <a id="supporting"></a>

Bu projeyi beğendin mi ? Orijinal projeyi yıldızlayabilirsiniz https://github.com/mansuf/mangadex-downloader veya mevcut ilgileniciye bağış yapın [@mansuf](https://github.com/mansuf)

İlgilenici şu tür bağışları destekler:

<a href='https://ko-fi.com/A0A04UDJ1' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://cdn.ko-fi.com/cdn/kofi2.png?v=3' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>

*Endonezya'daysanız, saweria ile bağış yapabilirsiniz.*

https://saweria.co/mansuf

## Linkler <a id="links"></a>

- [PyPI](https://pypi.org/project/mangadex-downloader/)
- [Docs](https://mangadex-dl.mansuf.link)

## sorumluluk reddi beyanı <a id="disclaimer"></a>

mangadex-downloader MangaDex'e bağlı değildir. Şuan ilgilenen kişi ([@mansuf](https://github.com/mansuf)) mangacix developeri değildir.
