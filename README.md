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
- [Destekleme](#supporting)
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

Daha fazla bilgi için [Read here](https://mangadex-dl.mansuf.link/en/latest/formats.html).

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

Şu şekilde de üykleyebilirsiniz.

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

- Download latest version here -> https://github.com/mansuf/mangadex-downloader/releases
- Extract it.
- [See this instructions to run mangadex-downloader](#command-line-interface-bundled-executable-version)

### How to (Development version) <a id="how-to-development-version"></a>

**NOTE:** You must have git installed. If you don't have it, install it from here https://git-scm.com/.

```shell
git clone https://github.com/mansuf/mangadex-downloader.git
cd mangadex-downloader
python setup.py install
```

## Usage <a id="usage"></a>

### Command-Line Interface (PyPI version) <a id="command-line-interface-pypi-version"></a>

```shell

mangadex-dl "insert MangaDex URL here" 
# or
mangadex-downloader "insert MangaDex URL here" 

# Use this if "mangadex-dl" or "mangadex-downloader" didn't work

# For Windows
py -3 -m mangadex_downloader "insert MangaDex URL here" 

# For Linux / Mac OS
python3 -m mangadex_downloader "insert MangaDex URL here" 
```

### Command-Line Interface (bundled executable version) <a id="command-line-interface-bundled-executable-version"></a>

- Navigate to folder where you downloaded mangadex-downloader
- Open "start cmd.bat" (don't worry it's not a virus, it will open a command prompt)

![example_start_cmd](https://raw.githubusercontent.com/mansuf/mangadex-downloader/main/assets/example_start_cmd.png)

- And then start using mangadex-downloader, see example below:

```shell
mangadex-dl.exe "insert MangaDex URL here" 
```

![example_usage_executable](https://raw.githubusercontent.com/mansuf/mangadex-downloader/main/assets/example_usage_executable.png)

For more example usage, you can [read here](https://mangadex-dl.mansuf.link/en/latest/cli_usage.html)

For more info about CLI options, you can [read here](https://mangadex-dl.mansuf.link/en/latest/cli_ref.html)

### Embedding (API) <a id="embedding-api"></a>

```python
from mangadex_downloader import download

download("insert MangaDex URL here")
```

For more information, you can [read here](https://mangadex-dl.mansuf.link/en/stable/usage_api.html)

## Notes <a id="notes"></a>

### Pornographic and erotica content <a id="pornographic-and-erotica-content"></a>

You may get error `You are not allowed to see ..` when downloading porn and erotica manga. 
This is because mangadex-downloader implement strict rule to porn mangas.

For more info, you can [see it here](https://mangadex-dl.mansuf.link/en/latest/notes/pornographic.html)

## Supporting <a id="supporting"></a>

Like this project ? Considering give this project a star or donate to the current maintainer [@mansuf](https://github.com/mansuf)

The maintainer support these types of donation:

<a href='https://ko-fi.com/A0A04UDJ1' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://cdn.ko-fi.com/cdn/kofi2.png?v=3' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>

*If you're in Indonesia you can donate with saweria*

https://saweria.co/mansuf

## Links <a id="links"></a>

- [PyPI](https://pypi.org/project/mangadex-downloader/)
- [Docs](https://mangadex-dl.mansuf.link)

## Disclaimer <a id="disclaimer"></a>

mangadex-downloader are not affiliated with MangaDex. Also, the current maintainer ([@mansuf](https://github.com/mansuf)) is not a MangaDex dev
