from flask import Flask, request
import telebot
import os
from moviepy.editor import *
from ShazamAPI import Shazam
from youtubesearchpython import VideosSearch
import youtube_dl
BOT_TOKEN = '5343881224:AAGcPo1wzHjHJQXmok_3bJsjPrqibTRewmQ'
BOT_URL = 'https://firdavsapp.herokuapp.com/'


bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)

def izla(malumot):
    try:
        bot.reply_to(malumot, "Please wait...")
        file_info = bot.get_file(malumot.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = 'videos.mp4'
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        new_file.close()
        #vedioni musikasini kesib olish
        vedio = VideoFileClip(os.path.join("videos.mp4"))
        vedio.audio.write_audiofile(os.path.join("movei_sound.mp3"))
        mp3_file_content_to_recognize = open('movei_sound.mp3', 'rb').read()

        shazam = Shazam(mp3_file_content_to_recognize)
        song = shazam.recognizeSong()
        name = next(song)
        a, b = name
        k = b["track"]
        g= k['title']
        bot.reply_to(malumot,f'Music name: {g}')
        videosSearch = VideosSearch(f'{g}', limit = 2)

        search = videosSearch.result()

        search = search['result']
        search = search[1]
        search = search['link']
        video_url = search
        video_info = youtube_dl.YoutubeDL().extract_info(
            url = video_url,download=False
        )
        filename = f"{g}.mp3"
        options={
            'format':'bestaudio/best',
            'keepvideo':False,
            'outtmpl':filename,
        }

        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([video_info['webpage_url']])

        with open(filename, 'rb') as f:
            music = f.read()
        bot.send_audio(malumot.chat.id, music, title=g)
        
        os.system('rm {}'.format(filename))
    except KeyError:
        bot.reply_to(malumot,'No found...\n Minimal video time 10 second')



@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome shazam bot. Admin: @bitcoin_money_admin \n Please send video!")

@bot.message_handler(content_types=['text'])
def content_text(message):
    bot.reply_to(message, 'Please send video file .')



@bot.message_handler(content_types='video')
def vedio(message):
    izla(malumot=message)
bot.infinity_polling()

@server.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '!', 200

@server.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=BOT_URL)
    return '!', 200


if __name__ == '__main__':
    server.run(host='0.0.0.0', port=int(os.environ.get('POST', 5000)))
