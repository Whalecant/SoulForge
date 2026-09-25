import pygame
import numpy as np
import sys
import os
import numpy as np

def resourcePath(relativePath):
    basePath = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(basePath, relativePath)

class audioManager:
    def __init__ (self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.sounds = { #sfx library
            "jump": pygame.mixer.Sound(resourcePath("assets/music/sfx/jumpSFX.mp3")),
            "land": pygame.mixer.Sound(resourcePath("assets/music/sfx/landSfx.mp3")),
            "walk": pygame.mixer.Sound(resourcePath("assets/music/sfx/walkSFX.wav")),
            "hover": pygame.mixer.Sound(resourcePath("assets/music/sfx/onHover.mp3")),
            "unhover": pygame.mixer.Sound(resourcePath("assets/music/sfx/onUnhover.mp3")),
            "pause": pygame.mixer.Sound(resourcePath("assets/music/sfx/openPauseMenu.mp3")),
        }

        self.currBgm = None
        self.bgmArr = None
        self.bgmSampleRate = pygame.mixer.get_init()[0]
        self.bgmChannel = pygame.mixer.Channel(7)

        self.bgmSpeed = 1.0
        self.bgmSegmentStartSample = 0
        self.bgmSegmentStartTicks = 0
        self.bgmPaused = False

        self.sfxVol = 0.7
        self.bgmVol = 0.25

        self.setSfxVol(self.sfxVol)
        self.setBgmVol(self.bgmVol)

    def playSfx(self, soundName):
        if soundName in self.sounds:
            self.sounds[soundName].play()

    def playBgm(self, filePath, loops=-1, fadeMs=500):
        if self.currBgm == filePath:
            return
        self.currBgm = filePath

        rawSound = pygame.mixer.Sound(resourcePath(filePath))
        self.bgmArr = pygame.sndarray.array(rawSound)

        self.bgmSpeed = 1.0
        self.bgmSegmentStartSample = 0
        self.bgmSegmentStartTicks = pygame.time.get_ticks()

        self.bgmLoops = loops
        self.playFromSample(0)

    def playFromSample(self, startSample):
        segment = self.bgmArr[startSample:]
        if len(segment == 0):
            segment = self.bgmArr
            startSample = 0

        sound = pygame.sndarray.make_sound(segment)
        sound.set_volume(self.bgmVol)
        if self.bgmLoops == -1:
            loops = -1
        else:
            loops = 0

        self.bgmChannel.play(sound, loops = loops, fade_ms= 500)

        self.bgmSegmentStartSample = startSample
        self.bgmSegmentStartTicks = pygame.time.get_ticks()

    def resampleArray(self, array, speed):
        numSamples = array.shape[0]
        newLength = max(1, int(numSamples / speed))
        indices = (np.arange(newLength) * speed).astype(np.int64)
        indices = np.clip(indices, 0, numSamples - 1)
        return array[indices] if array.ndim == 1 else array[indices, :]

    def playSegment(self, startSample):
        segment = self.bgmArr[startSample:]
        if len(segment) == 0:
            segment = self.bgmArr
            startSample = 0

        if self.bgmSpeed != 1.0:
            segment = self.resampleArray(segment, self.bgmSpeed)

        sound = pygame.sndarray.make_sound(segment)
        sound.set_volume(self.bgmVol)
        self.bgmChannel.play(sound, loops = 0)

        self.bgmSegmentStartSample = startSample
        self.bgmSegmentStartTicks  = pygame.time.get_ticks()

    def setBgmSpeed(self, speed):
        if self.bgmArr is None:
            return

        elapsedMs = pygame.time.get_ticks() - self.bgmSegmentStartTicks
        elapsedSamples = int((elapsedMs / 1000.0) * self.bgmSampleRate * self.bgmSpeed)
        currSample = (self.bgmSegmentStartSample + elapsedSamples) % len(self.bgmArr)

        self.bgmSpeed = speed
        self.playSegment(currSample)

    def update(self):
        if self.bgmArr is None or self.bgmPaused:
            return
        if not self.bgmChannel.get_busy() and self.bgmLoops == -1:
            self.playSegment(0)

    def pauseBgm(self):
        if not self.bgmPaused:
            self.bgmChannel.pause()
            self.bgmPaused = True

    def resumeBgm(self):
        if self.bgmPaused:
            self.bgmChannel.unpause()
            self.bgmPaused = False

    def stopBgm(self, fadeMs = 500):
        pygame.mixer.music.fadeout(fadeMs)
        self.currBgm = None

    def setSfxVol(self, vol):
        self.sfxVol = vol
        for sound in self.sounds.values():
            sound.set_volume(self.sfxVol)

    def setBgmVol(self, vol):
        self.bgmVol = vol
        pygame.mixer.music.set_volume(self.bgmVol)