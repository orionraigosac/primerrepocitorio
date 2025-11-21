import streamlit as st
import requests
import st_lottie
from streamlit_lottie 
import Image
from PIL 

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# =====================================================
# CONFIGURACIÓN DE PÁGINA
# =====================================================
st.set_page_config(
    page_title='DashBoard de Ventas',
    page_icon='📊',
    layout='wide'
)

st.title('📊 DashBoard de Análisis de Ventas')
st.markdown(
    "analizamos las ventas por **producto**, **región**, "
    "**vendedor** y **tiempo**, con métricas clave y gráficos dinámicos."
)
st.markdown('---')


# =====================================================
# 1. CREACIÓN DE DATOS SINTÉTICOS REALISTAS
# =====================================================
np.random.seed(42)
fechas = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
n_productos = ['Laptop', 'Mouse', 'Teclado', 'Monitor', 'Auriculares']
regiones = ['Norte', 'Sur', 'Este', 'Oeste', 'Centro']
vendedores = [f'Vendedor_{i}' for i in range(1, 21)]

data = []
for fecha in fechas:
    for _ in range(np.random.poisson(10)):    # 10 ventas promedio por día
        data.append({
            'fecha': fecha,
            'producto': np.random.choice(n_productos),
            'region': np.random.choice(regiones),
            'cantidad': np.random.randint(1, 6),
            'precio_unitario': np.random.uniform(50, 1500),
            'vendedor': np.random.choice(vendedores)
        })

df = pd.DataFrame(data)
df['venta_total'] = df['cantidad'] * df['precio_unitario']


# =====================================================
# 2. SIDEBAR – FILTROS AVANZADOS
# =====================================================
st.sidebar.header('🎛️ Filtros')

# Filtro de productos
productos_seleccionados = st.sidebar.multiselect(
    'Selecciona Productos:',
    options=df['producto'].unique(),
    default=df['producto'].unique()
)

# Filtro de regiones
regiones_seleccionadas = st.sidebar.multiselect(
    'Selecciona Regiones:',
    options=df['region'].unique(),
    default=df['region'].unique()
)

# Filtro de vendedores
vendedores_seleccionados = st.sidebar.multiselect(
    'Selecciona Vendedores:',
    options=df['vendedor'].unique(),
    default=df['vendedor'].unique()
)

# Filtro de rango de fechas
fecha_min = df['fecha'].min()
fecha_max = df['fecha'].max()

rango_fechas = st.sidebar.date_input(
    'Rango de Fechas:',
    value=[fecha_min, fecha_max],
    min_value=fecha_min,
    max_value=fecha_max
)

if len(rango_fechas) != 2:
    st.sidebar.warning("Selecciona un rango de dos fechas.")
    fecha_inicio = fecha_min
    fecha_fin = fecha_max
else:
    fecha_inicio, fecha_fin = rango_fechas

# =====================================================
# 3. APLICAR FILTROS AL DATAFRAME
# =====================================================
df_filtrado = df[
    (df['producto'].isin(productos_seleccionados)) &
    (df['region'].isin(regiones_seleccionadas)) &
    (df['vendedor'].isin(vendedores_seleccionados)) &
    (df['fecha'] >= pd.to_datetime(fecha_inicio)) &
    (df['fecha'] <= pd.to_datetime(fecha_fin))
]

if df_filtrado.empty:
    st.error("⚠ No hay datos para los filtros seleccionados. Ajusta los filtros.")
    st.stop()


# =====================================================
# 4. MÉTRICAS PRINCIPALES (KPIs)
# =====================================================
st.subheader("📌 Indicadores Clave")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric('Ventas Totales', f"${df_filtrado['venta_total'].sum():,.0f}")

with col2:
    st.metric('Promedio por Venta', f"${df_filtrado['venta_total'].mean():,.0f}")

with col3:
    st.metric('Número de Ventas', f"{len(df_filtrado):,}")

with col4:
    ventas_2024 = df_filtrado[df_filtrado['fecha'].dt.year == 2024]['venta_total'].sum()
    ventas_2023 = df_filtrado[df_filtrado['fecha'].dt.year == 2023]['venta_total'].sum()
    if ventas_2023 > 0:
        crecimiento = ((ventas_2024 / ventas_2023) - 1) * 100
    else:
        crecimiento = 0
    st.metric('Crecimiento 2024 vs 2023', f"{crecimiento:.1f}%")


st.markdown('---')


# =====================================================
# 5. TABS (Pestañas) PARA ORGANIZAR EL DASHBOARD
# =====================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 Visión General", "🛒 Productos", "🌎 Regiones", "📊 Distribución & Correlación", "📋 Detalle de Datos"]
)


# ===================== TAB 1: VISIÓN GENERAL =====================
with tab1:
    st.subheader("📈 Tendencia Mensual de Ventas")

    df_monthly = df_filtrado.groupby(df_filtrado['fecha'].dt.to_period('M'))['venta_total'].sum().reset_index()
    df_monthly['fecha'] = df_monthly['fecha'].astype(str)

    fig_monthly = px.line(
        df_monthly,
        x='fecha',
        y='venta_total',
        title='Tendencia de Ventas Mensuales (Filtrado)',
        labels={'venta_total': 'Ventas ($)', 'fecha': 'Mes'},
        markers=True
    )
    fig_monthly.update_traces(line=dict(width=4, color='royalblue'))
    fig_monthly.update_layout(xaxis_tickangle=-45)

    st.plotly_chart(fig_monthly, use_container_width=True)

    st.markdown('---')
    st.markdown(
        "✅ **Análisis sugerido:** La tendencia mensual permite identificar estacionalidad, "
        "meses fuertes y meses débiles. Esto es clave para planear inventarios, promociones y metas comerciales."
    )


# ===================== TAB 2: PRODUCTOS =====================
with tab2:
    col_p1, col_p2 = st.columns([2, 1])

    with col_p1:
        st.subheader("🛒 Ventas por Producto")

        df_productos = df_filtrado.groupby('producto')['venta_total'].sum().sort_values()
        fig_productos = px.bar(
            x=df_productos.values,
            y=df_productos.index,
            orientation='h',
            title='Ventas Totales por Producto (Filtrado)',
            labels={'x': 'Ventas Totales ($)', 'y': 'Producto'}
        )
        fig_productos.update_traces(marker_color='royalblue')
        st.plotly_chart(fig_productos, use_container_width=True)

    with col_p2:
        st.subheader("🎯 Top 5 Productos (por ingresos)")

        top5 = df_productos.sort_values(ascending=False).head(5)
        st.table(
            top5.reset_index().rename(columns={'index': 'Producto', 'venta_total': 'Ventas ($)'})
        )

    st.markdown('---')
    st.markdown(
        "✅ **Análisis sugerido:** Los productos con mayor contribución a las ventas pueden ser "
        "candidatos para estrategias de upselling, bundles, o foco en campañas de marketing."
    )


# ===================== TAB 3: REGIONES =====================
with tab3:
    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.subheader("🌎 Distribución de Ventas por Región")

        df_regiones = df_filtrado.groupby('region')['venta_total'].sum().reset_index()
        fig_regiones = px.pie(
            df_regiones,
            values='venta_total',
            names='region',
            title='Participación de Ventas por Región (Filtrado)'
        )
        fig_regiones.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_regiones, use_container_width=True)

    with col_r2:
        st.subheader("📊 Ventas por Región (Barras)")

        fig_regiones_bar = px.bar(
            df_regiones,
            x='region',
            y='venta_total',
            title='Ventas Totales por Región (Filtrado)',
            labels={'venta_total': 'Ventas ($)', 'region': 'Región'},
            text_auto='.2s'
        )
        st.plotly_chart(fig_regiones_bar, use_container_width=True)

    st.markdown('---')
    st.markdown(
        "✅ **Análisis sugerido:** Las regiones con mayor facturación pueden priorizarse para "
        "reforzar la presencia comercial, mejorar la logística y orientar campañas específicas."
    )


# ===================== TAB 4: DISTRIBUCIÓN & CORRELACIÓN =====================
with tab4:
    col_d1, col_d2 = st.columns(2)

    with col_d1:
        st.subheader("📊 Distribución de Ventas Individuales")
        fig_dist = px.histogram(
            df_filtrado,
            x='venta_total',
            nbins=50,
            title='Distribución de Ventas Individuales (Filtrado)',
            labels={'venta_total': 'Valor de la Venta ($)'}
        )
        fig_dist.update_layout(bargap=0.2)
        st.plotly_chart(fig_dist, use_container_width=True)

    with col_d2:
        st.subheader("📉 Correlación entre Variables")

        df_corr = df_filtrado[['cantidad', 'precio_unitario', 'venta_total']].corr()
        fig_heatmap = px.imshow(
            df_corr,
            text_auto=True,
            aspect='auto',
            title='Matriz de Correlación (Filtrado)',
            labels=dict(x='Variables', y='Variables', color='Correlación')
        )
        fig_heatmap.update_layout(coloraxis_colorbar_title_text='Correlación')
        st.plotly_chart(fig_heatmap, use_container_width=True)

    st.markdown('---')
    st.markdown(
        "✅ **Análisis sugerido:** La correlación entre cantidad, precio y venta total permite validar "
        "la lógica del modelo de negocio y detectar patrones, como sensibilidad al precio o tickets promedio."
    )


# ===================== TAB 5: DETALLE DE DATOS =====================
with tab5:
    st.subheader("📋 Detalle de Datos Filtrados")

    st.dataframe(df_filtrado, use_container_width=True, height=400)

    # Botón de descarga
    @st.cache_data
    def convertir_csv(df_):
        return df_.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="⬇ Descargar datos filtrados (CSV)",
        data=convertir_csv(df_filtrado),
        file_name="ventas_filtradas.csv",
        mime="text/csv"
    )

    st.markdown(
        "✅ **Tip didáctico:** Puedes descargar el archivo para que practiquen filtros, "

        "segmentación y exportación para análisis en Excel o Power BI.")

