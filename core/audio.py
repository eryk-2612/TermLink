import pygame

def toggle_audio(audio = None, toggle = True):
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    if not audio:
        return False

    if toggle:
        pygame.mixer.music.load(audio)
        pygame.mixer.music.play()
        return True
    else:
        pygame.mixer.music.stop()
        return False

def get_audio_length(audio):
    sound = pygame.mixer.Sound(audio)
    return sound.get_length()
