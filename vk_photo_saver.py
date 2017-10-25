# Script Name	: vk_photo_saver.py
# Author	: analyzehim
# Created	: 24th October 2017
#
# Description	: This simple script save all photo attachments form vk chat.
#                 All you need is VK_Token an ChatId.

import requests  # Load Modules
import time
import xml.etree.ElementTree as ET
import shutil
import os

URL = 'https://api.vk.com/method/'


def parse_config():     # Function to get basic constants, like vk_token , chat_id and proxy (if it needed)
    tree = ET.parse('config.xml')
    root = tree.getroot()
    vk_token = root.findall('vk_token')[0].text
    chat_id = root.findall('chat_id')[0].text
    proxy = root.findall('proxy')[0].text
    proxies = {"http": proxy, "https": proxy}
    return vk_token, chat_id, proxies


def download_file(url, file_name):      # Function to download and saving file on disk
    r = requests.get(url, stream=True, proxies=proxies)
    with open(file_name, 'wb') as f:
        shutil.copyfileobj(r.raw, f)
    return True


def get_photo_url(photo_res):       # Function to get URL with the highest resolution from part of VK Response
    if "src_xxxbig" in photo_res:
        return photo_res["src_xxxbig"]
    elif "src_xxbig" in photo_res:
        return photo_res["src_xxbig"]
    elif "src_xbig" in photo_res:
        return photo_res["src_xbig"]
    elif "src_big" in photo_res:
        return photo_res["src_big"]
    elif "src_small" in photo_res:
        return photo_res["src_small"]
    elif "src" in photo_res:
        return photo_res["src"]
    else:
        return


def chat_saver(CHAT_ID):        # Main function, get vk request, and saving photo from this response
    photo_count = 0
    directory = CHAT_ID
    count = 10      # count of photo, grabbing by one time
    if not os.path.exists(directory):   # Saving in directory which name is chat_id
        os.makedirs(directory)
    start_from = ''
    while True:
        vk_method_string = 'messages.getHistoryAttachments?access_token={0}&peer_id={1}&media_type=photo&count={2}&start_from={3}'.format(VK_TOKEN, CHAT_ID, count, start_from)
        r = requests.get(URL + vk_method_string, proxies=proxies)  # HTTP request with proxy
        if r.json()['response'] == [0]:     # blank response - all photo from chat was saved
            break
        for item in r.json()['response']:
            if item == "next_from":     # offset, to make next request
                start_from = r.json()['response'][item]
                continue
            if r.json()['response'][item] == 0:     # system part of response
                continue
            photo_url = get_photo_url(r.json()['response'][item]["photo"])
            filename = directory + '/' + photo_url.split('/')[-1]
            if download_file(photo_url, filename):
                photo_count += 1
                print "{0}: Download {1}".format(photo_count, photo_url)
        time.sleep(5)       # freeze, that not to be banned by VK (a lot of request per time)
    return photo_count


if __name__ == "__main__":
    VK_TOKEN, CHAT_ID, proxies = parse_config()
    chat_saver(CHAT_ID)
