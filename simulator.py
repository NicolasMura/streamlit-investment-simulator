"""
# Investment simulator
"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import math

st.set_page_config(layout='wide')

st.markdown(
    '''
        <style>
               .block-container {
                    padding-top: 30px;
                    padding-bottom: 30px;
                }
        </style>
    ''',
    unsafe_allow_html=True)

st.write(
    '''
        <a href="https://github.com/NicolasMura/streamlit-investment-simulator" style="display: inline-flex; align-items: center; text-decoration:none; color: inherit">
            <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="22px" />
            <span style="margin-left: 10px; vertical-align: text-bottom;">Code source</span>
        </a>
    ''',
    unsafe_allow_html=True)

st.markdown('## Étape 1 - Intérêts composés')

st.markdown('Si toi aussi tu veux devenir rentier, joue avec les paramètres ci-dessous.')


@st.cache_data()
def compute_capital_with_interests(
    initial_capital,
    monthly_amount,
    investment_period_in_years,
    average_monthly_performance,
    monthly_management_fees
):
    initial_capital_interests = initial_capital * \
        math.pow(1 + average_monthly_performance,
                 12 * investment_period_in_years)
    initial_capital_interests_with_fees = initial_capital * \
        math.pow(1 + (average_monthly_performance - monthly_management_fees), 12 * investment_period_in_years)
    composed_interests = (monthly_amount * (math.pow(1 + average_monthly_performance, 12 *
                          investment_period_in_years) - 1)) / (average_monthly_performance)
    composed_interests_with_fees = (monthly_amount * (math.pow(1 + average_monthly_performance - monthly_management_fees,
                                     12 * investment_period_in_years) - 1)) / (average_monthly_performance - monthly_management_fees)

    final_capital = initial_capital_interests + composed_interests
    final_capital_with_fees = initial_capital_interests_with_fees + \
        composed_interests_with_fees

    return final_capital, final_capital_with_fees


@st.cache_data()
def compute_capital(
    initial_capital,
    monthly_amount,
    investment_period_in_years
):
    return initial_capital + monthly_amount * investment_period_in_years * 12


total = 0

col1, col2 = st.columns([2, 3])
with col1:
    with st.form('form'):
        initial_capital = st.number_input(
            'Capital initial (€)', min_value=0, max_value=None, value=20000, key='initial_capital')
        monthly_amount = st.number_input(
            'Montant mensuel investi (€)', min_value=0, max_value=None, value=350, key='monthly_amount')
        investment_period = st.slider('Durée de l\'investissement (années)',
                                      min_value=2, max_value=100, value=24, key='investment_period', label_visibility='visible')
        average_annual_performance = st.slider(
            'Performance annuelle moyenne (%)', min_value=1, max_value=30, value=10, key='average_annual_performance', label_visibility='visible')
        annual_management_fees = st.slider(
            'Frais (%)', min_value=0.00, max_value=5.00, value=0.70, step=0.1, key='annual_management_fees', label_visibility='visible')

        st.form_submit_button('Simuler les intérêts composés')

current_date = pd.Timestamp('today')
# st.write(current_date)
# st.write(type(current_date))

# st.write((math.pow(1 + average_annual_performance / 100, 1 / 12) - 1) * 100)
data = np.array(
    [[current_date, initial_capital, initial_capital, initial_capital]])
for i in range(investment_period):
    current_capital = compute_capital(
        initial_capital,
        monthly_amount,
        i + 1
    )
    capital_with_interests, capital_with_interests_with_fees = compute_capital_with_interests(
        initial_capital,
        monthly_amount,
        i + 1,
        math.pow(1 + average_annual_performance / 100, 1 / 12) - 1,
        math.pow(1 + annual_management_fees / 100, 1 / 12) - 1,
    )
    if 'data' in locals():
        data = np.append(
            data,
            np.array([[
                current_date + pd.DateOffset(years=i+1),
                current_capital,
                capital_with_interests_with_fees,
                capital_with_interests,
            ]]),
            axis=0
        )
    else:
        data = np.array([[current_date, initial_capital, initial_capital]])

# st.write(type(data))
# st.write(data)

df = pd.DataFrame(
    data,
    # columns=['A', 'B', 'C'], index=pd.RangeIndex(100, name='x')
    columns=['Date', 'Sans intérêts composés',
             'Avec intérêts composés (avec frais)', 'Avec intérêts composés (sans frais)'],
)
# st.write(df)
df.drop(0)
# st.write(df)
df = df.reset_index(drop=True).melt('Date', var_name='Type', value_name='capital')
# st.write(df)

# Create a selection that chooses the nearest point & selects based on Date-value
nearest = alt.selection_point(nearest=True, on='mouseover',
                        fields=['Date'], empty=False)

# The basic line chart
composed_interests_chart = alt.Chart(df).mark_line(point=True).encode(
    x=alt.X('year(Date):T', title='Année', axis=alt.Axis(grid=False)), # O, N, Q, T, G.
    y=alt.X('capital:Q', title=None, axis=alt.Axis(grid=True, format='s')).scale(zero=False, domain=(df['capital'].min(), df['capital'].max()*120/100)),
    tooltip=[
        alt.Tooltip('year(Date):T', title='Année'),
        alt.Tooltip('capital:Q', title='Capital', format='s'),
    ],
    color=alt.Color('Type:N', title=None, sort=['Avec intérêts composés (sans frais)', 'Avec intérêts composés (avec frais)'],
                    scale=alt.Scale(scheme='set1'),
                    legend=alt.Legend(orient='top-left', strokeColor='gray', fillColor='#FFF',
                                      labelColor='black', labelLimit=0))
)

# # Transparent selectors across the chart. This is what tells us
# # the x-value of the cursor
selectors = alt.Chart(df).mark_point().encode(
    x='year(Date):T',
    opacity=alt.value(0),
).add_params(
    nearest
)

# Draw points on the line, and highlight based on selection
points = composed_interests_chart.mark_point().encode(
    opacity=alt.condition(nearest, alt.value(1), alt.value(0))
)

# Draw text labels near the points, and highlight based on selection
text = composed_interests_chart.mark_text(align='left', dx=5, dy=-20).encode(
    text=alt.condition(nearest, 'capital:Q', alt.value(''), format='s')
)

# Draw a rule at the location of the selection
rules = alt.Chart(df).mark_rule(color='gray').encode(
    x='year(Date):T',
).transform_filter(
    nearest
)

# Put the five layers into a chart and bind the data
col2.altair_chart(
    alt.layer(
        composed_interests_chart, selectors, points, rules, text),
    use_container_width=True
)

final_capital_without_interests = df[df['Type'].isin(['Sans intérêts composés'])].iloc[-1]['capital']
final_capital_wit_interests_without_fees = round(df[df['Type'].isin(['Avec intérêts composés (sans frais)'])].iloc[-1]['capital'], 2)
final_capital_wit_interests_with_fees = round(df[df['Type'].isin(['Avec intérêts composés (avec frais)'])].iloc[-1]['capital'], 2)
interests = float(final_capital_wit_interests_with_fees) - float(final_capital_without_interests)
col2.markdown(f'''
    Avec un capital de **{initial_capital} €** et en épargnant **{monthly_amount} €** par mois
    pour une durée de **{investment_period} ans**, vous accumulez **{final_capital_without_interests} €**.
    Si vous avez investi cet argent avec une performance annuelle de **{average_annual_performance}%**,
    votre patrimoine total sera de **{final_capital_wit_interests_with_fees} €**.
    Les intérêts accumulés sont donc de
    {final_capital_wit_interests_with_fees} - {final_capital_without_interests} = **{interests} €**.
''')
