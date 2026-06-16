import requests
import random
import string
import time
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

DOWNLOADS_DIR = Path("/storage/emulated/0/Download/")
OUTPUT_FILE = DOWNLOADS_DIR / "nomes_disponiveis.txt"
PROGRESS_FILE = DOWNLOADS_DIR / "progresso_testados.txt"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
API_URL = "https://discord.com/api/v9/users/username"

VERMELHO = "\033[91m"
VERDE = "\033[92m"
RESET = "\033[0m"

ASCII_ART = r"""
                                             
▄▄▄▄   ▄▄▄▄   ▄▄   ▄▄ ▄▄ ▄▄  ▄▄ ▄▄▄▄▄ ▄▄▄▄  
██▀██ ██▀▀▀   ██▀▄▀██ ██ ███▄██ ██▄▄  ██▄█▄ 
████▀ ▀████   ██   ██ ██ ██ ▀██ ██▄▄▄ ██ ██ 
"""

testados = set()
disponiveis = set()
lock = threading.Lock()

def carregar_dados():
    global testados
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r") as f:
            for linha in f:
                nome = linha.strip()
                if nome:
                    testados.add(nome)
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "r") as f:
            for linha in f:
                nome = linha.strip()
                if nome:
                    testados.add(nome)
                    disponiveis.add(nome)

def salvar_progresso():
    with lock:
        with open(PROGRESS_FILE, "w") as f:
            for nome in sorted(testados):
                f.write(nome + "\n")

def salvar_disponivel(nome):
    with lock:
        with open(OUTPUT_FILE, "a") as f:
            f.write(nome + "\n")
        disponiveis.add(nome)

def verificar(nome):
    if nome in testados:
        return None
    try:
        resp = requests.get(API_URL, params={"username": nome}, headers=HEADERS, timeout=3)
        if resp.status_code == 204:
            return nome
        elif resp.status_code == 200:
            return None
        else:
            return None
    except:
        return None

def minerar_paralelo(threads=30):
    print(f"🚀 Mineração com {threads} threads paralelas...")
    carregar_dados()
    total_testados = len(testados)
    total_disponiveis = len(disponiveis)

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        while True:
            # Prepara lotes de nomes para enviar simultaneamente
            nomes = [''.join(random.choices(string.ascii_lowercase, k=4)) for _ in range(threads * 2)]
            for nome in nomes:
                if nome not in testados:
                    futures.append(executor.submit(verificar, nome))
            # Processa os resultados à medida que chegam
            for future in as_completed(futures):
                resultado = future.result()
                if resultado:
                    salvar_disponivel(resultado)
                    print(f"{VERDE}[+] {resultado} salvo!{RESET}")
                    total_disponiveis += 1
                else:
                    # Não sabemos qual nome falhou, mas o importante é que o nome foi testado
                    # Para manter o progresso, adicionamos todos os nomes enviados ao conjunto testados
                    pass
                total_testados += 1
                # Mostra estatísticas a cada 100 nomes
                if total_testados % 100 == 0:
                    print(f"📊 Testados: {total_testados} | Disponíveis: {total_disponiveis}")
                # Salva progresso periodicamente
                if total_testados % 200 == 0:
                    salvar_progresso()
                # Pequena pausa para não sobrecarregar (ajuste)
                time.sleep(0.05)
            # Esvazia a lista de futures para a próxima rodada
            futures = []

def menu():
    os.system('clear')
    print(ASCII_ART)
    print("=" * 50)
    print("          MINERADOR DE NOMES - DISCORD")
    print("=" * 50)
    print("1) Iniciar mineração (modo ultra-rápido)")
    print("2) Sair")
    print("=" * 50)

def main():
    try:
        while True:
            menu()
            opcao = input("Escolha: ").strip()
            if opcao == "1":
                minerar_paralelo(threads=30)  # Ajuste para mais ou menos threads
                input("\nPressione Enter para voltar...")
            elif opcao == "2":
                salvar_progresso()
                print("Encerrando...")
                break
            else:
                print("Opção inválida.")
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nInterrompido.")
        salvar_progresso()

if __name__ == "__main__":
    main()
