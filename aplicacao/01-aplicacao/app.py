from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR.parent.parent / "notebooks" / "volve_ml_ready.db"
TABLE_NAME = "volve_ml_ready"

PALETTE = {
    "ink": "#1B2A34",
    "sand": "#F3EBDC",
    "stone": "#D9D0C1",
    "rust": "#C56A2D",
    "teal": "#1F6F78",
    "gold": "#B58B2A",
    "brick": "#8D3B2C",
}

NUMERIC_COLUMNS = [
    "ON_STREAM_HRS",
    "AVG_DOWNHOLE_PRESSURE",
    "AVG_DOWNHOLE_TEMPERATURE",
    "AVG_DP_TUBING",
    "AVG_CHOKE_SIZE_P",
    "AVG_WHP_P",
    "AVG_WHT_P",
    "BORE_OIL_VOL",
    "BORE_WAT_VOL",
    "oil_roll_30",
    "oil_roll_mean_7",
    "oil_roll_mean_14",
    "oil_delta_7d",
    "oil_zscore_30",
    "oil_trend_strength",
    "oil_volatility_index",
]

TABLE_COLUMNS = [
    "DATEPRD",
    "WELL_TYPE",
    "BORE_OIL_VOL",
    "BORE_WAT_VOL",
    "ON_STREAM_HRS",
    "AVG_DOWNHOLE_PRESSURE",
    "AVG_DOWNHOLE_TEMPERATURE",
    "AVG_DP_TUBING",
    "AVG_CHOKE_SIZE_P",
    "AVG_WHP_P",
    "oil_roll_mean_7",
    "oil_roll_30",
    "oil_delta_7d",
    "oil_zscore_30",
    "oil_trend_strength",
    "oil_volatility_index",
]


st.set_page_config(
    page_title="Dashboard Volve",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background:
                radial-gradient(circle at top right, rgba(181, 139, 42, 0.20), transparent 24%),
                linear-gradient(180deg, {PALETTE["sand"]} 0%, #EEE7DA 100%);
        }}
        .block-container {{
            padding-top: 1.25rem;
            padding-bottom: 2rem;
        }}
        h1, h2, h3 {{
            color: {PALETTE["ink"]};
        }}
        .hero {{
            background: linear-gradient(135deg, rgba(27, 42, 52, 0.98), rgba(31, 111, 120, 0.90));
            border-radius: 20px;
            padding: 1.4rem 1.6rem;
            margin-bottom: 1rem;
            box-shadow: 0 16px 40px rgba(27, 42, 52, 0.18);
            color: #F8F4EC;
        }}
        .hero p {{
            margin: 0.4rem 0 0 0;
            color: rgba(248, 244, 236, 0.86);
        }}
        .kpi-card {{
            background: rgba(255, 255, 255, 0.72);
            border: 1px solid rgba(27, 42, 52, 0.08);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            min-height: 118px;
            box-shadow: 0 10px 24px rgba(27, 42, 52, 0.08);
        }}
        .kpi-label {{
            color: #695B4E;
            font-size: 0.88rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}
        .kpi-value {{
            color: {PALETTE["ink"]};
            font-size: 1.95rem;
            font-weight: 700;
            line-height: 1.15;
            margin-top: 0.35rem;
        }}
        .kpi-detail {{
            color: #584B40;
            margin-top: 0.3rem;
            font-size: 0.9rem;
        }}
        div[data-testid="stMetric"] {{
            background: rgba(255, 255, 255, 0.70);
            border: 1px solid rgba(27, 42, 52, 0.08);
            border-radius: 16px;
            padding: 0.7rem 0.9rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_number(value: float, decimals: int = 1, suffix: str = "") -> str:
    if pd.isna(value):
        return "-"
    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".") + suffix


def apply_plot_theme(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.58)",
        margin=dict(l=20, r=20, t=48, b=20),
        font=dict(color=PALETTE["ink"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(gridcolor="rgba(27, 42, 52, 0.08)")
    fig.update_yaxes(gridcolor="rgba(27, 42, 52, 0.08)")
    return fig


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as connection:
        df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", connection)

    df["DATEPRD"] = pd.to_datetime(df["DATEPRD"], errors="coerce")

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df.sort_values("DATEPRD").reset_index(drop=True)


def render_header(df: pd.DataFrame) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <h1>Cockpit Operacional Volve</h1>
            <p>
                Monitoramento de producao, estabilidade operacional e anomalias derivadas de ML
                para o periodo de {df["DATEPRD"].min().date().isoformat()} ate {df["DATEPRD"].max().date().isoformat()}.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_sidebar(df: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    st.sidebar.header("Filtros")

    min_date = df["DATEPRD"].min().date()
    max_date = df["DATEPRD"].max().date()
    selected_dates = st.sidebar.date_input(
        "Periodo",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if len(selected_dates) != 2:
        start_date, end_date = min_date, max_date
    else:
        start_date, end_date = selected_dates

    well_types = sorted(df["WELL_TYPE"].dropna().unique().tolist())
    selected_well_types = st.sidebar.multiselect(
        "Tipo de poco",
        options=well_types,
        default=well_types,
    )

    st.sidebar.subheader("Producao")
    oil_range = st.sidebar.slider(
        "Oleo",
        min_value=float(df["BORE_OIL_VOL"].min()),
        max_value=float(df["BORE_OIL_VOL"].max()),
        value=(float(df["BORE_OIL_VOL"].min()), float(df["BORE_OIL_VOL"].max())),
        step=1.0,
    )
    water_range = st.sidebar.slider(
        "Agua",
        min_value=float(df["BORE_WAT_VOL"].min()),
        max_value=float(df["BORE_WAT_VOL"].max()),
        value=(float(df["BORE_WAT_VOL"].min()), float(df["BORE_WAT_VOL"].max())),
        step=1.0,
    )

    st.sidebar.subheader("Operacao")
    on_stream_range = st.sidebar.slider(
        "Horas em operacao",
        min_value=float(df["ON_STREAM_HRS"].min()),
        max_value=float(df["ON_STREAM_HRS"].max()),
        value=(float(df["ON_STREAM_HRS"].min()), float(df["ON_STREAM_HRS"].max())),
        step=0.25,
    )
    pressure_range = st.sidebar.slider(
        "Pressao downhole",
        min_value=float(df["AVG_DOWNHOLE_PRESSURE"].min()),
        max_value=float(df["AVG_DOWNHOLE_PRESSURE"].max()),
        value=(float(df["AVG_DOWNHOLE_PRESSURE"].min()), float(df["AVG_DOWNHOLE_PRESSURE"].max())),
        step=0.1,
    )
    temperature_range = st.sidebar.slider(
        "Temperatura downhole",
        min_value=float(df["AVG_DOWNHOLE_TEMPERATURE"].min()),
        max_value=float(df["AVG_DOWNHOLE_TEMPERATURE"].max()),
        value=(
            float(df["AVG_DOWNHOLE_TEMPERATURE"].min()),
            float(df["AVG_DOWNHOLE_TEMPERATURE"].max()),
        ),
        step=0.01,
    )
    tubing_range = st.sidebar.slider(
        "DP tubing",
        min_value=float(df["AVG_DP_TUBING"].min()),
        max_value=float(df["AVG_DP_TUBING"].max()),
        value=(float(df["AVG_DP_TUBING"].min()), float(df["AVG_DP_TUBING"].max())),
        step=0.1,
    )
    choke_range = st.sidebar.slider(
        "Choke size",
        min_value=float(df["AVG_CHOKE_SIZE_P"].min()),
        max_value=float(df["AVG_CHOKE_SIZE_P"].max()),
        value=(float(df["AVG_CHOKE_SIZE_P"].min()), float(df["AVG_CHOKE_SIZE_P"].max())),
        step=0.1,
    )
    whp_range = st.sidebar.slider(
        "Wellhead pressure",
        min_value=float(df["AVG_WHP_P"].min()),
        max_value=float(df["AVG_WHP_P"].max()),
        value=(float(df["AVG_WHP_P"].min()), float(df["AVG_WHP_P"].max())),
        step=0.1,
    )

    st.sidebar.subheader("ML e alertas")
    anomaly_threshold = st.sidebar.slider(
        "Limiar de anomalia | z-score",
        min_value=1.0,
        max_value=4.0,
        value=2.0,
        step=0.25,
    )
    trend_range = st.sidebar.slider(
        "Forca de tendencia",
        min_value=float(df["oil_trend_strength"].min()),
        max_value=float(df["oil_trend_strength"].max()),
        value=(float(df["oil_trend_strength"].min()), float(df["oil_trend_strength"].max())),
        step=1.0,
    )
    volatility_range = st.sidebar.slider(
        "Volatilidade",
        min_value=float(df["oil_volatility_index"].min()),
        max_value=float(df["oil_volatility_index"].max()),
        value=(float(df["oil_volatility_index"].min()), float(df["oil_volatility_index"].max())),
        step=0.01,
    )

    filtered = df.loc[
        (df["DATEPRD"].dt.date >= start_date)
        & (df["DATEPRD"].dt.date <= end_date)
        & (df["WELL_TYPE"].isin(selected_well_types))
        & (df["BORE_OIL_VOL"].between(*oil_range))
        & (df["BORE_WAT_VOL"].between(*water_range))
        & (df["ON_STREAM_HRS"].between(*on_stream_range))
        & (df["AVG_DOWNHOLE_PRESSURE"].between(*pressure_range))
        & (df["AVG_DOWNHOLE_TEMPERATURE"].between(*temperature_range))
        & (df["AVG_DP_TUBING"].between(*tubing_range))
        & (df["AVG_CHOKE_SIZE_P"].between(*choke_range))
        & (df["AVG_WHP_P"].between(*whp_range))
        & (df["oil_trend_strength"].between(*trend_range))
        & (df["oil_volatility_index"].between(*volatility_range))
    ].copy()

    st.sidebar.caption(f"{len(filtered)} de {len(df)} registros visiveis")
    return filtered, anomaly_threshold


def render_kpis(df: pd.DataFrame, anomaly_threshold: float) -> None:
    oil_total = df["BORE_OIL_VOL"].sum()
    oil_mean = df["BORE_OIL_VOL"].mean()
    water_total = df["BORE_WAT_VOL"].sum()
    water_mean = df["BORE_WAT_VOL"].mean()
    water_cut = 0.0
    total_liquids = oil_total + water_total
    if total_liquids > 0:
        water_cut = (water_total / total_liquids) * 100

    stream_mean = df["ON_STREAM_HRS"].mean()
    pressure_mean = df["AVG_DOWNHOLE_PRESSURE"].mean()
    oil_delta_7d = df["oil_delta_7d"].iloc[-1]
    anomaly_count = int((df["oil_zscore_30"].abs() >= anomaly_threshold).sum())

    cards = [
        ("Oleo total", format_number(oil_total, 1), f"Media diaria: {format_number(oil_mean, 1)}"),
        ("Agua total", format_number(water_total, 1), f"Media diaria: {format_number(water_mean, 1)}"),
        ("Water cut", format_number(water_cut, 1, "%"), "Participacao da agua no volume total"),
        ("Horas medias", format_number(stream_mean, 2, " h"), "Disponibilidade media do periodo"),
        ("Pressao media", format_number(pressure_mean, 2), "Pressao downhole media"),
        ("Delta oleo 7d", format_number(oil_delta_7d, 2), "Ultimo valor filtrado"),
        ("Anomalias", str(anomaly_count), f"Limiar atual: |z| >= {anomaly_threshold}"),
    ]

    for column, (label, value, detail) in zip(st.columns(len(cards)), cards, strict=True):
        column.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-detail">{detail}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_summary_tab(df: pd.DataFrame) -> None:
    time_series = go.Figure()
    time_series.add_trace(
        go.Scatter(
            x=df["DATEPRD"],
            y=df["BORE_OIL_VOL"],
            mode="lines",
            name="Oleo",
            line=dict(color=PALETTE["rust"], width=2.5),
        )
    )
    time_series.add_trace(
        go.Scatter(
            x=df["DATEPRD"],
            y=df["BORE_WAT_VOL"],
            mode="lines",
            name="Agua",
            line=dict(color=PALETTE["teal"], width=2.2),
        )
    )
    time_series.add_trace(
        go.Scatter(
            x=df["DATEPRD"],
            y=df["oil_roll_mean_7"],
            mode="lines",
            name="Media movel 7d",
            line=dict(color=PALETTE["gold"], width=2, dash="dot"),
        )
    )
    time_series.add_trace(
        go.Scatter(
            x=df["DATEPRD"],
            y=df["oil_roll_30"],
            mode="lines",
            name="Media movel 30d",
            line=dict(color=PALETTE["brick"], width=2, dash="dash"),
        )
    )
    time_series.update_layout(title="Producao e medias moveis")
    st.plotly_chart(apply_plot_theme(time_series), use_container_width=True)

    detail_left, detail_right = st.columns([1.15, 1])

    with detail_left:
        water_cut = df["BORE_WAT_VOL"] / (df["BORE_WAT_VOL"] + df["BORE_OIL_VOL"]).replace(0, pd.NA)
        water_cut_fig = px.area(
            x=df["DATEPRD"],
            y=water_cut.fillna(0) * 100,
            labels={"x": "Data", "y": "Water cut (%)"},
            title="Evolucao do water cut",
            color_discrete_sequence=[PALETTE["teal"]],
        )
        st.plotly_chart(apply_plot_theme(water_cut_fig), use_container_width=True)

    with detail_right:
        best_day = df.loc[df["BORE_OIL_VOL"].idxmax()]
        worst_day = df.loc[df["BORE_OIL_VOL"].idxmin()]
        summary = pd.DataFrame(
            {
                "Indicador": [
                    "Registros visiveis",
                    "Data inicial",
                    "Data final",
                    "Melhor dia de oleo",
                    "Pior dia de oleo",
                    "Media de tendencia",
                    "Media de volatilidade",
                ],
                "Valor": [
                    len(df),
                    df["DATEPRD"].min().date().isoformat(),
                    df["DATEPRD"].max().date().isoformat(),
                    f"{best_day['DATEPRD'].date().isoformat()} | {format_number(best_day['BORE_OIL_VOL'], 2)}",
                    f"{worst_day['DATEPRD'].date().isoformat()} | {format_number(worst_day['BORE_OIL_VOL'], 2)}",
                    format_number(df["oil_trend_strength"].mean(), 2),
                    format_number(df["oil_volatility_index"].mean(), 3),
                ],
            }
        )
        st.subheader("Leitura rapida")
        st.dataframe(summary, use_container_width=True, hide_index=True)


def render_diagnostics_tab(df: pd.DataFrame) -> None:
    chart_1, chart_2 = st.columns(2)
    chart_3, chart_4 = st.columns(2)

    with chart_1:
        fig = px.scatter(
            df,
            x="AVG_DOWNHOLE_PRESSURE",
            y="BORE_OIL_VOL",
            color="ON_STREAM_HRS",
            size="BORE_WAT_VOL",
            title="Pressao downhole vs oleo",
            color_continuous_scale=["#D9D0C1", PALETTE["gold"], PALETTE["rust"]],
            hover_data=["DATEPRD", "WELL_TYPE"],
        )
        st.plotly_chart(apply_plot_theme(fig), use_container_width=True)

    with chart_2:
        fig = px.scatter(
            df,
            x="AVG_DOWNHOLE_TEMPERATURE",
            y="BORE_OIL_VOL",
            color="AVG_WHP_P",
            size="ON_STREAM_HRS",
            title="Temperatura downhole vs oleo",
            color_continuous_scale=["#D9D0C1", PALETTE["teal"], PALETTE["ink"]],
            hover_data=["DATEPRD", "BORE_WAT_VOL"],
        )
        st.plotly_chart(apply_plot_theme(fig), use_container_width=True)

    with chart_3:
        fig = px.scatter(
            df,
            x="AVG_CHOKE_SIZE_P",
            y="BORE_OIL_VOL",
            color="AVG_DOWNHOLE_PRESSURE",
            size="BORE_WAT_VOL",
            title="Choke size vs oleo",
            color_continuous_scale=["#EEE7DA", PALETTE["gold"], PALETTE["brick"]],
            hover_data=["DATEPRD", "ON_STREAM_HRS"],
        )
        st.plotly_chart(apply_plot_theme(fig), use_container_width=True)

    with chart_4:
        fig = px.scatter(
            df,
            x="AVG_DP_TUBING",
            y="BORE_OIL_VOL",
            color="oil_trend_strength",
            size="ON_STREAM_HRS",
            title="DP tubing vs oleo",
            color_continuous_scale=["#27404D", "#F3EBDC", "#C56A2D"],
            hover_data=["DATEPRD", "AVG_CHOKE_SIZE_P"],
        )
        st.plotly_chart(apply_plot_theme(fig), use_container_width=True)

    corr_columns = [
        "BORE_OIL_VOL",
        "BORE_WAT_VOL",
        "ON_STREAM_HRS",
        "AVG_DOWNHOLE_PRESSURE",
        "AVG_DOWNHOLE_TEMPERATURE",
        "AVG_DP_TUBING",
        "AVG_CHOKE_SIZE_P",
        "AVG_WHP_P",
        "oil_trend_strength",
        "oil_volatility_index",
    ]
    corr = df[corr_columns].corr(numeric_only=True).round(2)
    heatmap = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale=["#27404D", "#F3EBDC", "#C56A2D"],
        title="Heatmap de correlacao",
    )
    st.plotly_chart(apply_plot_theme(heatmap), use_container_width=True)


def render_alerts_tab(df: pd.DataFrame, anomaly_threshold: float) -> None:
    trend_fig = go.Figure()
    trend_fig.add_trace(
        go.Scatter(
            x=df["DATEPRD"],
            y=df["oil_trend_strength"],
            mode="lines",
            name="Trend strength",
            line=dict(color=PALETTE["teal"], width=2.3),
        )
    )
    trend_fig.add_trace(
        go.Bar(
            x=df["DATEPRD"],
            y=df["oil_delta_7d"],
            name="Delta oleo 7d",
            marker_color="rgba(197, 106, 45, 0.45)",
            yaxis="y2",
        )
    )
    trend_fig.update_layout(
        title="Tendencia e deslocamento semanal",
        yaxis=dict(title="Trend strength"),
        yaxis2=dict(title="Delta 7d", overlaying="y", side="right", showgrid=False),
    )
    st.plotly_chart(apply_plot_theme(trend_fig), use_container_width=True)

    left, right = st.columns([1.15, 1])

    with left:
        zscore_fig = px.line(
            df,
            x="DATEPRD",
            y="oil_zscore_30",
            title="Z-score do oleo (janela de 30 dias)",
            color_discrete_sequence=[PALETTE["brick"]],
        )
        zscore_fig.add_hline(y=anomaly_threshold, line_dash="dot", line_color=PALETTE["gold"])
        zscore_fig.add_hline(y=-anomaly_threshold, line_dash="dot", line_color=PALETTE["gold"])
        st.plotly_chart(apply_plot_theme(zscore_fig), use_container_width=True)

    with right:
        critical_days = df.loc[df["oil_zscore_30"].abs() >= anomaly_threshold, [
            "DATEPRD",
            "BORE_OIL_VOL",
            "BORE_WAT_VOL",
            "oil_zscore_30",
            "oil_delta_7d",
            "oil_trend_strength",
        ]].sort_values("oil_zscore_30", key=lambda series: series.abs(), ascending=False)

        st.subheader("Top dias criticos")
        st.dataframe(
            critical_days,
            use_container_width=True,
            hide_index=True,
            column_config={
                "DATEPRD": st.column_config.DateColumn("Data"),
                "BORE_OIL_VOL": st.column_config.NumberColumn("Oleo", format="%.2f"),
                "BORE_WAT_VOL": st.column_config.NumberColumn("Agua", format="%.2f"),
                "oil_zscore_30": st.column_config.NumberColumn("Z-score", format="%.2f"),
                "oil_delta_7d": st.column_config.NumberColumn("Delta 7d", format="%.2f"),
                "oil_trend_strength": st.column_config.NumberColumn("Trend", format="%.2f"),
            },
        )


def render_data_tab(df: pd.DataFrame) -> None:
    st.dataframe(
        df[TABLE_COLUMNS].sort_values("DATEPRD", ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "DATEPRD": st.column_config.DateColumn("Data"),
            "WELL_TYPE": st.column_config.TextColumn("Tipo"),
            "BORE_OIL_VOL": st.column_config.NumberColumn("Oleo", format="%.2f"),
            "BORE_WAT_VOL": st.column_config.NumberColumn("Agua", format="%.2f"),
            "ON_STREAM_HRS": st.column_config.NumberColumn("Horas", format="%.2f"),
            "AVG_DOWNHOLE_PRESSURE": st.column_config.NumberColumn("Pressao", format="%.2f"),
            "AVG_DOWNHOLE_TEMPERATURE": st.column_config.NumberColumn("Temperatura", format="%.2f"),
            "AVG_DP_TUBING": st.column_config.NumberColumn("DP tubing", format="%.2f"),
            "AVG_CHOKE_SIZE_P": st.column_config.NumberColumn("Choke", format="%.2f"),
            "AVG_WHP_P": st.column_config.NumberColumn("WHP", format="%.2f"),
            "oil_roll_mean_7": st.column_config.NumberColumn("Media 7d", format="%.2f"),
            "oil_roll_30": st.column_config.NumberColumn("Media 30d", format="%.2f"),
            "oil_delta_7d": st.column_config.NumberColumn("Delta 7d", format="%.2f"),
            "oil_zscore_30": st.column_config.NumberColumn("Z-score", format="%.2f"),
            "oil_trend_strength": st.column_config.NumberColumn("Trend", format="%.2f"),
            "oil_volatility_index": st.column_config.NumberColumn("Volatilidade", format="%.3f"),
        },
    )


def main() -> None:
    inject_styles()

    if not DB_PATH.exists():
        st.error(f"Banco nao encontrado em {DB_PATH}")
        st.stop()

    df = load_data()
    render_header(df)
    filtered_df, anomaly_threshold = build_sidebar(df)

    if filtered_df.empty:
        st.warning("Os filtros removeram todos os registros. Ajuste os limites na lateral.")
        st.stop()

    render_kpis(filtered_df, anomaly_threshold)

    summary_tab, diagnostics_tab, alerts_tab, data_tab = st.tabs(
        ["Resumo executivo", "Diagnostico operacional", "Tendencias e alertas", "Base filtrada"]
    )

    with summary_tab:
        render_summary_tab(filtered_df)
    with diagnostics_tab:
        render_diagnostics_tab(filtered_df)
    with alerts_tab:
        render_alerts_tab(filtered_df, anomaly_threshold)
    with data_tab:
        render_data_tab(filtered_df)


if __name__ == "__main__":
    main()
