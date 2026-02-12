# 🚴 Projeto Tembici - Análise de Dados de Bike Sharing

## 📋 Sobre o Projeto

Este projeto consiste na consolidação e análise de dados reais de um sistema de compartilhamento de bicicletas (bike sharing), utilizando BigQuery para processamento e integração de múltiplas fontes de dados.

### 🎯 Objetivo

Criar uma base analítica consolidada que permita avaliar a utilização do sistema de bicicletas compartilhadas, analisando padrões de uso, comportamento de clientes, multas e erros operacionais.

---

## 📊 Dashboard e Documentação

- **📈 Dashboard Interativo**: [Looker Studio](https://lookerstudio.google.com/reporting/59a0baed-5d94-45b6-af1f-d052013427ac)
- **📑 Base de Dados Tratada**: [Google Sheets](https://docs.google.com/spreadsheets/d/1F75hEdM7eJ82rbMvhAIXQHXRqHVFHur-QMirec-nyP0/edit?usp=sharing)

---

## 🗂️ Estrutura dos Dados

### Bases de Origem (BRONZE)

O projeto integra 4 bases de dados principais:

1. **VIAGENS** - Informações sobre as viagens realizadas
   - Projeto, cliente, ID da viagem
   - Timestamps de início e fim
   - Duração em segundos
   - Referências de faturamento

2. **CLIENTES** - Dados de assinaturas e perfil dos usuários
   - Informações de cadastro
   - Tipo e periodicidade do plano
   - Status de primeira compra e recorrência
   - Datas de início e fim de assinatura

3. **FATURAS** - Registros de multas e cobranças
   - Status da fatura
   - Valores de multa (usage_fee)
   - Relacionamento com viagens

4. **UNLOCK_ERROS** - Eventos de erro na liberação de bicicletas
   - Timestamp do evento
   - Tipo de erro
   - Identificação do usuário

---

## 🛠️ Tecnologias Utilizadas

- **Google BigQuery** - Data Warehouse e processamento SQL
- **SQL** - Linguagem de consulta e transformação
- **Python** - Conversão de formatos (JSON → Excel)
- **Google Sheets** - Visualização e compartilhamento de dados
- **Looker Studio** - Dashboards e visualizações analíticas

---

## 🚀 Processo de Desenvolvimento

### 1️⃣ Ingestão de Dados no BigQuery

#### Desafios Enfrentados

**Problema com a tabela CLIENTES:**
- A formatação automática do BigQuery não funcionou corretamente
- **Solução**: Upload inicial como STRING seguido de conversão manual dos tipos de dados usando `PARSE_TIMESTAMP()` e `CAST()`

**Problema com encoding de caracteres:**
- Exportação direta para CSV quebrava caracteres especiais (acentuação) devido à codificação LATIN
- **Solução**: 
  1. Extração da base consolidada em formato JSON
  2. Conversão JSON → Excel via Python
  3. Upload do arquivo final no Google Drive

### 2️⃣ Modelagem da Base Consolidada (GOLD)

A tabela analítica final foi estruturada seguindo boas práticas de Data Warehouse:

```sql
CREATE OR REPLACE TABLE `projeto-tembici-487111.GOLD.BD_TEMBICI`
CLUSTER BY PROJETO, CLIENTE, ID_CLIENTE
```

#### Arquitetura da Query

A query utiliza CTEs (Common Table Expressions) para modularizar o processamento:

1. **VIAGENS** - Normalização da base de viagens
2. **FATURAS** - Padronização de multas
3. **CLIENTES** - Tratamento de assinaturas e planos
4. **ERROS_UNLOCK_DEDUP** - Deduplicação de eventos de erro
5. **ERROS_TOTAL_POR_CLIENTE** - Agregação de erros por cliente
6. **VIAGENS_COM_ASSINATURA** - Join temporal entre viagens e assinaturas vigentes
7. **ERROS_NA_DATA_VIAGEM** - Correlação de erros com datas de viagem

#### Principais Transformações

**Tratamento Temporal:**
- Conversão de strings para timestamps
- Extração de dimensões temporais (ano, mês, dia, hora)
- Classificação de períodos do dia (pico manhã, pico tarde, comercial, fora de pico)
- Identificação de dias úteis vs fim de semana

**Categorização de Planos:**
- Normalização de tipos de plano (SHORT → CURTO, LONG → LONGO)
- Padronização de periodicidades (MONTHLY → MENSAL, YEARLY → ANUAL, etc.)
- Tratamento de valores nulos

**Métricas Calculadas:**
- Duração de viagem formatada (HH:MM)
- Agrupamento por faixas de duração (até 15min, até 1h, até 2h, mais de 2h)
- Status de assinatura no momento da viagem
- Agregação de tipos de erro por data

**Lógica de Join Temporal:**
```sql
AND V.INICIO_VIAGEM_TS >= C.INICIO_ASSINATURA_TS
AND (C.FIM_ASSINATURA_TS IS NULL OR V.INICIO_VIAGEM_TS < C.FIM_ASSINATURA_TS)
```
Esta lógica garante que cada viagem seja associada à assinatura vigente no momento de sua realização.

### 3️⃣ Script de Conversão Python

Devido ao volume de dados e limitações do Google Sheets, foi necessário criar um script intermediário:

```python
import pandas as pd

# Leitura do JSON Lines exportado do BigQuery
df = pd.read_json(json_path, lines=True)

# Exportação para Excel preservando encoding
df.to_excel(excel_path, index=False)
```

---

## 📈 KPIs e Métricas Definidas

### KPIs Operacionais

1. **Taxa de Finalização de Viagens**
   - `(Viagens Finalizadas / Total de Viagens) × 100`
   - Mede a confiabilidade do sistema

2. **Duração Média de Viagem**
   - Identifica padrões de uso
   - Segmentado por tipo de plano e período do dia

3. **Taxa de Erro no Unlock**
   - `(Viagens com Erro / Total de Viagens) × 100`
   - Indicador de qualidade da experiência do usuário

### KPIs Financeiros

4. **Receita de Multas**
   - Valor total e distribuição por status de pagamento
   - Análise de inadimplência

5. **Valor Médio por Assinatura**
   - Segmentado por tipo e periodicidade de plano

### KPIs de Comportamento do Cliente

6. **Taxa de Recorrência**
   - `(Clientes Recorrentes / Total de Clientes) × 100`
   - Mede fidelização

7. **Distribuição por Tipo de Plano**
   - Análise de preferência entre planos curtos vs longos
   - Periodicidade mais popular

8. **Horários de Pico**
   - Distribuição de viagens por período do dia
   - Concentração em dias úteis vs fim de semana

### KPIs de Qualidade

9. **Erros Recorrentes por Cliente**
   - Identifica usuários com dificuldades técnicas
   - Oportunidade de suporte proativo

10. **Correlação Erro-Multa**
    - Análise se erros de unlock resultam em multas

---

## 📊 Estrutura de Acompanhamento

### Dashboard Principal

**Visão Geral (Overview)**
- Total de viagens realizadas
- Total de clientes ativos
- Receita total de multas
- Taxa de erro global

**Análise Temporal**
- Viagens por dia/semana/mês
- Sazonalidade de uso
- Comparativo ano a ano (se aplicável)

**Análise de Clientes**
- Distribuição por tipo de plano
- Taxa de conversão (primeira compra → recorrente)
- Tempo médio de assinatura ativa

**Análise Operacional**
- Distribuição de duração de viagens
- Horários de maior demanda
- Mapa de calor (dia da semana × hora)

**Análise de Problemas**
- Top 10 tipos de erro mais frequentes
- Clientes com mais erros
- Taxa de resolução (viagens com erro que finalizaram)

**Análise Financeira**
- Distribuição de status de pagamento de multas
- Valor médio de multa
- Taxa de inadimplência

---

## 🔍 Insights Potenciais

### Operacionais
- Identificar horários que demandam mais bicicletas disponíveis
- Detectar problemas técnicos recorrentes no sistema de unlock
- Otimizar redistribuição de bicicletas baseado em padrões de uso

### Comerciais
- Planos mais populares por perfil de cliente
- Oportunidades de upsell (clientes em planos curtos com uso frequente)
- Campanhas de retenção para clientes com assinatura próxima ao fim

### Financeiros
- Recuperação de multas em aberto
- Análise de custo-benefício por tipo de plano
- Identificação de fraudes ou uso anômalo

---

## 📁 Estrutura de Arquivos

```
projeto-tembici/
│
├── README.md
├── CODIGO_BASE_BIGQUERY.sql        # Query principal de consolidação
├── CONVERSOR_EXCEL.py              # Script de conversão JSON → Excel
│
└── dados/
    └── BASE_TRATADA_TEMBICI.xlsx   # Base consolidada final
```

---

## 🔄 Ingestão Diária

### Estratégia de Atualização

Para manter a base atualizada diariamente, recomenda-se:

1. **Scheduled Query no BigQuery**
   ```sql
   -- Executar diariamente às 2h AM
   -- Processar apenas dados do dia anterior
   WHERE DATE(START_TIME) = CURRENT_DATE() - 1
   ```

2. **Particionamento da Tabela**
   ```sql
   CREATE OR REPLACE TABLE `projeto-tembici-487111.GOLD.BD_TEMBICI`
   PARTITION BY DATE(DATA_VIAGEM)
   CLUSTER BY PROJETO, CLIENTE, ID_CLIENTE
   ```

3. **Incremental Load**
   - Evitar reprocessamento de dados históricos
   - Usar `MERGE` para atualizar registros existentes
   - Inserir apenas novos registros

---

## ⚠️ Limitações e Considerações

1. **Volume de Dados**: Base consolidada muito pesada para exportação direta ao Google Sheets
2. **Encoding**: Caracteres especiais requerem tratamento especial na exportação
3. **Performance**: Query complexa pode ter tempo de execução elevado em grandes volumes
4. **Custo**: Consultas no BigQuery são cobradas por bytes processados

---

## 🎓 Aprendizados

1. Importância de validar encoding logo na ingestão
2. Benefícios de estruturar queries com CTEs para manutenibilidade
3. Uso de clustering para otimizar queries analíticas
4. Necessidade de pipeline de conversão para integração com ferramentas de visualização

---

## 👨‍💻 Autor

Projeto desenvolvido como case técnico de análise de dados.

---

## 📝 Licença

Este projeto contém dados amostrais e é destinado apenas para fins educacionais e demonstração de habilidades técnicas.

---

## 🔗 Links Úteis

- [Documentação BigQuery](https://cloud.google.com/bigquery/docs)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [Looker Studio](https://lookerstudio.google.com/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
