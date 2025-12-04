import streamlit as st
import pandas as pd
import altair as alt
from statistics import multimode, median

import matplotlib.pyplot as plt

def barra_termometro(min_val, max_val, atual):
    # Garantir que os valores fiquem dentro de 0–100
    min_val = max(0, min(100, min_val))
    max_val = max(0, min(100, max_val))
    if max_val < min_val:
        max_val = min_val

    atual = max(0, min(100, atual))

    # Cores
    cor_fundo = "#00264d"      # azul bem escuro
    cor_faixa = "#1f77b4"      # azul mais claro
    cor_atual = "#ffd700"      # dourado (gold)

    fig, ax = plt.subplots(figsize=(10, 1.4))

    # Fundo 0–100
    ax.barh(
        y=0,
        width=100,
        left=0,
        height=0.6,
        color=cor_fundo
    )

    # Faixa [min, max]
    ax.barh(
        y=0,
        width=max_val - min_val,
        left=min_val,
        height=0.4,
        color=cor_faixa
    )

    # Marcador da posição atual
    largura_atual = 1
    ax.barh(
        y=0,
        width=largura_atual,
        left=atual - largura_atual/2,
        height=0.8,
        color=cor_atual
    )

    # Ajustes visuais
    ax.set_xlim(0, 100)
    ax.set_ylim(-1, 1)
    ax.set_yticks([])
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_xlabel("Escala (0 a 100)")

    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.tight_layout()
    return fig


# ------------------------------------------------------------
# Configuração da página
# ------------------------------------------------------------
st.set_page_config(
    page_title="Aplicativo para Cálculo das Dezenas Atrasadas",
    layout="wide"
)

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
        font-size: 40px;
        margin-bottom: 0.25rem;
    ">
        Aplicativo para Cálculo das Dezenas Atrasadas
    </h1>
    <p style="
        font-family: 'Montserrat', sans-serif;
        color: #F5F7FA;
        font-size: 17px;
        max-width: 900px;
        margin-top: 0.25rem;
        margin-bottom: 1.5rem;
    ">
        Análise estatística dos atrasos por dezena da Mega-Sena, com foco nas dezenas mais atrasadas,
        períodos em que lideraram como Top1 e termômetro visual em escala de 0 a 100 concursos.
    </p>
    """,
    unsafe_allow_html=True
)

# ------------------------------------------------------------
# Upload da base
# ------------------------------------------------------------
uploaded_file = st.file_uploader(
    "📂 Envie o arquivo CSV com os resultados da Mega-Sena",
    type=["csv"]
)

if uploaded_file is None:
    st.stop()


@st.cache_data
def load_data(f):
    # Tenta vírgula e depois ponto-e-vírgula
    for sep in [",", ";"]:
        try:
            df_tmp = pd.read_csv(f, sep=sep)
            if {"Concurso", "Data"}.issubset(df_tmp.columns):
                return df_tmp
        except Exception:
            f.seek(0)
            continue
    f.seek(0)
    return pd.read_csv(f, sep=",")


df = load_data(uploaded_file)

cols_esperadas = {"Concurso", "Data"}
cols_bolas = [c for c in df.columns if c.lower().startswith("bola")]

if not cols_esperadas.issubset(df.columns) or len(cols_bolas) == 0:
    st.error("❌ A base precisa ter as colunas `Concurso`, `Data` e colunas de bolas (`Bola1`, `Bola2`, ...).")
    st.stop()

# Tipos
df["Concurso"] = pd.to_numeric(df["Concurso"], errors="coerce")
df = df.dropna(subset=["Concurso"])
df["Concurso"] = df["Concurso"].astype(int)
df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")

st.success(
    f"✅ Base carregada com **{len(df)} sorteios**. Colunas de bolas detectadas: {', '.join(cols_bolas)}"
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

# ------------------------------------------------------------
# Cálculo dos atrasos + períodos Top1
# ------------------------------------------------------------
todas_dezenas = list(range(1, 61))

# Atraso dinâmico
atraso = {d: 0 for d in todas_dezenas}
# Se a dezena está liderando neste momento
in_lead = {d: False for d in todas_dezenas}
# Quantos períodos completos de liderança
streaks_top1 = {d: 0 for d in todas_dezenas}
# Atrasos máximos por período de liderança
atrasos_max_por_periodo = {d: [] for d in todas_dezenas}
# Atraso máximo do período em andamento
current_period_max = {d: 0 for d in todas_dezenas}

prev_conc = None

for _, row in df_filtrado.iterrows():
    conc = int(row["Concurso"])

    # Em caso de gaps de concurso, consideramos múltiplos sorteios
    if prev_conc is None:
        delta = 1
    else:
        delta = conc - prev_conc
        if delta < 1:
            delta = 1

    # Incrementa atraso de todas as dezenas
    for d in todas_dezenas:
        atraso[d] += delta

    # Zera atraso das dezenas sorteadas neste concurso
    for col in cols_bolas:
        dez = pd.to_numeric(row[col], errors="coerce")
        if pd.notna(dez):
            dez_int = int(dez)
            if dez_int in atraso:
                atraso[dez_int] = 0

    # Determina o maior atraso > 0
    max_atraso = max(atraso.values())
    if max_atraso <= 0:
        # Ninguém atrasado neste ponto
        for d in todas_dezenas:
            in_lead[d] = False
        prev_conc = conc
        continue

    leaders = [d for d, a in atraso.items() if a == max_atraso and a > 0]

    # Atualiza períodos de liderança
    for d in todas_dezenas:
        if d in leaders:
            if not in_lead[d]:
                # Começou um novo período de liderança
                streaks_top1[d] += 1
                current_period_max[d] = atraso[d]
                in_lead[d] = True
            else:
                # Continua no período, atualiza máximo daquele período
                current_period_max[d] = max(current_period_max[d], atraso[d])
        else:
            # Se estava em liderança e saiu, encerra o período
            if in_lead[d]:
                if current_period_max[d] > 0:
                    atrasos_max_por_periodo[d].append(current_period_max[d])
                current_period_max[d] = 0
            in_lead[d] = False

    prev_conc = conc

# Encerra períodos ainda abertos no final do bloco
for d in todas_dezenas:
    if in_lead[d] and current_period_max[d] > 0:
        atrasos_max_por_periodo[d].append(current_period_max[d])
        current_period_max[d] = 0

# ------------------------------------------------------------
# Monta DataFrame final com Moda/Mediana + min/max
# ------------------------------------------------------------
linhas = []
for d in todas_dezenas:
    if atraso[d] > 0:  # desconsidera atraso = 0
        lista = atrasos_max_por_periodo[d]

        if len(lista) == 0:
            atraso_tipico = None
            min_top1 = None
            max_top1 = None
        else:
            min_top1 = min(lista)
            max_top1 = max(lista)

            modos = multimode(lista)
            freq_modo = lista.count(modos[0])

            if freq_modo > 1:
                # Existe moda verdadeira → pega a menor moda
                atraso_tipico = min(modos)
            else:
                # Não há moda (todos diferentes) → usa mediana
                atraso_tipico = median(lista)

        linhas.append(
            {
                "Dezena": d,
                "Atraso_Atual": atraso[d],
                "Qtde_Vezes_Top1": streaks_top1[d],
                "Atraso_Top1_Tipico": atraso_tipico,  # moda ou mediana
                "Atraso_Top1_Min": min_top1,
                "Atraso_Top1_Max": max_top1,
            }
        )

df_res = pd.DataFrame(linhas).sort_values("Atraso_Atual", ascending=False)

st.subheader("📌 Atrasos por dezena (SEM atraso = 0)")
st.dataframe(df_res.reset_index(drop=True), use_container_width=True)

# ------------------------------------------------------------
# Gráfico Top 10 por atraso atual
# ------------------------------------------------------------
top10 = df_res.head(10)

st.subheader("🔝 Top 10 maiores atrasos (entre as dezenas atrasadas)")

chart_top10 = (
    alt.Chart(top10)
    .mark_bar()
    .encode(
        x=alt.X("Dezena:N", sort="-y", title="Dezena"),
        y=alt.Y("Atraso_Atual:Q", title="Atraso (nº de concursos)"),
        tooltip=[
            "Dezena",
            "Atraso_Atual",
            "Qtde_Vezes_Top1",
            "Atraso_Top1_Tipico",
            "Atraso_Top1_Min",
            "Atraso_Top1_Max",
        ],
    )
    .properties(height=400)
)

#st.altair_chart(chart_top10, use_container_width=True)

# ------------------------------------------------------------
# Termômetro com tooltip + animação suave (Plotly)
# ------------------------------------------------------------
import plotly.graph_objects as go

st.subheader("📏 Termômetro de atraso – clique em uma das 10 dezenas mais atrasadas")

top10_dezenas = top10["Dezena"].tolist()

dezena_escolhida = st.radio(
    "Ordem = ranking das mais atrasadas:",
    options=top10_dezenas,
    horizontal=True,
    format_func=lambda x: f"{x:02d}"
)

linha = df_res[df_res["Dezena"] == dezena_escolhida].iloc[0]

min_top1 = linha["Atraso_Top1_Min"]
max_top1 = linha["Atraso_Top1_Max"]
atraso_atual = linha["Atraso_Atual"]

if pd.isna(min_top1) or pd.isna(max_top1):
    st.info(
        f"A dezena **{dezena_escolhida}** nunca liderou como Top1 no bloco selecionado. "
        "Não há faixa histórica de atraso Top1 para mostrar."
    )

else:
    def clamp(v):
        return max(0, min(100, v))

    faixa_ini = clamp(min_top1)
    faixa_fim = clamp(max_top1)
    atual = clamp(atraso_atual)

    # ✅ largura da barra amarela aumentada em 10%
    largura_atual = 1 * 1.10

    fig = go.Figure()

    # Fundo azul escuro (0–100)
    fig.add_trace(go.Bar(
        x=[100],
        y=["Faixa"],
        orientation='h',
        marker=dict(color="#00264d"),
        hoverinfo='skip',
        showlegend=False
    ))

    # Faixa azul clara (min_top1 -> max_top1)
    fig.add_trace(go.Bar(
        x=[faixa_fim - faixa_ini],
        y=["Faixa"],
        orientation='h',
        base=faixa_ini,
        marker=dict(color="rgba(31,119,180,0.40)"),
        hovertemplate=f"Faixa histórica Top1: {min_top1} a {max_top1} concursos<extra></extra>",
        showlegend=False
    ))

    # 🔆 HALO atrás do marcador amarelo (efeito glow estático)
    largura_halo = largura_atual * 2.5
    fig.add_trace(go.Bar(
        x=[largura_halo],
        y=["Faixa"],
        orientation="h",
        base=atual - largura_halo / 2,
        marker=dict(color="rgba(255,215,0,0.20)"),
        hoverinfo="skip",
        showlegend=False
    ))

    # ⭐ Marcador amarelo (com tooltip), 10% mais largo
    fig.add_trace(go.Bar(
        x=[largura_atual],
        y=["Faixa"],
        orientation="h",
        base=atual - largura_atual / 2,
        marker=dict(
            color="#FFD700",
            line=dict(color="white", width=2)
        ),
        hovertemplate=f"<b>Atraso atual:</b> {atraso_atual} concursos<extra></extra>",
        showlegend=False
    ))

    # Layout + transição suave quando mudar de dezena
    fig.update_layout(
        barmode='overlay',
        height=120,
        margin=dict(l=30, r=30, t=40, b=20),
        xaxis=dict(range=[0, 100], title="Escala (0 a 100 concursos)"),
        yaxis=dict(showticklabels=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        transition=dict(
            duration=450,
            easing="cubic-in-out"
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"""
        **Interpretação para a dezena {dezena_escolhida:02d}:**

        - A faixa azul representa os atrasos em que a dezena já foi **Top1**  
          (**{int(min_top1)}** a **{int(max_top1)}** concursos).
        - O marcador amarelo (com barra 10% mais larga) indica o **atraso atual**: **{int(atraso_atual)}** concursos.  
        - A escala é padronizada entre **0 e 100** concursos para facilitar comparação.
        """
    )
