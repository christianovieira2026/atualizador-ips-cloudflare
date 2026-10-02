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

# 2. Baixar IPs oficiais atualizados do Azure (URL Corrigida)
print("Buscando IPs atualizados do Azure...")
azure_url = "https://githubusercontent.com"

try:
    response = requests.get(azure_url)
    response.raise_for_status()
    azure_data = response.json()
except Exception as e:
    print(f"Erro ao baixar os IPs do Azure: {e}")
    exit(1)

ips_brazil_south = []
for value in azure_data.get("values", []):
    if value.get("name") == "AzureCloud.brazilsouth":
        for ip in value["properties"]["addressPrefixes"]:
            ips_brazil_south.append({"ip": ip})

print(f"Encontrados {len(ips_brazil_south)} IPs para Brazil South.")

if not ips_brazil_south:
    print("Nenhum IP encontrado para a região especificada. Encerrando.")
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
