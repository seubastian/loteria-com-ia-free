# 🎰 Loteria com IA – Repositório Privado (3Millennium)
**Repositório interno da suíte completa de aplicativos profissionais para análise de loterias com Inteligência Artificial.**

Este é o repositório **privado** da 3Millennium Tecnologia & IA contendo:
- Apps Premium em Streamlit
- Algoritmos proprietários de análise estatística
- Modelos de machine learning
- Mecanismos avançados de filtragem
- Processamento de bases históricas
- Scripts internos de engenharia de dados
- Integração com Google Cloud Storage
- Ferramentas exclusivas da plataforma “Seu Canal da Sorte”

⚠️ **Atenção:**  
Nenhum conteúdo deste repositório pode ser divulgado, clonado, copiado ou distribuído sem autorização expressa da 3Millennium.

---

## 📁 Estrutura Geral

loteria-com-ia/
│
├── apps-premium/
│ ├── mega-sena-premium/
│ ├── lotofacil-premium/
│ ├── quina-premium/
│ └── ...
│
├── libs/
│ ├── filtros/
│ ├── estatisticas/
│ ├── machine_learning/
│ └── utils/
│
├── datasets/
│ ├── (não versionados – carregados via GCS)
│
├── models/
│ ├── xgboost/
│ ├── redes_neurais/
│ └── joblib/
│
├── scripts/
│ ├── atualiza_bases.py
│ ├── pre_processamento.py
│ ├── pipeline_treinamento.py
│
├── .streamlit/
│ └── secrets.toml (não versionado)
└── README.md


---

## 🔧 Tecnologias e Padrões

- Python 3.x  
- Streamlit  
- Pandas / NumPy  
- XGBoost / Scikit-Learn  
- Plotly  
- Google Cloud Storage  
- Railway / Cloud Run (deploy)  
- Padrão empresarial para versionamento e documentação  

---

## 🔒 Dados e Segurança

- Todos os `.csv` de produção são armazenados exclusivamente no **Google Cloud Storage**.  
- O repositório não contém dados confidenciais.  
- Credenciais estão protegidas em `secrets.toml` (não versionado).  
- Acesso restrito a colaboradores autorizados da 3Millennium.

---

## 🛠️ Como rodar localmente

1. Clone o repositório  
```bash
git clone https://github.com/3millennium/loteria-com-ia.git

2- Ative o ambiente virtual

python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate  # Linux/Mac

    Instale dependências

pip install -r requirements.txt

    Execute o app

streamlit run apps-premium/mega-sena-premium/app.py

🧩 Integrações Internas

    Google Cloud Storage (datasets)

    Cloudflare (domínios corporativos)

    Railway / Cloud Run (deploy Premium)

    Automação de atualizações via scripts internos

    APIs externas de sorteios (quando aplicável)

📎 Licença

© 3Millennium Tecnologia & IA – Uso exclusivo corporativo.
Todos os direitos reservados.
📞 Contato Interno

    Desenvolvimento: sebastiao@3millennium.com.br

Suporte técnico: infra@3millennium.com.br


