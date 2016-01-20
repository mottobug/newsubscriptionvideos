#!/usr/bin/python

import sys
import pdb
import os
import socket

import subprocess
from subprocess import Popen, PIPE, STDOUT  

# pip install google-api-python-client
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "<DEVELOPER_KEY>"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def getVideos():

  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

  print("Fetching Subscription list")
  all_subscriptions = []
  subscriptions_list_request = youtube.subscriptions().list(
    part="snippet",
    channelId="<CHANNEL_ID>",
    maxResults=50,
  )
  while subscriptions_list_request:
    subscriptions_list_response = subscriptions_list_request.execute()
    for subscriptions_list_item in subscriptions_list_response['items']:
      all_subscriptions.append(subscriptions_list_item)
    subscriptions_list_request = youtube.subscriptions().list_next(subscriptions_list_request, subscriptions_list_response)

  print("Total subscriptions: %s" % len(all_subscriptions))
  
  videos = []
  for subscriptions in all_subscriptions:
    channel_id = subscriptions['snippet']['resourceId']['channelId']
  
    channel_response = youtube.channels().list(
      part="contentDetails",
      id=channel_id,
      maxResults=50
    ).execute()
    
    print("Getting Upload-Playlist-ID for %s" % subscriptions['snippet']['title'])
    for channel_item in channel_response['items']:

      playlist_id = channel_item['contentDetails']['relatedPlaylists']['uploads']
      playlist_request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults = 50
      )
      loops = 0
      while playlist_request:
        loops = loops + 1
        playlist_request_response = playlist_request.execute()
        for playlist_item in playlist_request_response['items']:
          videos.append({
            "id": playlist_item['snippet']['resourceId']['videoId'],
            "title": playlist_item['snippet']['title'],
            "description": playlist_item['snippet']['description'],
            "date": playlist_item['snippet']['publishedAt'],
            "channel": playlist_item['snippet']['channelTitle'],
          })

        playlist_request = youtube.playlistItems().list_next(playlist_request, playlist_request_response) 
      
      print(len(videos))
  svideos = sorted(videos, key=lambda k: k['date'], reverse=True)

  return(svideos)

def get_lock(process_name):
  global lock_socket
  lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
  try:
    lock_socket.bind('\0' + process_name)
  except socket.error:
    print "already running"
    sys.exit()

if __name__ == "__main__":
  
  get_lock('youtubeDownloadNewSubScriptionVideos')
  
  for video in getVideos():
    print(video['id'])
