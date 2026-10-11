# -*- coding: utf-8 -*-
# Sylheti TTS Transliteration NVDA Add-on
# Author: ashu-choudhury
# License: MIT

import ctypes
import os
import re
import globalPluginHandler
import scriptHandler
import speech
import ui
from logHandler import log

_lib = None
_plugin_dir = os.path.dirname(__file__)
is_64bit = ctypes.sizeof(ctypes.c_void_p) == 8

# Priority candidate DLLs based on architecture
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

# Common Sylheti markers to distinguish Sylheti messages from general Windows UI text
SYLHETI_MARKERS = {
    "kila", "keela", "killa", "aso", "asho", "acho", "asi", "ashi", "achi",
    "bala", "bhala", "baala", "khani", "khaani", "fani", "faani", "pani",
    "zairam", "jairam", "sairam", "zao", "jao", "zaitam", "jaitam", "zaiba", "jaiba",
    "khoro", "koro", "khorray", "korray", "khorbo", "korbo", "khoriya", "koriya",
    "khaiso", "khaiba", "khamu", "boiya", "jiroiram", "zirairam", "dekhi", "dekhba",
    "kotha", "khotha", "koitam", "koytam", "ajke", "aji", "kalike", "kailke",
    "bihane", "behane", "shonjebela", "sonjebela", "raite", "rayte", "ekhon", "aikhon",
    "bade", "baade", "ghor", "ghoro", "bazar", "dukan", "khosoba", "roid", "biromber",
    "oigese", "lagbo", "shonge", "songe", "kita", "kono", "koy", "khene", "kisu", "kichu",
    "emne", "cha", "bhat", "salun", "gusto", "gush", "fua", "pua", "furi", "puri",
    "amra", "tumra", "tain", "tore", "bhai", "bhay", "bon", "boin", "ni",
}


def should_transliterate(text: str) -> bool:
    """Checks if the text contains recognizable Sylheti vocabulary or Nagri script."""
    if not text:
        return False

    # If text already contains Sylheti Nagri Unicode characters, transliterate
    for ch in text:
        if 0xA800 <= ord(ch) <= 0xA82F:
            return True

    # Check words against Sylheti marker set
    tokens = re.findall(r"[A-Za-z]+", text.lower())
    for token in tokens:
        if token in SYLHETI_MARKERS:
            return True

    return False


def convert_text(text: str) -> str:
    """
    Converts Romanized Sylheti text to Hindi Devanagari phonetics.
    ALWAYS returns the original text on any failure or if the text is not Sylheti.
    """
    global _lib
    if not text or not text.strip():
        return text

    # Only modify text that actually contains Sylheti words
    # This prevents Windows UI (Desktop, Taskbar, Menus) from being turned into Devanagari!
    if not should_transliterate(text):
        return text

    if not _lib:
        log.debug("sylheti_tts: Library not loaded; returning original text")
        return text

    try:
        encoded = text.encode("utf-8")
        ptr = _lib.sylheti_convert_to_hindi(encoded)
        if not ptr:
            log.warning("sylheti_tts: Native function returned null pointer for input: %r" % text)
            return text

        try:
            converted_bytes = ctypes.string_at(ptr)
            if converted_bytes:
                converted_str = converted_bytes.decode("utf-8")
                # Safety check: if converted string is empty, fallback to original
                if converted_str and converted_str.strip():
                    return converted_str
            return text
        finally:
            _lib.sylheti_free_string(ptr)
    except Exception as e:
        log.error("sylheti_tts: Conversion exception on %r: %s" % (text, e), exc_info=True)
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
        if not self.enabled:
            return

        try:
            new_sequence = []
            for item in speechSequence:
                if isinstance(item, str) and item.strip():
                    converted = convert_text(item)
                    # Guaranteed: Never append an empty string!
                    new_sequence.append(converted if converted else item)
                else:
                    new_sequence.append(item)

            speechSequence[:] = new_sequence
        except Exception as e:
            # Absolute failsafe: NVDA must NEVER stop speaking
            log.error("sylheti_tts: Critical error in filterSpeech: %s" % e, exc_info=True)

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
