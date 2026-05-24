import pygame

def play_audio(audio):
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    if not audio:
        return False

    pygame.mixer.music.load(audio)
    pygame.mixer.music.play()
    return True

def stop_audio():
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

def get_audio_length(audio):
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    sound = pygame.mixer.Sound(audio)
    return sound.get_length()
