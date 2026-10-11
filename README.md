# sylheti-tts (NVDA Add-on) 🗣️

> **NVDA Add-on for Real-Time Sylheti Speech Transliteration**  
> Powered by the high-performance native [`sylheti_phonetics`](https://crates.io/crates/sylheti_phonetics) Rust engine.

---

## 🎯 What This Add-on Does

When reading WhatsApp, Telegram, or social media messages in Romanized Sylheti (*"Kila aso bhai? Khani khaiso ni? Office-o meeting-e aisi"*), standard English and Bengali synthesizers butcher the words.

This add-on hooks directly into NVDA's speech pipeline (`filter_speechSequence`):
1. **Intercepts incoming speech text** in real time before it reaches your synthesizer.
2. **Runs it through the native `sylheti_phonetics` engine** in microseconds.
3. **Converts Sylheti words to authentic Devanagari phonetics** (`कीला आसो भाइ? ख़ानी ख़ाइसो नी?`) while keeping English loanwords smooth and natural.
4. **Passes the audio-ready text to your synthesizer** so it sounds like authentic native Sylheti speech!

---

## 🚀 Installation

1. Download or locate [`sylheti-tts.nvda-addon`](sylheti-tts.nvda-addon).
2. Press **Enter** on `sylheti-tts.nvda-addon` (or install via NVDA Menu $\to$ **Tools** $\to$ **Manage add-ons** $\to$ **Install**).
3. Confirm installation and restart NVDA.

---

## ⌨️ Shortcuts & Usage

* **Toggle Transliteration On/Off:**  
  Press **`NVDA + Shift + Y`**  
  * NVDA will announce: *"Sylheti transliteration enabled"* or *"Sylheti transliteration disabled"*.
* **Custom Gestures:**  
  You can reassign the shortcut anytime via **NVDA Menu** $\to$ **Preferences** $\to$ **Input Gestures** $\to$ **Sylheti TTS**.

---

## 🔊 Recommended Synthesizers

For the best experience, select a **Hindi or multilingual TTS voice**:
* **Nuance Vocalizer (Recommended):** *Lekha* or *Neel*
* **Windows OneCore:** Hindi voice (Kalpana / Hemant)
* **eSpeak NG:** Hindi (`hi`)

---

## 🛠️ Building From Source

```bash
python build_addon.py
```

This will produce `sylheti-tts.nvda-addon`.
