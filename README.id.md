[![pypi-total-downloads](https://img.shields.io/pypi/dm/mangadex-downloader?label=DOWNLOADS&style=for-the-badge)](https://pypi.org/project/mangadex-downloader)
[![python-ver](https://img.shields.io/pypi/pyversions/mangadex-downloader?style=for-the-badge)](https://pypi.org/project/mangadex-downloader)
[![pypi-release-ver](https://img.shields.io/pypi/v/mangadex-downloader?style=for-the-badge)](https://pypi.org/project/mangadex-downloader)

# mangadex-downloader

Sebuah alat antarmuka baris perintah untuk mengunduh manga dari [MangaDex](https://mangadex.org/), 
ditulis di bahasa [Python](https://www.python.org/)

## Daftar isi

- [Fitur utama](#fitur-utama)
- [Format yang didukung](#format-yang-didukung)
- [Instalasi](#instalasi)
    - [Python Package Index (PyPI)](#instalasi-pypi)
    - [Satu paket aplikasi](#instalasi-satu-paket-aplikasi)
    - [Versi perkembangan](#instalasi-versi-perkembangan)
- [Pemakaian](#pemakaian)
    - [Versi PyPI](#pemakaian-versi-pypi)
    - [Versi satu paket aplikasi](#pemakaian-versi-satu-paket-aplikasi)
- [Berkontribusi](#berkontribusi)
- [Donasi](#donasi)
- [Daftar tautan](#tautan)
- [Penafian (disclaimer)](#penafian)

## Fitur utama

- Mengunduh manga, bab, atau daftar manga langung dari MangaDex
- Mengunduh manga atau daftar manga dari pustaka pengguna
- Cari dan unduh tautan MangaDex dari forums MangaDex ([https://forums.mangadex.org/](https://forums.mangadex.org/))
- Mendukung batch download
- Mendukung tautan lama MangaDex
- Mendukung penyaringan grup scanlation
- Mendukung autentikasi
- Kendalikan berapa banyak bab dan lembar yang anda ingin unduh
- Mendukung gambar yang terkompresi
- Mendukung HTTP / SOCKS proxy
- Mendukung DNS-over-HTTPS
- Mendukung banyak bahasa
- Simpan dalam gambar, EPUB, PDF, Comic Book Archive (.cbz atau .cb7)

***Dan kemampuan untuk tidak mengunduh bab oneshot***

## Format yang didukung <a id="format-yang-didukung"></a>

[Baca disini](https://mangadex-dl.mansuf.link/en/latest/formats.html) untuk informasi lebih lanjut.

## Instalasi <a id="instalasi"></a>

Berikut aplikasi yang anda butuhkan:

- Python versi 3.8.x atau keatas dengan Pip (Jika OS anda adalah Windows, anda bisa mengunduh satu paket aplikasi. 
[Lihat instruksi berikut untuk memasangnya](#instalasi-satu-paket-aplikasi))

### Python Package Index (PyPI) <a id="instalasi-pypi"></a>

Menginstalasi mangadex-downloader sangat mudah asalkan anda mempunyai aplikasi yang dibutuhkan

```shell
# Untuk Windows
py -3 -m pip install mangadex-downloader

# Untuk Linux / Mac OS
python3 -m pip install mangadex-downloader
```

Anda juga bisa menginstal dependensi opsional

- [py7zr](https://pypi.org/project/py7zr/) untuk dukungan cb7
- [orjson](https://pypi.org/project/orjson/) untuk performa maksimal (cepat JSON modul)
- [lxml](https://pypi.org/project/lxml/) untuk dukungan EPUB

Atau anda bisa menginstal semua opsional dependensi

```shell
# Untuk Windows
py -3 -m pip install mangadex-downloader[optional]

# Untuk Mac OS / Linux
python3 -m pip install mangadex-downloader[optional]
```

Sudah selesai deh, gampang kan ?

### Satu paket aplikasi <a id="instalasi-satu-paket-aplikasi"></a>

**Catatan:** Instalasi ini hanya untuk OS Windows saja.

Karena ini satu paket aplikasi, Python tidak harus diinstal

Langkah-langkah:

- Unduh versi terbaru disini -> [https://github.com/mansuf/mangadex-downloader/releases](https://github.com/mansuf/mangadex-downloader/releases)
- Ekstrak hasil unduhan tersebut
- Selamat, anda telah berhasil menginstal mangadex-downloader.
[Lihat instruksi berikut untuk menjalankan mangadex-downloader](#usage-bundled-executable-version)

### Versi perkembangan <a id="instalasi-versi-perkembangan"></a>

**Catatan:** Anda harus mempunyai git. Jika anda tidak mempunyainya, instal dari sini [https://git-scm.com/](https://git-scm.com/)

```shell
git clone https://github.com/mansuf/mangadex-downloader.git
cd mangadex-downloader
python setup.py install # atau "pip install ."
```

## Pemakaian <a id="pemakaian"></a>

### Versi PyPI <a id="pemakaian-versi-pypi"></a>

```shell

mangadex-dl "Masukan tautan MangaDex disini"
# atau
mangadex-downloader "Masukan tautan MangaDex disini" 

# Gunakan ini jika "mangadex-dl" atau "mangadex-downloader" tidak bekerja

# Untuk Windows
py -3 -m mangadex_downloader "Masukan tautan MangaDex disini" 

# Untuk Linux / Mac OS
python3 -m mangadex_downloader "Masukan tautan MangaDex disini" 
```

### Versi satu paket aplikasi <a id="pemakaian-versi-satu-paket-aplikasi"></a>

- Arahkan ke tempat dimana anda mengunduh mangadex-downloader
- Buka "start cmd.bat" (jangan khawatir ini bukan virus, ini akan membuka command prompt)

![example_start_cmd](https://raw.githubusercontent.com/mansuf/mangadex-downloader/main/assets/example_start_cmd.png)

- Lalu kita bisa memakai mangadex-downlaoder, lihat contoh dibawah:

```shell
mangadex-dl.exe "Masukan tautan MangaDex disini" 
```

![example_usage_executable](https://raw.githubusercontent.com/mansuf/mangadex-downloader/main/assets/example_usage_executable.png)

Untuk lebih banyak contoh tentang pemakaian, 
[anda bisa baca disini](https://mangadex-dl.mansuf.link/en/stable/cli_usage/index.html)

Untuk informasi lebih lanjut tentang opsi CLI, 
[Anda bisa baca disini](https://mangadex-dl.mansuf.link/en/stable/cli_ref/index.html)

## Berkontribusi <a id="berkontribusi"></a>

Lihat [CONTRIBUTING.md](https://github.com/mansuf/mangadex-downloader/blob/main/CONTRIBUTING.md) untuk info lebih lanjut

## Donasi <a id="donasi"></a>

Jika anda suka dengan project ini, tolong pertimbangkan untuk donasi ke salah satu website ini:

- [Sociabuzz](https://sociabuzz.com/mansuf/donate)
- [Github Sponsor](https://github.com/sponsors/mansuf)

Setiap jumlah yang diterima akan diapresiasi 💖

## Daftar tautan <a id="tautan"></a>

- [PyPI](https://pypi.org/project/mangadex-downloader/)
- [Docs](https://mangadex-dl.mansuf.link)

## Penafian (disclaimer) <a id="penafian"></a>

mangadex-downloader tidak bersangkutan dengan MangaDex. 
Dan pengelola yang sekarang ([@mansuf](https://github.com/mansuf)) bukan seorang MangaDex developer