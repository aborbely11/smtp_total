import smtplib
import socket
from pathlib import Path
import os

def check_user_smtp(server, port, users, method):
    try:
        with smtplib.SMTP(server, port, timeout=10) as smtp:
            smtp.ehlo_or_helo_if_needed()
            results = {}

            for user in users:
                code = None
                msg = ""
                if method == "VRFY":
                    code, msg = smtp.verify(user)
                elif method == "EXPN":
                    code, msg = smtp.expn(user)
                elif method == "RCPT":
                    smtp.mail("<>")
                    code, msg = smtp.rcpt(user)
                else:
                    print(f"Método inválido: {method}")
                    return {}

                msg = msg.decode() if isinstance(msg, bytes) else msg

                if code == 250:
                    status = "✅ EXISTE"
                elif code == 252:
                    status = "⚠️ POSSIVEL"
                elif code in [550, 551, 553]:
                    status = "❌ NÃO EXISTE"
                else:
                    status = f"❓ CÓDIGO {code}"

                results[user] = (code, status, msg)

            return results

    except (smtplib.SMTPException, socket.error) as e:
        print(f"Erro ao conectar: {e}")
        return {}

def listar_wordlists(diretorio):
    arquivos = [f for f in os.listdir(diretorio) if f.endswith('.txt') and os.path.isfile(os.path.join(diretorio, f))]
    return arquivos

def main():
    server = input("🔐 Servidor SMTP (ex: mail.alvo.htb): ").strip()
    port = int(input("🔌 Porta (ex: 25): ").strip())
    method = input("📬 Método (VRFY, RCPT ou EXPN): ").strip().upper()

    print("\n📁 Wordlists disponíveis no diretório atual:")
    wordlists = listar_wordlists('.')
    for i, wl in enumerate(wordlists, 1):
        print(f"[{i}] {wl}")

    escolha = input("\nDigite o número da wordlist ou caminho completo: ").strip()

    if escolha.isdigit() and 1 <= int(escolha) <= len(wordlists):
        wordlist_path = wordlists[int(escolha) - 1]
    else:
        wordlist_path = escolha

    if not Path(wordlist_path).exists():
        print("Arquivo de wordlist não encontrado.")
        return

    try:
        with open(wordlist_path, 'r', encoding='utf-8') as f:
            users = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Erro ao ler a wordlist: {e}")
        return

    if method == "RCPT":
        domain = input("🌐 Domínio de e-mail (ex: alvo.htb): ").strip()
        users = [f"{u}@{domain}" for u in users]

    results = check_user_smtp(server, port, users, method)

    print("\n🧪 RESULTADO:")
    for user, (code, status, msg) in results.items():
        print(f"{user:<25} → {status:<12} | {msg}")

if __name__ == "__main__":
    main()
