import vlc
p = None

def play_sound(file_name):
    global p

    if p != None:
        if p.is_playing():
            p.stop()
            
    p = vlc.MediaPlayer(file_name)
    p.audio_output_set('alsa')
    p.audio_output_device_set('alsa', u'sysdefault:CARD=ALSA')
    p.play()

def stop_sound():
    global p

    if p == None:
        return

    if p.is_playing():
        p.stop()


