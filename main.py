#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MINERADOR DE NOMES PARA DISCORD - TERMUX
DELAY = 0 (MÁXIMA VELOCIDADE)
POR: CRUZ
"""

import requests
import time
import random
import string
import os
import sys
from colorama import init, Fore, Back, Style

init(autoreset=True)

# =============================================================
# ARTE ASCII
# =============================================================
BANNER = f"""
{Fore.CYAN}▓█████▄  ▄▄▄       ███▄    █ ▓█████▄ ▒███████▒
{Fore.CYAN}▒██▀ ██▌▒████▄     ██ ▀█   █ ▒██▀ ██▌▒ ▒ ▒ ▄▀░
{Fore.CYAN}░██   █▌▒██  ▀█▄  ▓██  ▀█ ██▒░██   █▌░ ▒ ▄▀▒░
{Fore.CYAN}░▓█▄   ▌░██▄▄▄▄██ ▓██▒  ▐▌██▒░▓█▄   ▌  ▄▀▒   ░
{Fore.CYAN}░▒████▓  ▓█   ▓██▒▒██░   ▓██░░▒████▓ ▒███████▒
{Fore.CYAN} ▒▒▓  ▒  ▒▒   ▓▒█░░ ▒░   ▒ ▒  ▒▒▓  ▒ ░▒▒ ▓░▒░▒
{Fore.CYAN} ░ ▒  ▒   ▒   ▒▒ ░░ ░░   ░ ▒░ ░ ▒  ▒ ░░▒ ▒ ░ ▒
{Fore.CYAN} ░ ░  ░   ░   ▒      ░   ░ ░  ░ ░  ░ ░ ░ ░ ░ ░
{Fore.CYAN}   ░          ░  ░         ░    ░      ░ ░
{Fore.CYAN} ░                            ░      ░      {Fore.YELLOW}by CRUZ
{Fore.MAGENTA}────────────────────────────────────────────────────────
{Fore.GREEN}OPÇÕES:
{Fore.YELLOW}  4l  -> Busca por 4 LETRAS (a-z)
{Fore.YELLOW}  4c  -> Busca por 4 CARACTERES (a-z, 0-9, _, .)
{Fore.YELLOW}  exit -> Sair
{Fore.MAGENTA}────────────────────────────────────────────────────────
{Fore.RED}ATENÇÃO: DELAY CONFIGURADO COMO 0 (MÁXIMA VELOCIDADE)
{Fore.RED}ISSO PODE CAUSAR RATE LIMIT E BLOQUEIOS.
{Fore.RED}O SCRIPT AGUARDARÁ AUTOMATICAMENTE QUANDO O RATE LIMIT FOR ATINGIDO.
"""

# =============================================================
# CONFIGURAÇÕES
# =============================================================
DOWNLOAD_DIR = os.path.expanduser("~/storage/downloads")
if not os.path.exists(DOWNLOAD_DIR):
    DOWNLOAD_DIR = os.getcwd()
OUTPUT_FILE = os.path.join(DOWNLOAD_DIR, "minernames.txt")

DELAY = 0  # SEM DELAY
TIMEOUT = 10

LETTERS = string.ascii_lowercase
CHARACTERS = string.ascii_lowercase + string.digits + "_."

# =============================================================
# FUNÇÃO DE VERIFICAÇÃO
# =============================================================
def check_username(token, username):
    url = "https://discord.com/api/v9/users/@me"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    payload = {"username": username}
    
    try:
        response = requests.patch(url, headers=headers, json=payload, timeout=TIMEOUT)
        if response.status_code == 200 or response.status_code == 204:
            return True, "disponível"
        if response.status_code == 400:
            data = response.json()
            if "username" in data and "taken" in str(data["username"]).lower():
                return False, "já resgatado"
            else:
                return False, f"erro: {data}"
        elif response.status_code == 429:
            retry_after = response.json().get("retry_after", 5)
            return False, f"rate limit: aguarde {retry_after}s"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, f"exceção: {str(e)}"

# =============================================================
# GERADORES
# =============================================================
def generate_4l():
    return ''.join(random.choices(LETTERS, k=4))

def generate_4c():
    return ''.join(random.choices(CHARACTERS, k=4))

# =============================================================
# REVERTER NOME
# =============================================================
def revert_username(token, original):
    url = "https://discord.com/api/v9/users/@me"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        requests.patch(url, headers=headers, json={"username": original}, timeout=5)
    except:
        pass

# =============================================================
# PRINCIPAL
# =============================================================
def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(BANNER)
    
    token = input(f"{Fore.YELLOW}Digite seu token do Discord (MT...): {Fore.RESET}").strip()
    if not token:
        print(f"{Fore.RED}Token inválido. Saindo.")
        return
    
    current = input(f"{Fore.YELLOW}Digite seu nome de usuário ATUAL: {Fore.RESET}").strip()
    if not current:
        print(f"{Fore.RED}Nome atual necessário. Saindo.")
        return
    
    print(f"{Fore.GREEN}Token e nome configurados. Iniciando com DELAY=0...{Fore.RESET}")
    print(f"{Fore.CYAN}Arquivo de saída: {OUTPUT_FILE}{Fore.RESET}")
    
    found = []
    total = 0
    
    while True:
        mode = input(f"\n{Fore.YELLOW}Escolha o modo (4l / 4c / exit): {Fore.RESET}").strip().lower()
        if mode == "exit":
            break
        if mode not in ("4l", "4c"):
            print(f"{Fore.RED}Modo inválido. Use 4l, 4c ou exit.{Fore.RESET}")
            continue
        
        print(f"{Fore.CYAN}Iniciando busca no modo {mode.upper()}... (Ctrl+C para parar){Fore.RESET}")
        try:
            while True:
                username = generate_4l() if mode == "4l" else generate_4c()
                total += 1
                sys.stdout.write(f"\r{Fore.WHITE}Testando: {username}  [{total}]")
                sys.stdout.flush()
                
                available, msg = check_username(token, username)
                
                if available:
                    revert_username(token, current)
                    found.append(username)
                    with open(OUTPUT_FILE, "a") as f:
                        f.write(f"{username}\n")
                    print(f"\n{Fore.GREEN}[{username}] NÃO RESGATADO!{Fore.RESET}")
                else:
                    if "rate limit" in msg.lower():
                        print(f"\n{Fore.YELLOW}Rate limit! Aguardando...{Fore.RESET}")
                        # Extrai tempo de espera se possível
                        try:
                            wait = float(msg.split("aguarde ")[1].split("s")[0])
                        except:
                            wait = 5
                        time.sleep(wait + 1)
                        continue
                    print(f"\n{Fore.RED}[{username}] já resgatado{Fore.RESET}")
                
                # Delay = 0 (sem pausa)
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Interrompido.{Fore.RESET}")
            break
        except Exception as e:
            print(f"\n{Fore.RED}Erro: {e}{Fore.RESET}")
            break
    
    print(f"\n{Fore.GREEN}Busca finalizada. Nomes não resgatados: {len(found)}{Fore.RESET}")
    if found:
        print(f"{Fore.CYAN}Salvos em: {OUTPUT_FILE}{Fore.RESET}")
        print(f"{Fore.WHITE}Lista: {', '.join(found)}{Fore.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Encerrado.{Fore.RESET}")
    except Exception as e:
        print(f"{Fore.RED}Erro fatal: {e}{Fore.RESET}")
        sys.exit(1)