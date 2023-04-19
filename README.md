# ThreadGPT

Experimenting with the OpenAI API and discord.

A small bot, that can be configured with a custom system message.
It can output GIFs (via Tenor) and Images (via DALL-E).

## How to use

Install dependencies with `pip install -r requirements.txt`.
Create a `.env` file and set the variables, that are present in `template.env`.

If everything went fine, just run `src/main.py`.

## Info

The current `system.txt` is very questionable and should be changed.

If you want image generation and gif querying you have to include something along the lines of:
```
If you would like to respond with a gif insert the following exactly:
[GIF: <search term>]
Info: <search term> should be replaced by you with whatever gif you want to use, it will be replaced with the actual GIF. The more you write in your search term the better the result.

If you would like to show an image of your thought you can using the following syntax, follow it exactly:
[DALL-E: <thought>]
INFO <thought> should be replaced by whatever you want to show the chat, for example "white cat" would show a picture of a white cat.
```