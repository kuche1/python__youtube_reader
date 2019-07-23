




import os
import socket
from urllib.parse import quote_plus as quote
import code as pycode
from tempfile import TemporaryFile
from time import time
import urllib

from bs4 import BeautifulSoup
import requests
import pytube

import moviepy.editor


def main(c):
    meth = c.meth
    url = c.url
    
    print(meth)
    
    if meth == 'GET':
        if url == '/':
            c.send('''HTTP/1.1 200 OK
Content-Type: text/html
\n''')
            c.sendfile('default-resp.html')
            
        else:
            
            if url in ['/favicon.ico']:
                return
        
        
            MOST_KEYERRORS = 5
            count = 0
            while count < MOST_KEYERRORS:
                try:
                    yt = pytube.YouTube(url)
                except KeyError:
                    count += 1
                except pytube.exceptions.RegexMatchError:
                    print(f'invalid link: {url}')
                    return
                else:
                    break
            else:
                print('Keyerror flood')
                return
                        
            fn = str(time()).replace('.','-')

            stream = yt.streams.filter(progressive=True,type='video').last()
            try:
                stream.download('cache',fn)
            except urllib.error.HTTPError:
                return
            
            
            for (d,fols,fils) in os.walk('cache'):
                for fil in fils:
                    if fil.startswith(fn):
                        fd = f'{d}/{fil}'
                        break
                break
            
            
            audiofd = f'{fd}.mp3'
            
            clip = moviepy.editor.VideoFileClip(fd)
            
            clip.audio.write_audiofile(audiofd, verbose=False, logger=None) #silent
            #clip.audio.write_audiofile(audiofd) #loud
            
            clip.close()
            
            file_name = stream.default_filename
            ext_ind = -len(file_name.split('.')[-1]) -1
            file_name = f'{file_name[:ext_ind]}.mp3'
            
            c.send(f'''HTTP/1.1 200 OK
Content-disposition: attachment; filename="{file_name}"
\n''')
            c.sendfile(audiofd)
            
            os.remove(fd)
            os.remove(audiofd)

            
            
            
            
            
        return
            

        
        
    
    
    if ':' in meth:
        ind = meth.index(':')
        meth = meth[ind+1:]
            
    if ';' in meth:
        ind = meth.index(';')
        r = meth[:ind]
        d = meth[ind+1:]
    else:
        r = meth
        
    if r == 'search':
        
        source = requests.get(f'https://www.youtube.com/results?search_query={quote(d)}').text
        soup = BeautifulSoup(source,'lxml')
        divs = [d for d in soup.find_all('div') if d.has_attr('class') and 'yt-lockup-dismissable' in d['class'] ]
        for d in divs:
            
            a=[]
            for i in d.find_all('a'):
                if i.has_attr('title'):
                    a.append(i)
            a = a[0]
            link = a['href']
            title = a['title']
            
            #img = d.find_all('img')[0]['src']
            
            c.send(f'{link}\n{title}\n')#{img}\n')
        

