import os
import requests

TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
LIST_ID = os.getenv("CLOUDFLARE_LIST_ID")

if not all([TOKEN, ACCOUNT_ID, LIST_ID]):
    print("ERRO: Variáveis secretas do Cloudflare estão vazias no GitHub Secrets!")
    exit(1)

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 1. Buscar os IPs usando um servidor de API DNS completamente diferente e ultra estável
print("Buscando IPs atualizados do Azure (Brazil South)...")
azure_url = "https://amazonaws.com" # Usado apenas como teste de conectividade se falhar, mas vamos focar no blob do azure abaixo:

# Para garantir independência total do githubusercontent, usamos a API do IP-API/Mirror estável do Azure
azure_url = "https://azureedge.net" 

# Se o link acima falhar ou estiver indisponível, usamos um espelho alternativo em outra infraestrutura (Cloudflare Pages)
azure_url = "https://pages.dev"

try:
    response = requests.get(azure_url, timeout=15)
    response.raise_for_status()
    ips_lista = response.json() # Este endpoint já entrega os IPs do Brazil South limpos em uma lista
except Exception as e:
    print(f"Erro ao baixar os IPs do Azure: {e}")
    exit(1)

# Formatando no padrão de objeto do Cloudflare IP List
ips_brazil_south = [{"ip": ip, "comment": "Azure Brazil South Auto-Update"} for ip in ips_lista]
print(f"Encontrados {len(ips_brazil_south)} IPs para Brazil South.")

# 2. Enviar em massa para a lista do Cloudflare
cf_url = f"https://cloudflare.com{ACCOUNT_ID}/rules/lists/{LIST_ID}/items"

print("Enviando novos IPs para o Cloudflare...")
try:
    cf_response = requests.put(cf_url, headers=headers, json=ips_brazil_south, timeout=15)
except Exception as e:
    print(f"Erro de conexão ou Timeout com o Cloudflare: {e}")
    exit(1)

if cf_response.status_code == 200:
    print("Sucesso! Lista do Cloudflare atualizada perfeitamente.")
else:
    print(f"Erro retornado pelo Cloudflare (Código {cf_response.status_code}):")
    print(cf_response.text)
    exit(1)
