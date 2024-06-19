import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import os
import tkinter as tk
from tkinter import messagebox
import sqlite3

# banco de dados
conn = sqlite3.connect('progress.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS progress
             (id INTEGER PRIMARY KEY, text TEXT, translation TEXT, language TEXT)''')
conn.commit()

def recognize_speech(lang="pt-BR"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Ajustando ao ruído ambiente... Por favor, aguarde.")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Pronto para ouvir. Fale algo...")
        audio = recognizer.listen(source)

    try:
        print("Reconhecendo o áudio...")
        text = recognizer.recognize_google(audio, language=lang)
        print("Você disse: " + text)
        return text
    except sr.UnknownValueError:
        print("Desculpe, não entendi o que você disse.")
        return None
    except sr.RequestError as e:
        print(f"Erro ao solicitar resultados do serviço de reconhecimento de fala; {e}")
        return None

def translate_text(text, dest_lang="en"):
    translator = Translator()
    translation = translator.translate(text, dest=dest_lang)
    print(f"Tradução: {translation.text}")
    return translation.text

def provide_feedback(translated_text, dest_lang="en"):
    tts = gTTS(text=translated_text, lang=dest_lang)
    tts.save("feedback.mp3")
    os.system("mpg321 feedback.mp3")

def save_progress(text, translation, language):
    c.execute("INSERT INTO progress (text, translation, language) VALUES (?, ?, ?)",
              (text, translation, language))
    conn.commit()

def on_translate_click():
    lang = language_var.get()
    dest_lang = "en" if lang == "pt-BR" else "pt"
    original_text = recognize_speech(lang)
    if original_text:
        translated_text = translate_text(original_text, dest_lang)
        provide_feedback(translated_text, dest_lang)
        save_progress(original_text, translated_text, lang)
        messagebox.showinfo("Tradução", f"Original: {original_text}\nTradução: {translated_text}")
    else:
        messagebox.showerror("Erro", "Não foi possível reconhecer a fala. Tente novamente.")

def on_view_progress_click():
    c.execute("SELECT * FROM progress")
    records = c.fetchall()
    progress_window = tk.Toplevel()
    progress_window.title("Progresso do Usuário")
    text = tk.Text(progress_window)
    text.pack()
    for record in records:
        text.insert(tk.END, f"ID: {record[0]}, Texto: {record[1]}, Tradução: {record[2]}, Idioma: {record[3]}\n")

#  GUI
root = tk.Tk()
root.title("Sistema de Aprendizado de Idiomas")

tk.Label(root, text="Escolha o idioma para falar:").pack()
language_var = tk.StringVar(value="pt-BR")
tk.Radiobutton(root, text="Português", variable=language_var, value="pt-BR").pack()
tk.Radiobutton(root, text="Inglês", variable=language_var, value="en").pack()

tk.Button(root, text="Falar e Traduzir", command=on_translate_click).pack()
tk.Button(root, text="Ver Progresso", command=on_view_progress_click).pack()

root.mainloop()

# Fecha a conexão com o banco de dados ao finalizar
conn.close()