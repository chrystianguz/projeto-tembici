import pandas as pd

# Caminho do arquivo
json_path = r"C:\Users\CHRYSTIAN.5654\Desktop\CÓDIGOS\PROJETO_T\BASE\BASE_TRATADA.json"
excel_path = r"C:\Users\CHRYSTIAN.5654\Desktop\CÓDIGOS\PROJETO_T\BASE\BASE_TRATADA.xlsx"

# Ler JSON Lines
df = pd.read_json(json_path, lines=True)

# Exportar para Excel
df.to_excel(excel_path, index=False)

print("Arquivo convertido com sucesso!")
