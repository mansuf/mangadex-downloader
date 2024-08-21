# Enable DNS-over-HTTPS

mangadex-downloader support DoH (DNS-over-HTTPS). 
You can use it in case your router or ISP being not friendly to MangaDex server.

Example usage

```shell
mangadex-dl "https://mangadex.org/title/..." --dns-over-https cloudflare
```

If you're looking for all available providers, [see here](https://requests-doh.mansuf.link/en/stable/doh_providers.html)
