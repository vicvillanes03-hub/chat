import queue
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

from dotenv import load_dotenv
from google import genai

import time


MODELO = "gemini-3.5-flash-lite"  # troque se quiser usar outro modelo

load_dotenv()
try:
    client = genai.Client()
except Exception as e:
    raise SystemExit(f"Erro ao iniciar o cliente (confira o .env): {e}")

fila = queue.Queue()


import time

def consultar(pergunta):
    for tentativa in range(3):
        try:
            resposta = client.models.generate_content(model=MODELO, contents=pergunta)
            fila.put(("Gemini", resposta.text))
            return
        except Exception as e:
            if "503" in str(e) and tentativa < 2:
                time.sleep(2 * (tentativa + 1))  # espera 2s, depois 4s
                continue
            fila.put(("Erro", str(e)))
            return

def mostrar(autor, texto):
    conversa.config(state="normal")
    conversa.insert(tk.END, f"{autor}:\n", "autor")
    conversa.insert(tk.END, f"{texto}\n\n")
    conversa.config(state="disabled")
    conversa.see(tk.END)


def verificar_fila():
    try:
        autor, texto = fila.get_nowait()
    except queue.Empty:
        root.after(100, verificar_fila)
        return
    mostrar(autor, texto)
    botao.config(state="normal", text="Enviar")
    entrada.focus()


def enviar(event=None):
    pergunta = entrada.get().strip()
    if not pergunta:
        return
    mostrar("Você", pergunta)
    entrada.delete(0, tk.END)
    botao.config(state="disabled", text="Pensando...")
    threading.Thread(target=consultar, args=(pergunta,), daemon=True).start()
    root.after(100, verificar_fila)


root = tk.Tk()
root.title("Chat com Gemini")
root.geometry("600x500")

conversa = ScrolledText(root, wrap="word", state="disabled", padx=10, pady=10)
conversa.tag_config("autor", font=("Arial", 10, "bold"), foreground="#1a5fb4")
conversa.pack(fill="both", expand=True, padx=10, pady=(10, 5))

barra = tk.Frame(root)
barra.pack(fill="x", padx=10, pady=(0, 10))

entrada = tk.Entry(barra, font=("Arial", 11))
entrada.pack(side="left", fill="x", expand=True, ipady=5)
entrada.bind("<Return>", enviar)
entrada.focus()

botao = tk.Button(barra, text="Enviar", command=enviar, width=10)
botao.pack(side="right", padx=(8, 0))

root.mainloop()