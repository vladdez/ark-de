# Ark DE

Russian-language knowledge base about emigration from Russia to Germany, prepared from selected Telegram discussions.

First edition: **10 articles and 20 anonymized source summaries**. The imported private archive contains 211,768 messages; this site does **not** expose or search that whole archive.

## Website

Intended GitHub Pages address: <https://vladdez.github.io/ark-de/>.

To enable publishing, open **Settings → Pages**, choose **Deploy from a branch**, then **main** and **/docs**, and save. This follows [GitHub's branch publishing instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

## Build and check

Python 3.10 or later; no third-party packages required:

```sh
python3 scripts/build.py
python3 scripts/check.py
```

Commit the source changes and regenerated `docs/` together. GitHub Pages serves `docs/` directly with Jekyll disabled.

## Content and provenance

- `content/articles.json`: reviewed article copy and official references.
- `content/source_summaries.json`: authored, anonymized paraphrases.
- `content/sources.json`: paraphrases with source message IDs, dates, archive locations and text checksums. No authors or raw messages.
- `assets/`: self-hosted CSS and JavaScript. No external fonts, analytics or runtime dependencies.
- `scripts/build.py`: renders HTML and Markdown, sitemap and topic index.
- `scripts/check.py`: validates local links, source references, page metadata and excluded archive files.
- `docs/`: generated public website.

Source cards are editorial paraphrases, **not verbatim transcripts**. Dates indicate when the underlying discussion occurred. Official sources are listed separately; community observations are not presented as current legal determinations. Original messages remain in the owner's private archive.

Search covers published articles only. HTML content is present without JavaScript; JavaScript provides topic filtering and search. `llms.txt` is a convenience index and does not guarantee crawler access, indexing or exhaustive retrieval.

Ark DE is an independent reference project, not the official website of the Kovcheg organization.
