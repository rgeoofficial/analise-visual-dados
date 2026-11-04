from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import functions

st.set_page_config(
    page_title="Projeto de Exploração e Análise Visual de Dados",
    page_icon=":material/bar_chart:",
    layout="wide"
)

with st.bottom:
    st.html(
        "<p style='text-align: center; font-size: 0.8rem; opacity: 0.7; margin: 0;'>"
        "© 2026 Desenvolvido por Rhonner Ramírez no Departamento de Geotecnia - "
        "EESC/USP · All rights reserved</p>"
    )

st.html(
    "<h1 style='text-align: center; font-size: 1.2rem;'>"
    "PROJETO DE EXPLORAÇÃO E ANÁLISE VISUAL DE DADOS 📊</h1>"
)
st.html(
    "<h1 style='text-align: center; font-size: 1.0rem;'>"
    "Análise de Dados Aplicada à Otimização de Projetos de Fundações para "
    "Redução das Emissões de CO₂ e da Demanda de Energia Primária</h1>"
)

geojson_path = Path("brazil-states.geojson")
url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/main/public/data/brazil-states.geojson"
palettes = {
    "Azul (padrão)":              ["#e8eef7", "#bdd7ee", "#6baed6", "#2171b5", "#08306b"],
    "Viridis (daltonismo geral)": ["#fde725", "#5ec962", "#21918c", "#3b528b", "#440154"],
    "Cividis (vermelho-verde)":   ["#ffea46", "#bcaf6f", "#7d7c78", "#414d6b", "#00204d"],
    "Laranja-marrom":             ["#ffffd4", "#fed98e", "#fe9929", "#d95f0e", "#993404"],
    "Tons de cinza":              ["#f0f0f0", "#bdbdbd", "#969696", "#636363", "#252525"],
}

def is_dark(hex_color):
    """Perceived luminance, used to pick white or black label text."""
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return 0.299 * r + 0.587 * g + 0.114 * b < 140

@st.cache_data
def load_df(file):
    return pd.read_excel(file)
df = load_df("df.xlsx")
df = df.astype({
    "UF": "category",
    "Tf": "category"
})
data = df["UF"].value_counts().to_dict()

@st.cache_data
def build_map(data, palette_name):
    """Build the whole map figure once; toggling widgets won't rebuild it."""
    geojson = funcoes.load_geojson(geojson_path, url)

    rows = []
    for feat in geojson["features"]:
        lon, lat = funcoes.state_centroid(feat["geometry"])
        rows.append({"state": feat["properties"]["sigla"], "lon": lon, "lat": lat})
    dfmap = pd.DataFrame(rows)
    dfmap["value"] = dfmap["state"].map(data).fillna(0).astype(int)

    bins = [-1, 0, 1, 3, 6, float("inf")]
    labels = ["0", "1", "2–3", "4–6", "7 ou mais"]
    colors = palettes[palette_name]
    color_map = dict(zip(labels, colors))

    dfmap["classe"] = pd.cut(dfmap["value"], bins=bins, labels=labels).astype(str)

    fig = px.choropleth(
        dfmap,
        geojson=geojson,
        locations="state",
        featureidkey="properties.sigla",
        color="classe",
        color_discrete_map=color_map,
        category_orders={"classe": labels},
        hover_name="state",
        hover_data={"state": False, "classe": False, "value": True},
        labels={"classe": "Número de projetos", "value": "Número de projetos"},
    )
    dark = {lab for lab, col in color_map.items() if is_dark(col)}
    fig.add_trace(
        go.Scattergeo(
            lon=dfmap["lon"],
            lat=dfmap["lat"],
            text=dfmap["state"],
            mode="text",
            textfont={
                "size": 11,
                "color": ["white" if c in dark else "black" for c in dfmap["classe"]],
            },
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
    fig.update_layout(
        margin={"l": 0, "r": 0, "t": 40, "b": 10},
        height=475,
        legend={
            "title": {"text": "Número de projetos"},
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": 1.075,
            "yanchor": "top",
        },
    )
    return fig

with st.expander("Dataset", expanded=False):
    st.dataframe(df)
    row_count, column_count = df.shape
    categoric_var = len(df.select_dtypes("category").columns)
    numeric_var = len(df.columns.difference(df.select_dtypes("category").columns))
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Observações", f"{row_count:,}", border=True)
    col2.metric("Variáveis", f"{column_count:,}", border=True)
    col3.metric("Variáveis categóricas", f"{categoric_var:,}", border=True)
    col4.metric("Variáveis numéricas", f"{numeric_var:,}", border=True)

ufs_dict = df["UF"].value_counts().to_dict()
fig2 = px.bar(
    x = ufs_dict.keys(),
    y = ufs_dict.values(),
    labels = {"x": "Unidades Federativas", "y": "Frequência"}
)

variable_names = {
    "UF": "Unidade Federativa",
    "Np": "Número de pavimentos total",
    "Ned": "Número de edificações",
    "At": "Área do pavimento térreo",
    "Tf": "Tipo de fundação",
    "Ar": "Área do radier",
    "er": "Espessura do radier",
    "Vr": "Volume do radier",
    "fckr": "Resistência à compressão característica do radier",
    "Mat60r": "Massa de aço de telas CA-60 do radier",
    "Mab50r": "Massa de aço de barras CA-50 do radier",
    "Mab60r": "Massa de aço de barras CA-60 do radier",
    "Mac190r": "Massa de aço de cordoalha CP190 RB 12,7 (kg)",
    "Ve": "Volume das estacas",
    "fcke": "Resistência à compressão característica das estacas",
    "Mab50e": "Massa de aço de barras CA-50 da estaca",
    "Vbc": "Volume dos blocos de coroamento",
    "fckbc": "$f_{ck}$ dos blocos de coroamento",
    "Mab50bc": "Massa de aço de barras CA-50 do bloco de coroamento",
    "Vvi": "Volume de vigas",
    "fckvi": "$f_{ck}$ das vigas",
    "Vm": "Volume da mesoestrutura",
    "fckm": "$f_{ck}$ da mesoestrutura",
    "Ma50fm": "Massa de aço de barras CA-50 da fundação mais mesoestrutura",
    "Ma60fm": "Massa de aço de barras CA-60 da fundação mais mesoestrutura"
}

tab1, tab2 = st.tabs(["Visão geral dos dados", "Análise visual"])

with tab1:
    variavel = st.pills("Variável", tuple(df.columns), default="UF", help="""
        - UF: Unidade Federativa
        - Np: Número de pavimentos total
        - Ned: Número de edificações
        - At: Área do pavimento térreo
        - Tf: Tipo de fundação
        - Ar: Área do radier
        - er: Espessura do radier
        - Vr: Volume do radier
        - fckr: Resistência à compressão característica do radier
        - Mat60r: Massa de aço de telas CA-60 do radier
        - Mab50r: Massa de aço de barras CA-50 do radier
        - Mab60r: Massa de aço de barras CA-60 do radier
        - Mac190r: Massa de aço de cordoalha CP190 RB 12,7 (kg)
        - Ve: Volume das estacas
        - fcke: Resistência à compressão característica das estacas
        - Mab50e: Massa de aço de barras CA-50 da estaca
        - Vbc: Volume dos blocos de coroamento
        - fckbc: $f_{ck}$ dos blocos de coroamento
        - Mab50bc: Massa de aço de barras CA-50 do bloco de coroamento
        - Vvi: Volume de vigas
        - fckvi: $f_{ck}$ das vigas
        - Vm: Volume da mesoestrutura
        - fckm: $f_{ck}$ da mesoestrutura
        - Ma50fm: Massa de aço de barras CA-50 da fundação mais mesoestrutura
        - Ma60fm: Massa de aço de barras CA-60 da fundação mais mesoestrutura
        """,
        )

    if variavel == "UF":
        palette_name = st.radio(
            "Paleta de cores",
            list(palettes),
            horizontal=True,
            help="Viridis e Cividis foram desenhadas para serem legíveis por pessoas com daltonismo.",
        )
        col1, col2 = st.columns(2)
        with col1:
            with st.spinner("Gerando mapa..."):
                fig = build_map(data, palette_name)
                st.plotly_chart(fig, width="stretch", height=475, key="1")
        with col2:
            st.plotly_chart(fig2, width="stretch", height=475, key="2")
    else:
        nbins = st.slider(label="Bins", min_value=5, max_value=10, value=10, step=1)
        fig = px.histogram(df, x=variavel, nbins=nbins, barmode="overlay", opacity=0.7)
        fig.update_layout(bargap=0.05, xaxis_title=variable_names[variavel], yaxis_title="Frequência", height=400)
        st.plotly_chart(fig, width="stretch")

with tab2:
    tab1, tab2, tab3 = st.tabs(["Localização dos projetos", "Tipo de fundação e número de edificações", "Tipo de fundação e número de pavimentos"])
    with tab1:
        palette_name = st.radio(
            "Paleta de cores",
            list(palettes),
            horizontal=True,
            help="Viridis e Cividis foram desenhadas para serem legíveis por pessoas com daltonismo.", key="5"
        )
        col1, col2 = st.columns(2)
        with col1:
            with st.spinner("Gerando mapa..."):
                fig = build_map(data, palette_name)
                st.plotly_chart(fig, width="stretch", height=475, key="3")
        with col2:
            st.plotly_chart(fig2, width="stretch", height=475, key="4")
    with tab2:
        Tf_Ned = df.groupby("Tf", observed=True)["Ned"].sum().sort_values(ascending=False).to_dict()
        fig3 = px.bar(
            x = Tf_Ned.keys(),
            y = Tf_Ned.values(),
            labels = {"x": "Tipo de fundação", "y": "Número de edificações"}
        )
        st.plotly_chart(fig3, width="stretch", height=475)
    with tab3:
        fig = px.violin(
            df, x="Tf", y="Np",
            box=True,
            points="all",          # draw every observation
            labels={"Tf": "Tipo de fundação", "Np": "Número de pavimentos"},
        )
        grid_color = fig.layout.template.layout.yaxis.gridcolor
        fig.update_traces(
            spanmode="hard",
            jitter=0.4,            # horizontal spread of the points (0 to 1)
            pointpos=0,            # 0 = centered on the violin, -1.5 = left side, 1.5 = right side
            marker=dict(size=4, opacity=1),
        )
        fig.update_yaxes(
            rangemode="nonnegative",
            showgrid=True, gridcolor=grid_color, gridwidth=1,
            minor=dict(dtick=1, showgrid=True, gridcolor=grid_color, gridwidth=1),
        )
        st.plotly_chart(fig, width="stretch", height=475)
