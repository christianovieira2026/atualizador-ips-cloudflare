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

# 2. Baixar IPs oficiais atualizados do Azure
print("Buscando IPs atualizados do Azure...")
azure_url = "https://githubusercontent.com"
azure_data = requests.get(azure_url).json()

ips_brazil_south = []
for value in azure_data.get("values", []):
    if value.get("name") == "AzureCloud.brazilsouth":
        # O Cloudflare precisa do formato {"ip": "regra_cidr"}
        for ip in value["properties"]["addressPrefixes"]:
            ips_brazil_south.append({"ip": ip})

print(f"Encontrados {len(ips_brazil_south)} IPs para Brazil South.")

# 3. Enviar em massa para a lista do Cloudflare (Substituindo a antiga)
# A API do Cloudflare aceita PUT para sobrescrever a lista inteira de uma vez
cf_url = f"https://cloudflare.com{ACCOUNT_ID}/rules/lists/{LIST_ID}/items"

print("Enviando novos IPs para o Cloudflare...")
response = requests.put(cf_url, headers=headers, json=ips_brazil_south)

if response.status_code == 200:
    print("Sucesso! Lista do Cloudflare atualizada com sucesso.")
else:
    print(f"Erro ao atualizar: {response.status_code}")
    print(response.text)
