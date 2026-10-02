import os
import re
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

print("Buscando IPs atualizados diretamente da infraestrutura Microsoft Azure...")

try:
    # 1. Acessa a página oficial de downloads da Microsoft para obter o link do arquivo JSON semanal
    download_page_url = "https://microsoft.com"
    page_response = requests.get(download_page_url, timeout=20)
    page_response.raise_for_status()
    
    # 2. Usa expressão regular para capturar o link direto do JSON de download hospedado no domínio da Microsoft
    matches = re.findall(r'href="(https://download\.microsoft\.com/[^"]+\.json)"', page_response.text)
    
    if not matches:
        raise ValueError("Não foi possível encontrar o link do JSON na página oficial da Microsoft.")
        
    direct_azure_url = matches[0]
    print(f"Baixando o arquivo oficial: {direct_azure_url}")
    
    # 3. Baixa o JSON oficial direto do domínio microsoft.com
    azure_response = requests.get(direct_azure_url, timeout=20)
    azure_response.raise_for_status()
    azure_data = azure_response.json()

except Exception as e:
    print(f"Erro ao interagir com a infraestrutura da Microsoft: {e}")
    exit(1)

# 4. Filtra o JSON oficial procurando pelo Brazil South
ips_brazil_south = []
for value in azure_data.get("values", []):
    if value.get("name") == "AzureCloud.brazilsouth":
        for ip in value["properties"]["addressPrefixes"]:
            ips_brazil_south.append({"ip": ip, "comment": "Azure Brazil South Auto-Update"})

print(f"Encontrados {len(ips_brazil_south)} IPs para Brazil South.")

if not ips_brazil_south:
    print("Nenhum IP encontrado no arquivo JSON oficial. Encerrando.")
    exit(1)

# 5. Envia os dados para a API do Cloudflare
cf_url = f"https://cloudflare.com{ACCOUNT_ID}/rules/lists/{LIST_ID}/items"
print("Enviando novos IPs para o Cloudflare...")

try:
    cf_response = requests.put(cf_url, headers=headers, json=ips_brazil_south, timeout=15)
except Exception as e:
    print(f"Erro de conexão com o Cloudflare: {e}")
    exit(1)

if cf_response.status_code == 200:
    print("Sucesso! Lista do Cloudflare atualizada perfeitamente.")
else:
    print(f"Erro retornado pelo Cloudflare (Código {cf_response.status_code}):")
    print(cf_response.text)
    exit(1)
