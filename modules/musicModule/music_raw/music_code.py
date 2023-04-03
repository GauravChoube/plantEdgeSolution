from scipy.io.wavfile import write
import numpy as np
import pygame
import pygame._sdl2.audio as sdl2_audio


samplerate = 44100 
base_music = "./twinkle-twinkle.wav"

def get_devices(capture_devices: bool = False):
    init_by_me = not pygame.mixer.get_init()
    if init_by_me:
        pygame.mixer.init()
    devices = tuple(sdl2_audio.get_audio_device_names(capture_devices))
    if init_by_me:
        pygame.mixer.quit()
    return devices
 

def get_piano_notes():
    '''
    Returns a dict object for all the piano 
    note's frequencies
    '''
    # White keys are in Uppercase and black keys (sharps) are in lowercase
    octave = ['C', 'c', 'D', 'd', 'E', 'F', 'f', 'G', 'g', 'A', 'a', 'B'] 
    # base_freq = 261.63 #Frequency of Note C4
     #Frequency of Note C4
    global base_freq
    note_freqs = {octave[i]: base_freq * pow(2,(i/12)) for i in range(len(octave))}       
    note_freqs[''] = 0.0
    return note_freqs
    
def get_wave(freq, duration=0.3):
    music_amplitude = 4096
    t = np.linspace(0, duration, int(samplerate * duration))
    wave = music_amplitude * np.sin(2 * np.pi * freq * t)
    
    return wave
        
def get_song_data(music_notes):
    note_freqs = get_piano_notes()
    song = [get_wave(note_freqs[note]) for note in music_notes.split('-')]
    song = np.concatenate(song)
    return song.astype(np.int16)
    

def music():
    #Notes of "twinkle twinkle little star"
    music_notes = 'C-C-G-G-A-A-G--F-F-E-E-D-D-C'
    
    # next line create song object (Music file)
    data = get_song_data(music_notes)
    data = data * (16300/np.max(data))
    write(base_music, samplerate, data.astype(np.int16))


    # audioDeviceList = ('bcm2835 Headphones, bcm2835 Headphones', 'vc4-hdmi-0, MAI PCM i2s-hifi-0', 'vc4-hdmi-1, MAI PCM i2s-hifi-0') #get_devices()
    # print("list of audio device :",audioDeviceList)
    # device=audioDeviceList[0]
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(base_music)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
    pygame.quit()

def musicPlay(amplitude):    
      print("Plant signal data: ", amplitude)
      global base_freq
      base_freq = amplitude /10  
      # the above value we can vary after checking which amplitude needs which note and equate accordingly
      
      # print("Base freq: " ,base_freq)
      music()