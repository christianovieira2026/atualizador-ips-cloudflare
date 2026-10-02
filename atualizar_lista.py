import os
import requests

# 1. Configurações vindas das variáveis secretas do GitHub
TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
LIST_ID = os.getenv("CLOUDFLARE_LIST_ID")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 2. Buscar IPs do Azure Brazil South de uma CDN alternativa super rápida (jsDelivr)
print("Buscando IPs atualizados do Azure (Brazil South)...")
azure_url = "https://jsdelivr.net"

try:
    response = requests.get(azure_url)
    response.raise_for_status()
    ips_lista = response.json()  # Este arquivo já traz direto uma lista de strings ["IP1", "IP2"...]
except Exception as e:
    print(f"Erro ao baixar os IPs do Azure: {e}")
    exit(1)

# Formatando os IPs para o padrão aceito pela API do Cloudflare
ips_brazil_south = [{"ip": ip} for ip in ips_lista]

print(f"Encontrados {len(ips_brazil_south)} IPs para Brazil South.")

if not ips_brazil_south:
    print("Nenhum IP encontrado. Encerrando.")
    exit(1)

# 3. Enviar em massa para a lista do Cloudflare
cf_url = f"https://cloudflare.com{ACCOUNT_ID}/rules/lists/{LIST_ID}/items"

print("Enviando novos IPs para o Cloudflare...")
cf_response = requests.put(cf_url, headers=headers, json=ips_brazil_south)

if cf_response.status_code == 200:
    print("Sucesso! Lista do Cloudflare atualizada com sucesso.")
else:
    print(f"Erro ao atualizar o Cloudflare: {cf_response.status_code}")
    print(cf_response.text)
    exit(1)
