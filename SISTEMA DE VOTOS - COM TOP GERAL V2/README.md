# Sistema de Análise Eleitoral — Rondônia 🗳️

Dashboard interativo e relatório HTML com dados eleitorais do estado de Rondônia (2016–2024).

---

## 📁 Estrutura

```
├── src/
│   ├── data_processor.py   # Carrega e prepara dados_bairros.json
│   ├── analytics.py        # Análises e indicadores eleitorais
│   ├── visualizations.py   # Gráficos Plotly
│   └── dashboard.py        # App Dash para deploy
├── index.html              # Relatório HTML estático (gerado)
├── admin.html              # Painel de administração
├── login.html              # Tela de login
├── app.py                  # Entrada para Gunicorn (produção)
├── main.py                 # Script CLI principal
├── gerar_relatorio.py      # Gerador de relatório HTML estático
├── gerar_summary.py        # Pré-agregador de dados
├── dados_bairros.json      # Dados eleitorais brutos (TSE)
├── dados_summary.json      # Dados pré-agregados (gerado)
├── requirements.txt
├── Procfile                # Heroku / Railway
├── render.yaml             # Render.com
└── runtime.txt
```

---

## 🚀 Como usar

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Gerar relatório HTML estático

```bash
python main.py relatorio
# ou para um ano específico:
python main.py relatorio --year 2024
```

Abre `index.html` em qualquer navegador — sem servidor necessário.

### 3. Iniciar servidor interativo (Dash)

```bash
python main.py servidor
# Acesse: http://localhost:8050
```

### 4. Pré-agregar dados

```bash
python main.py summary
```

---

## 📊 Funcionalidades

- **Relatório HTML estático** com gráficos Plotly interativos (zoom, hover, exportação)
- **Filtros** por ano (2016, 2018, 2020, 2022, 2024) e cargo
- **5 abas**: Visão Geral, Candidatos, Partidos, Geografia, Histórico
- **Visualizações**: barras, treemap, sunburst, linhas temporais
- **Top 20 candidatos** com detalhamento por partido, cargo e município
- **Análise partidária** completa com taxa de eleição e capilaridade
- **Painel de administração** protegido por login

---

## 🗺️ Dados

- **Fonte**: Tribunal Superior Eleitoral (TSE)
- **Período**: 2016 a 2024
- **Eleições**: Municipais (2016, 2020, 2024) e Estaduais/Federais (2018, 2022)
- **Cobertura**: 52 municípios de Rondônia
- **Volume**: ~12.373 candidatos, ~382 localidades

---

## ☁️ Deploy

### Render.com
Conecte o repositório e o `render.yaml` configura tudo automaticamente.

### Heroku / Railway
```bash
git push heroku main
```

### Docker
```bash
docker-compose up
```

---

## 📄 Licença

Dados eleitorais de domínio público (TSE). Código sob licença MIT.
