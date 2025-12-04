import streamlit as st
import pandas as pd
import altair as alt


# ------------------------------------------------------------
# Configuração da página
# ------------------------------------------------------------
#st.set_page_config(
    #page_title="Aplicativo para Cálculo da Frequência de Dezenas",
   # layout="wide"
#)

# ------------------------------------------------------------
# Estilo global (cores + fonte da tela inicial)
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Importa Montserrat Extra Bold (alternativa à Gotham Bold) */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800&display=swap');

    /* Fundo azul em degradê, estilo Caixa */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0066CC 0%, #008ED4 50%, #00AAB8 100%);
    }

    /* Remove fundo padrão do header do Streamlit */
    [data-testid="stHeader"] {
        background: rgba(0, 0, 0, 0);
    }

    /* Ajuste geral de fonte para o app (opcional) */
    body, p, label, span, div {
        font-family: "Montserrat", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------------------------------------------
# Título customizado
# ------------------------------------------------------------
st.markdown(
    """
    <h1 style="
        font-family: 'Montserrat', sans-serif;
        font-weight: 800;
        color: #FFFFFF;
        font-size: 25px;
        margin-bottom: 0.15rem;
    ">
        Aplicativo para Cálculo da Frequência de Dezenas
    </h1>
    <p style="
        font-family: 'Montserrat', sans-serif;
        color: #F5F7FA;
        font-size: 15px;
        max-width: 900px;
        margin-top: 0.15rem;
        margin-bottom: 1.5rem;
    ">
        Este aplicativo calcula a frequência de cada dezena da Mega-Sena,
    considerando **apenas o bloco de sorteios que você escolher**
    </p>
    """,
    unsafe_allow_html=True
)



# ==============================
# Upload da base
# ==============================
uploaded_file = st.file_uploader(
    "📂 Envie o arquivo CSV com os resultados da Mega-Sena",
    type=["csv"]
)

if uploaded_file is None:
    st.info("⏳ Aguardando o upload do arquivo CSV...")
    st.stop()

# Tentativa de leitura do CSV
@st.cache_data
def load_data(file):
    # Tenta com vírgula, depois com ponto e vírgula
    for sep in [",", ";"]:
        try:
            df_tmp = pd.read_csv(file, sep=sep)
            if {"Concurso", "Data"}.issubset(df_tmp.columns):
                return df_tmp
        except Exception:
            file.seek(0)  # volta ponteiro do arquivo
            continue
    # Se chegou aqui, tenta pelo menos carregar algo
    file.seek(0)
    return pd.read_csv(file, sep=",")


df = load_data(uploaded_file)

# Validação básica
cols_esperadas = {"Concurso", "Data"}
cols_bolas = [c for c in df.columns if c.lower().startswith("bola")]

if not cols_esperadas.issubset(df.columns) or len(cols_bolas) == 0:
    st.error(
        "❌ A base precisa ter, no mínimo, as colunas `Concurso`, `Data` e as colunas de bolas (`Bola1`, `Bola2`, ...)."
    )
    st.stop()

# Garantir tipos adequados
df["Concurso"] = pd.to_numeric(df["Concurso"], errors="coerce")
df = df.dropna(subset=["Concurso"])
df["Concurso"] = df["Concurso"].astype(int)

# Converter data
df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")

st.success(
    f"✅ Base carregada com **{len(df)} sorteios** e colunas de bolas: {', '.join(cols_bolas)}"
)

# ------------------------------------------------------------
# Seleção do bloco de sorteios — apenas por intervalo de Concurso
# ------------------------------------------------------------
st.sidebar.header("🎯 Bloco de Análise (por Concurso)")

min_conc = int(df["Concurso"].min())
max_conc = int(df["Concurso"].max())

ini, fim = st.sidebar.slider(
    "Intervalo de concursos",
    min_value=min_conc,
    max_value=max_conc,
    value=(min_conc, max_conc),
    step=1
)

df_filtrado = df[(df["Concurso"] >= ini) & (df["Concurso"] <= fim)]

st.markdown(
    f"🔢 <b>Bloco selecionado:</b> concursos de <b>{ini}</b> a <b>{fim}</b> "
    f"({len(df_filtrado)} sorteios)",
    unsafe_allow_html=True
)

if df_filtrado.empty:
    st.warning("⚠️ Nenhum sorteio encontrado nesse bloco.")
    st.stop()

df_filtrado = df_filtrado.sort_values("Concurso")

# ==============================
# Cálculo da frequência das dezenas
# ==============================
# Empilhar todas as bolas do bloco selecionado
valores = df_filtrado[cols_bolas].values.ravel()

# Converte para inteiros válidos (ignorando NaN)
series_dezenas = pd.to_numeric(pd.Series(valores), errors="coerce").dropna().astype(int)

# Considera dezenas de 1 a 60
todas_dezenas = range(1, 61)
freq = series_dezenas.value_counts().reindex(todas_dezenas, fill_value=0)

df_freq = pd.DataFrame(
    {
        "Dezena": list(freq.index),
        "Frequência": freq.values
    }
)

st.subheader("📈 Frequência das dezenas no bloco selecionado")
st.dataframe(df_freq.style.format({"Frequência": "{:.0f}"}), use_container_width=True)

# ==============================
# Top 10 Máximos e Mínimos
# ==============================
top10_max = df_freq.sort_values("Frequência", ascending=False).head(10)
top10_min = df_freq.sort_values("Frequência", ascending=True).head(10)

col1, col2 = st.columns(2)

with col1:
    st.markdown(
    """
    <h3 style="font-size:30px; margin-bottom:4px; font-weight:700;">
        Top 10 dezenas <b>mais</b> sorteadas
    </h3>
    """,
    unsafe_allow_html=True
)

    chart_max = (
        alt.Chart(top10_max)
        .mark_bar()
        .encode(
            x=alt.X("Dezena:N", sort="-y", title="Dezena"),
            y=alt.Y("Frequência:Q", title="Quantidade"),
            tooltip=["Dezena", "Frequência"]
        )
        .properties(height=400)
    )
    st.altair_chart(chart_max, use_container_width=True)

with col2:
    st.markdown(
    """
    <h3 style="font-size:30px; margin-bottom:4px; font-weight:700;">
        Top 10 dezenas <b>menos</b> sorteadas
    </h3>
    """,
    unsafe_allow_html=True
    )
    chart_min = (
        alt.Chart(top10_min)
        .mark_bar()
        .encode(
            x=alt.X("Dezena:N", sort="y", title="Dezena"),
            y=alt.Y("Frequência:Q", title="Quantidade"),
            tooltip=["Dezena", "Frequência"]
        )
        .properties(height=400)
    )
    st.altair_chart(chart_min, use_container_width=True)

st.markdown("---")
st.caption("App gerado automaticamente para análise de frequência de dezenas por bloco de sorteios da Mega-Sena.")
