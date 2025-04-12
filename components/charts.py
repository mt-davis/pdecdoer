import streamlit as st
import plotly.express as px

def display_impact_chart(data):
    categories = list(data.keys())
    values = list(data.values())

    fig = px.bar(
        x=categories,
        y=values,
        labels={'x': 'Category', 'y': 'Impact Level'},
        title="Simulated Impact by Category",
        text=values
    )
    fig.update_layout(
        yaxis_range=[0, 100],
        plot_bgcolor='white',
        title_font_size=20,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    fig.update_traces(marker_color='rgba(75, 106, 155, 0.8)', textposition='outside')

    st.plotly_chart(fig, use_container_width=True)
