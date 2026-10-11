# -*- coding: utf-8 -*-
# Sylheti TTS Transliteration NVDA Add-on
# Author: ashu-choudhury
# License: MIT

import ctypes
import os
import globalPluginHandler
import scriptHandler
import speech
import ui
from logHandler import log

_lib = None
_plugin_dir = os.path.dirname(__file__)
is_64bit = ctypes.sizeof(ctypes.c_void_p) == 8

candidate_dlls = []
if is_64bit:
    candidate_dlls = ["sylheti_phonetics_x64.dll", "sylheti_phonetics.dll"]
else:
    candidate_dlls = ["sylheti_phonetics_x86.dll", "sylheti_phonetics.dll"]

for dll_name in candidate_dlls:
    dll_path = os.path.join(_plugin_dir, dll_name)
    if os.path.isfile(dll_path):
        try:
            temp_lib = ctypes.CDLL(dll_path)
            temp_lib.sylheti_convert_to_hindi.argtypes = [ctypes.c_char_p]
            temp_lib.sylheti_convert_to_hindi.restype = ctypes.c_void_p
            temp_lib.sylheti_free_string.argtypes = [ctypes.c_void_p]
            temp_lib.sylheti_free_string.restype = None
            _lib = temp_lib
            log.info("sylheti_tts: Successfully loaded %s (64-bit=%s)" % (dll_name, is_64bit))
            break
        except Exception as e:
            log.error("sylheti_tts: Error loading %s: %s" % (dll_name, e), exc_info=True)

if not _lib:
    log.error("sylheti_tts: Could not load any compatible sylheti_phonetics DLL for 64-bit=%s" % is_64bit)


def convert_text(text: str) -> str:
    """
    Converts text using the native sylheti_phonetics engine.
    Guaranteed: On ANY error, null return, or empty result, ALWAYS returns the original text.
    """
    global _lib
    if not text or not text.strip() or not _lib:
        return text

    try:
        encoded = text.encode("utf-8")
        ptr = _lib.sylheti_convert_to_hindi(encoded)
        if not ptr:
            return text

        try:
            converted_bytes = ctypes.string_at(ptr)
            if converted_bytes:
                result = converted_bytes.decode("utf-8")
                if result and result.strip():
                    return result
            return text
        finally:
            _lib.sylheti_free_string(ptr)
    except Exception as e:
        log.error("sylheti_tts: Error converting %r: %s" % (text, e), exc_info=True)
        return text


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = "Sylheti TTS"

    def __init__(self):
        super().__init__()
        self.enabled = True
        try:
            speech.filter_speechSequence.register(self.filterSpeech)
            log.info("sylheti_tts: Registered filter_speechSequence successfully.")
        except Exception as e:
            log.error("sylheti_tts: Failed to register filter_speechSequence: %s" % e, exc_info=True)

    def terminate(self):
        try:
            speech.filter_speechSequence.unregister(self.filterSpeech)
            log.info("sylheti_tts: Unregistered filter_speechSequence.")
        except Exception as e:
            log.error("sylheti_tts: Failed to unregister filter_speechSequence: %s" % e, exc_info=True)
        super().terminate()

    def filterSpeech(self, speechSequence):
        if not self.enabled or not speechSequence:
            return speechSequence

        try:
            new_sequence = []
            for item in speechSequence:
                if isinstance(item, str):
                    converted = convert_text(item)
                    new_sequence.append(converted if converted else item)
                else:
                    new_sequence.append(item)

            return new_sequence
        except Exception as e:
            log.error("sylheti_tts: Error in filterSpeech: %s" % e, exc_info=True)
            return speechSequence

    @scriptHandler.script(
        description="Toggles Sylheti speech transliteration on or off.",
        gesture="kb:NVDA+shift+y",
    )
    def script_toggleSylheti(self, gesture):
        self.enabled = not self.enabled
        if self.enabled:
            ui.message("Sylheti transliteration enabled")
        else:
            ui.message("Sylheti transliteration disabled")
