#Imports
from django.shortcuts import render
from django.contrib import messages
from .forms import DownloadForm
from pytube import YouTube
from math import pow, floor, log
from datetime import timedelta


# Convert from bytes
def convertsize(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(floor(log(size_bytes, 1024)))
    p = pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

# Convert long numbers
def humanformat(number):
    units = ['', 'K', 'M', 'B', 'T', 'Q']
    k = 1000.0
    magnitude = int(floor(log(number, k)))
    return '%.2f%s' % (number / k**magnitude, units[magnitude])

#When click search button
def download_video(request, string=""):
    global context
    form = DownloadForm(request.POST or None)
    if form.is_valid():
        video_url = form.cleaned_data.get("url")
        try:
            yt_obj = YouTube(video_url)
        except:
            messages.error(request, 'Invalid URL.')
            return render(request, 'home.html',{ 'form': form })

        try:
            videos = yt_obj.streams.filter(is_dash=False).desc()
            audios = yt_obj.streams.filter(only_audio=True).order_by('abr').desc()
        except:
            messages.error(request, 'Invalid URL.')
            return render(request, 'home.html',{ 'form': form })

        video_audio_streams = []
        audio_streams = []

        # List of video streams dictionaries
        for s in videos:
            video_audio_streams.append({
                'resolution' : s.resolution,
                'extension' : s.mime_type.replace('video/',''),
                'file_size' : convertsize(s.filesize),
                'video_url' : s.url
            })
        
        # List of audio streams dictionaries
        for s in audios:
            audio_streams.append({
                'resolution' : s.abr,
                'extension' : s.mime_type.replace('audio/',''),
                'file_size' : convertsize(s.filesize),
                'video_url' : s.url
            })

        # Full content to render
        context = {
            'form' : form,'title' : yt_obj.title,
            'rating': int(yt_obj.rating), 'rating_check' : int(yt_obj.rating) + 1 if float(int(yt_obj.rating)) != yt_obj.rating else 6,
            'rating_list' : [1,2,3,4,5], 'thumb' : yt_obj.thumbnail_url, 'author' : yt_obj.author,
            'author_url' : yt_obj.channel_url,
            'duration' : str(timedelta(seconds=yt_obj.length)), 'views' : humanformat(yt_obj.views) if yt_obj.views >= 1000 else yt_obj.views,
            'stream_audio' : audio_streams, 'streams' : video_audio_streams
        }

        return render(request, 'home.html', context)
        
    return render(request, 'home.html',{ 'form': form })

