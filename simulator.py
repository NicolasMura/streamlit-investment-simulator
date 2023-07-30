"""
# Investment simulator
"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import math

st. set_page_config(layout="wide")

st.write(
    '''
        <a href="https://github.com/NicolasMura/streamlit-investment-simulator" style="display: inline-flex; align-items: center; text-decoration:none; color: inherit">
            <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="22px" />
            <span style="margin-left: 10px; vertical-align: text-bottom;">Code source</span>
        </a>
    ''',
    unsafe_allow_html=True)

st.markdown('## Étape 1 - Intérêts composés')

st.markdown('Si toi aussi tu veux devenir rentier, joue avec moi.')

# @st.cache_data()
def get_chart(data):
    hover = alt.selection_single(
        fields=["date"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data, height=500, title="Evolution of stock prices")
        .mark_line()
        .encode(
            x=alt.X("date", title="Date"),
            y=alt.Y("price", title="Price"),
            color="symbol",
        )
    )

    # Draw points on the line, and highlight based on selection
    points = lines.transform_filter(hover).mark_circle(size=65)

    return (lines + points).interactive()

def compute_capital_with_interests(initial_capital, monthly_amount, investment_period_in_years, average_monthly_performance):
    initial_capital_with_interests = initial_capital * math.pow(1 + average_monthly_performance, 12 * investment_period_in_years)
    composed_interests = (monthly_amount *  (math.pow(1 + average_monthly_performance, 12 * investment_period_in_years) - 1)) / (average_monthly_performance)

    return initial_capital_with_interests + composed_interests

def compute_capital(initial_capital, monthly_amount, investment_period_in_years):
   return initial_capital + monthly_amount * investment_period_in_years * 12;

total = 0

col1, col2 = st.columns([2, 3])
with col1:
    with st.form('form'):
        initial_capital = st.number_input('Capital initial (€)', 0, None, 20000, key='initial_capital')
        monthly_amount = st.number_input('Montant mensuel investi (€)', 0, None, 300, key='monthly_amount')
        investment_period = st.slider('Durée de l\'investissement (années)', 2, 100, 24, key='investment_period', label_visibility='visible')
        average_annual_performance = st.slider('Performance annuelle moyenne (%)', 1, 30, 10, key='average_annual_performance', label_visibility='visible')

        st.form_submit_button('Simuler les intérêts composés')

with col2:
    capital = compute_capital(
        initial_capital,
        monthly_amount,
        investment_period
    )
    capital_with_interests = compute_capital_with_interests(
        initial_capital,
        monthly_amount,
        investment_period,
        math.pow(1 + average_annual_performance / 100, 1 / 12) - 1
    )
    current_date = pd.Timestamp('today')
    current_year = pd.Timestamp('today').year

    data = np.array([[current_date, initial_capital, initial_capital]])
    for i in range(investment_period):
        current_capital = compute_capital(
            initial_capital,
            monthly_amount,
            i + 1
        )
        current_capital_with_interests = compute_capital_with_interests(
            initial_capital,
            monthly_amount,
            i + 1,
            math.pow(1 + average_annual_performance / 100, 1 / 12) - 1
        )
        if 'data' in locals():
            data = np.append(
                data,
                np.array([[current_date + pd.DateOffset(years=i+1), round(current_capital_with_interests), round(current_capital)]]),
                axis=0
            )
        else:
           data = np.array([[current_date, initial_capital, initial_capital]])

    chart_data = pd.DataFrame(
        data,
        columns=['date', 'Avec intérêts composés', 'Sans intérêts composés']
    )

    c1 = alt.Chart(chart_data, height=500).mark_line(point=True).encode(
        x=alt.X("date", title="Date"),
        y=alt.Y("Avec intérêts composés", title=None, scale=alt.Scale(zero=False)),
        color=alt.value('red')
    )
    c2 = alt.Chart(chart_data, height=500).mark_line(point=True).encode(
        x=alt.X("date", title="Date"),
        y=alt.Y("Sans intérêts composés", scale=alt.Scale(zero=False)),
    )

    st.altair_chart(alt.layer(c1, c2), use_container_width=True)
