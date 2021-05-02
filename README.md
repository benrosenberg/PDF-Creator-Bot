# PDF Creator

Discord bot that creates PDFs from Markdown messages. Also includes functionality as an image uploader for insertion into Markdown files.

### Requirements

 - Python (3.7.3 and up should be fine, newer is better)
 - discord.py
 - `python-dotenv` (can be installed with `pip`)
 - [Pandoc](https://pandoc.org/)
 - `curl`
 - LaTeX (a full installation of [TeX Live](https://www.tug.org/texlive/) should be fine)
 - ImageMagick

### Usage

1. Put bot token in a `.env` file in the same directory as `bot.py`
2. Run `python bot.py` (or `python3 bot.py`, depending on your Python installation)
3. Follow instructions [here](https://bots.thief.fyi/#PDF%20Creator) and [here](https://bots.thief.fyi/PDFCreator/) (somewhat outdated -- YAML headers have been removed as they were buggy)
