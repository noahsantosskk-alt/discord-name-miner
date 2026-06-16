import requests
import random
import string
import time
import os
import threading
import sys
from pathlib import Path

# ================== CONFIGURAÇÕES ==================
DOWNLOADS_DIR = Path("/storage/emulated/0/Download/")
OUTPUT_FILE = DOWNLOADS_DIR / "nomes_disponiveis.txt"
PROGRESS_FILE = DOWNLOADS_DIR / "progresso_testados.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
API_URL = "https://discord.com/api/v9/users/username"

# Cores ANSI (funcionam no Termux)
VERMELHO = "\033[91m"
VERDE = "\033[92m"
RESET = "\033[0m"

# ================== ARTES ASCII ==================
ASCII_ART = r"""
                                             
▄▄▄▄   ▄▄▄▄   ▄▄   ▄▄ ▄▄ ▄▄  ▄▄ ▄▄▄▄▄ ▄▄▄▄  
██▀██ ██▀▀▀   ██▀▄▀██ ██ ███▄██ ██▄▄  ██▄█▄ 
████▀ ▀████   ██   ██ ██ ██ ▀██ ██▄▄▄ ██ ██ 
"""

# ================== VARIÁVEIS GLOBAIS ==================
minerando = False
thread_mineracao = None
evento_parar = threading.Event()

# Conjunto para evitar repetir nomes testados
testados = set()

# ================== FUNÇÕES DE ARQUIVO ==================
def carregar_progresso():
    global testados
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r") as f:
            for linha in f:
                nome = linha.strip()
                if nome:
                    testados.add(nome)
        print(f"✅ Carregados {len(testados)} nomes já testados.")

def salvar_progresso():
    with open(PROGRESS_FILE, "w") as f:
        for nome in sorted(testados):
            f.write(nome + "\n")

def carregar_disponiveis():
    """Adiciona os nomes já salvos ao conjunto de testados para não re-verificar."""
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "r") as f:
            for linha in f:
                nome = linha.strip()
                if nome:
                    testados.add(nome)

def salvar_disponivel(nome):
    with open(OUTPUT_FILE, "a") as f:
        f.write(nome + "\n")

# ================== FUNÇÃO DE VERIFICAÇÃO ==================
def verificar_disponibilidade(nome):
    try:
        resp = requests.get(API_URL, params={"username": nome}, headers=HEADERS, timeout=5)
        if resp.status_code == 204:
            return True
        elif resp.status_code == 200:
            return False
        else:
            # Se for 429 (rate limit), espera e tenta novamente? Vamos apenas retornar False
            return False
    except Exception:
        return False

# ================== THREAD DE MINERAÇÃO ==================
def minerar():
    global testados, minerando
    print("🚀 Mineração iniciada! (Pressione 2 para sair)\n")
    contador = 0
    while not evento_parar.is_set():
        # Gerar nome aleatório de 4 letras
        nome = ''.join(random.choices(string.ascii_lowercase, k=4))
        if nome in testados:
            continue

        disponivel = verificar_disponibilidade(nome)
        testados.add(nome)
        contador += 1

        if disponivel:
            salvar_disponivel(nome)
            print(f"{VERDE}[+] {nome} salvo!{RESET}")
        else:
            print(f"{VERMELHO}[-] {nome} já resgatado{RESET}")

        # Salvar progresso a cada 50 testes
        if contador % 50 == 0:
            salvar_progresso()

        # Aguardar para não sobrecarregar a API (ajuste conforme necessário)
        time.sleep(0.3)

    # Ao sair do loop, salvar progresso final
    salvar_progresso()
    print("⏹️  Mineração interrompida.")

# ================== FUNÇÃO PARA INICIAR A THREAD ==================
def iniciar_mineracao():
    global thread_mineracao, minerando, evento_parar
    if minerando:
        print("⚠️  A mineração já está em andamento.")
        return
    evento_parar.clear()
    minerando = True
    thread_mineracao = threading.Thread(target=minerar, daemon=True)
    thread_mineracao.start()

def parar_mineracao():
    global minerando, evento_parar
    if not minerando:
        return
    evento_parar.set()
    minerando = False
    if thread_mineracao and thread_mineracao.is_alive():
        thread_mineracao.join(timeout=1)

# ================== MENU PRINCIPAL ==================
def exibir_menu():
    os.system('clear')  # Limpa a tela
    print(ASCII_ART)
    print("=" * 50)
    print("          MINERADOR DE NOMES - DISCORD")
    print("=" * 50)
    print("1) Iniciar mineração")
    print("2) Sair")
    print("=" * 50)

def main():
    # Carregar progresso ao iniciar
    carregar_progresso()
    carregar_disponiveis()

    try:
        while True:
            exibir_menu()
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                iniciar_mineracao()
                input("\nPressione Enter para voltar ao menu...")
            elif opcao == "2":
                print("Encerrando...")
                parar_mineracao()
                break
            else:
                print("Opção inválida. Tente novamente.")
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.")
    finally:
        parar_mineracao()
        salvar_progresso()
        print(f"✅ Progresso salvo. Total de nomes testados: {len(testados)}")
        print(f"📁 Nomes disponíveis salvos em: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
