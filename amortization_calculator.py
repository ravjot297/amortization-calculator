import datetime as dt
from dateutils import month_start, relativedelta

import numpy as np
import numpy_financial as npf
import pandas as pd
import matplotlib.pyplot as plt

import streamlit as st


st.set_page_config(layout="centered")


st.write("## Amortization Calculator")
col1, col2, col3 = st.columns(3)

# Inputs
loan_amount = col1.number_input("Loan Amount (in $)", min_value=0, value=100000)
interest_rate = col2.number_input("Interest Rate (p.a. in %)", min_value=0.0, max_value=100.0, value=5.0, step=1.0,
                                  format="%0.3f")
loan_term_in_years = col3.number_input("Time Period (in years)", min_value=1, max_value=100, value=10)


# Calculations
loan_term_in_months = loan_term_in_years*12
converted_interest_rate_monthly = interest_rate/(12*100)
start = month_start(dt.date.today() + dt.timedelta(30))

# list of month's start dates
periods = [start + relativedelta(months=x) for x in range(loan_term_in_months)]


monthly_pmt= [np.round(npf.pmt(converted_interest_rate_monthly, loan_term_in_months, -loan_amount),0)
              for month in range(1, loan_term_in_months+1)]

interest_pmt= [np.round(npf.ipmt(converted_interest_rate_monthly, month, loan_term_in_months, -loan_amount), 0)
               for month in range(1, loan_term_in_months+1)]

principal_pmt= [np.round(npf.ppmt(converted_interest_rate_monthly, month, loan_term_in_months, -loan_amount), 0)
                for month in range(1, loan_term_in_months+1)]

total_interest = sum(interest_pmt)
total_repayments = sum(monthly_pmt)



#Display Repayments and Pie Chart

col1, col2 = st.columns(2)

with col1:
    st.write("### Repayments")
    st.metric(label="Monthly Repayments", value=f"${monthly_pmt[0]:,.0f}")
    st.metric(label="Total Repayments", value=f"${total_repayments:,.0f}")
    st.metric(label="Total Interest Paid", value=f"${total_interest:,.0f}")


with col2:

    st.write("   ")
    st.write("   ")

    # Creating Pie Chart
    pie_labels = ["Interest", "Loan"]
    pie_data = [total_interest, loan_amount]

    fig2 = plt.figure(figsize=(2.5, 2.5))
    plt.pie(pie_data, labels=pie_labels, explode=(0.05, 0.05), shadow=True, startangle=90, autopct='%.0f%%',
            pctdistance=0.5, labeldistance=1.1, radius=1.1)

    st.pyplot(fig2)


#Data Frame
table = pd.DataFrame({'Payment': monthly_pmt, 'Interest': interest_pmt, 'Principal': principal_pmt},
                     index=pd.to_datetime(periods))
table.index.names = ['Date ']
table['Balance'] = loan_amount - table['Principal'].cumsum()
table['Total Interest'] = table['Interest'].cumsum()
table['Total Repayment'] = table['Payment'].cumsum()
table['Date'] = table.index
table['Date'] = table['Date'].apply(lambda x: x.date())
table['Year'] = (np.arange(len(table)) // 12) + 1




# Display Payment Schedule Chart and Monthly Schedule Table
st.write("### Payment Schedule")
st.line_chart(table, y=["Balance", "Total Interest", "Total Repayment"], use_container_width=True)


st.write("### Monthly Schedule")

col1, col2 = st.columns(2)
with col1:
    st.caption("Loan Start Date" + " " + str(table.index.date[0]))
with col2:
    st.caption("Loan End Date" + " " + str(table.index.date[-1]))

st.dataframe(table, column_order=("Year", "Date", "Payment", "Interest", "Principal", "Balance"),
             use_container_width=True, hide_index=True)
