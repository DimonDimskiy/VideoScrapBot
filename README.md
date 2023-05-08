# VideoScrapBot
This is simple telegram bot that downloads videos from received URLs and sends them back to user as a mediafile.
## How to run
To run bot you should add .env file with TOKEN="yourtoken_here". After adding file use
```
docker-compose up --build
```

## Dependencies
- For downloading used yt-dlp https://github.com/yt-dlp/yt-dlp . 
- Library used in bot implementation  https://github.com/python-telegram-bot/python-telegram-bot .
- Postprocessing (such ass convertation files into mp4) requires ffmpeg installed on system, not just pip installed, but apt-get installed. Anywhay it was taken to account while Dockerfile was written, so you dont need to install anything else while using docker.


