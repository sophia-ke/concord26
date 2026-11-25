# Concord 26 — 康迎医疗网站

Bilingual (简体中文 / English) static website for Shanghai Concord Medical, live on GitHub Pages.

- Chinese pages at the root, English pages in `en/`.
- Language is chosen automatically (saved choice → browser language → visitor's country), and can be switched with the 🌐 menu.
- Pages are generated: edit `_build/build.py` (page text, layout) or `_build/i18n_en.py` (English product text), then run

```bash
python3 -I _build/build.py .
```
