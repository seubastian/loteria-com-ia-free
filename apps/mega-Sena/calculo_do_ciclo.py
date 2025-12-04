import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


# ------------------------------------------------------------
# Configuração da página
# ------------------------------------------------------------
#st.set_page_config(
 #   page_title="Aplicativo para Cálculo dos Ciclos da Mega Sena",
  #  layout="wide"
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
# Título customizado da tela inicial
# ------------------------------------------------------------
st.markdown(
    """
    <h1 style="
        font-family: 'Montserrat', sans-serif;
        font-weight: 800;
        color: #FFFFFF;
        font-size: 30px;
        margin-bottom: 0.25rem;
    ">
        Aplicativo para Cálculo dos Ciclos da Mega-Sena
    </h1>
    <p style="
        font-family: 'Montserrat', sans-serif;
        color: #F5F7FA;
        font-size: 17px;
        max-width: 900px;
        margin-top: 0.25rem;
        margin-bottom: 1.5rem;
    ">
        Um ciclo se encerra quando todas as 60 dezenas foram sorteadas. 
        Esta ferramenta mostra o status do ciclo atual e estatísticas de tendência central (Média, Moda, Mediana) dos ciclos passados.
    </p>
    """,
    unsafe_allow_html=True
)

# --- 1. Upload do Arquivo ---
st.sidebar.header("Carregar Dados")
uploaded_file = st.sidebar.file_uploader("Faça upload do CSV (RESULTADOS_MEGASENA.csv)", type=["csv"])

@st.cache_data
def carregar_dados(file):
    try:
        df = pd.read_csv(file)
        cols_bolas = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
        df[cols_bolas] = df[cols_bolas].apply(pd.to_numeric, errors='coerce')
        return df.sort_values(by='Concurso')
    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")
        return None

def calcular_ciclos(df):
    """
    Percorre todos os sorteios para determinar o histórico de ciclos e o estado atual.
    """
    ciclos_fechados = []
    
    # Estado do ciclo atual
    dezenas_no_ciclo = set()
    inicio_ciclo = 1
    numero_ciclo = 1
    
    todas_dezenas = set(range(1, 61))
    
    for idx, row in df.iterrows():
        concurso = row['Concurso']
        sorteadas = {row['Bola1'], row['Bola2'], row['Bola3'], row['Bola4'], row['Bola5'], row['Bola6']}
        
        dezenas_no_ciclo.update(sorteadas)
        
        # Verifica se completou as 60 dezenas
        if len(dezenas_no_ciclo) == 60:
            qtd_concursos = concurso - inicio_ciclo + 1
            ciclos_fechados.append({
                'Ciclo': numero_ciclo,
                'Inicio': inicio_ciclo,
                'Fim': concurso,
                'Qtd_Sorteios': qtd_concursos
            })
            
            # Resetar para o próximo ciclo
            numero_ciclo += 1
            dezenas_no_ciclo = set()
            inicio_ciclo = concurso + 1
            
    # Ciclo atual (aberto)
    ciclo_atual_info = {
        'Ciclo_Atual': numero_ciclo,
        'Inicio': inicio_ciclo,
        'Dezenas_Sairam': dezenas_no_ciclo,
        'Dezenas_Faltam': todas_dezenas - dezenas_no_ciclo,
        'Ultimo_Concurso_Base': df['Concurso'].max()
    }
    
    return pd.DataFrame(ciclos_fechados), ciclo_atual_info

if uploaded_file is not None:
    df = carregar_dados(uploaded_file)
    
    if df is not None:
        # Processamento
        df_historico_ciclos, info_atual = calcular_ciclos(df)
        
        # --- Métricas do Topo (Status Atual) ---
        st.divider()

        # Agora teremos 5 colunas
        col1, col2, col3, col4, col5 = st.columns(5)

        conc_atual = info_atual["Ultimo_Concurso_Base"]
        inicio_ciclo = info_atual["Inicio"]
        concursos_no_ciclo_atual = conc_atual - inicio_ciclo + 1
        qtd_faltam = len(info_atual["Dezenas_Faltam"])

        # 1 - Ciclo atual
        col1.metric("Ciclo Atual", f"#{info_atual['Ciclo_Atual']}")

        # 2 - Sorteio em que o ciclo começou (só o número do concurso)
        col2.metric("Sorteio Início do Ciclo", f"{inicio_ciclo}")

        # 3 - Sorteio atual (último concurso considerado na base)
        col3.metric("Sorteio Atual", f"{conc_atual}")

        # 4 - Quantidade de sorteios já ocorridos neste ciclo
        col4.metric("Sorteios neste Ciclo", f"{concursos_no_ciclo_atual}")

        # 5 - Quantas dezenas ainda faltam sair no ciclo
        col5.metric("Faltam Sair", f"{qtd_faltam}", delta_color="inverse")

        st.divider()

        
        # --- Visualização do Volante (Grid) ---
        st.subheader(f"🧩 Status das Dezenas no Ciclo #{info_atual['Ciclo_Atual']}")
        
        # Preparar dados para o Grid
        grid_data = []
        for row in range(6): 
            for col in range(10): 
                numero = row * 10 + (col + 1)
                status = "Falta" if numero in info_atual['Dezenas_Faltam'] else "Saiu"
                cor_valor = 1 if status == "Falta" else 0 
                
                grid_data.append({
                    'Numero': numero, 'Linha': row, 'Coluna': col, 'Status': status, 'Valor_Cor': cor_valor
                })
        
        df_grid = pd.DataFrame(grid_data)
        
        fig = go.Figure()
        fig.add_trace(go.Heatmap(
            z=df_grid['Valor_Cor'],
            x=df_grid['Coluna'],
            y=df_grid['Linha'],
            text=df_grid['Numero'],
            texttemplate="%{text}",
            textfont={"size": 20},
            colorscale=[[0, '#e0e0e0'], [1, '#ff4b4b']], 
            showscale=False,
            xgap=3, ygap=3,
            hoverongaps=False,
            hovertemplate="Dezena: %{text}<br>Status: %{customdata}<extra></extra>",
            customdata=df_grid['Status']
        ))

        fig.update_layout(
            height=400,
            xaxis=dict(showticklabels=False, fixedrange=True),
            yaxis=dict(showticklabels=False, fixedrange=True, autorange="reversed"),
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        if qtd_faltam > 0:
            st.warning(f"🚨 **Dezenas que faltam sair:** {sorted(list(info_atual['Dezenas_Faltam']))}")

        # --- Histórico e Estatísticas (MODA E MEDIANA) ---
        st.markdown("---")
        st.subheader("📚 Histórico e Estatísticas de Duração")

        if not df_historico_ciclos.empty:
            # 1. Cálculos Estatísticos
            series_duracao = df_historico_ciclos['Qtd_Sorteios']
            
            media = series_duracao.mean()
            mediana = series_duracao.median()
            moda_series = series_duracao.mode()
            
            # Tratamento da Moda (pode haver mais de uma)
            if not moda_series.empty:
                lista_modas = sorted(moda_series.tolist())
                moda_str = ", ".join(map(str, lista_modas))
                legenda_moda = "Moda (Mais frequente)"
            else:
                # Fallback caso não haja moda (muito raro em inteiros repetidos, mas possível se todos forem unicos)
                # O usuário pediu "se não tiver, a mediana".
                moda_str = f"{mediana:.1f}"
                legenda_moda = "Moda (Usando Mediana)"

            # 2. Exibição das Métricas
            cm1, cm2, cm3, cm4 = st.columns(4)
            cm1.metric("Total de Ciclos Fechados", len(df_historico_ciclos))
            cm2.metric("Média de Sorteios", f"{media:.1f}")
            cm3.metric("Mediana (Centro)", f"{mediana:.1f}")
            cm4.metric(legenda_moda, moda_str)

            # 3. Gráfico
            col_h1, col_h2 = st.columns([2, 1])
            
            with col_h1:
                fig_hist = px.bar(
                    df_historico_ciclos, 
                    x='Ciclo', 
                    y='Qtd_Sorteios',
                    title='Duração de cada Ciclo Histórico',
                    labels={'Qtd_Sorteios': 'Duração (Jogos)'}
                )
                
                # Linhas de referência no gráfico
                #fig_hist.add_hline(y=media, line_dash="dash", line_color="blue", annotation_text=f"Média: {media:.1f}")
                #fig_hist.add_hline(y=mediana, line_dash="dot", line_color="green", annotation_text=f"Mediana: {mediana:.1f}")
                
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col_h2:
                st.write("**Tabela de Ciclos:**")
                st.dataframe(
                    df_historico_ciclos.sort_values(by='Ciclo', ascending=False), 
                    hide_index=True,
                    use_container_width=True
                )
        else:
            st.info("Ainda não há ciclos históricos fechados suficientes para calcular estatísticas.")

else:
    st.info("Aguardando upload do arquivo RESULTADOS_MEGASENA.csv")