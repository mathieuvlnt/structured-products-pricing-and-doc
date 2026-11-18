import streamlit as st
from products.phoenix import Phoenix
from products.multi import Note,KINDS
from pricing.monte_carlo import Market,GBMMonteCarloPricer
from pricing.multi import MultiPricer
from documentation.generator import TermSheetGenerator
from documentation.disclosures import UnderlyingProfile
from datetime import date

st.set_page_config(page_title='Structured Products | Pricing & Documentation',layout='wide',page_icon='📊')
from ui.theme import apply_theme
apply_theme()
st.markdown('<div class="desk-kicker">STRUCTURED PRODUCTS DESK / INDEPENDENT PROTOTYPE</div>', unsafe_allow_html=True)
st.markdown('<h1 class="desk-title">Pricing & Documentation</h1>', unsafe_allow_html=True)
st.markdown('<div class="desk-subtitle">Indicative valuation · Contractual mechanics · Document generation</div>', unsafe_allow_html=True)
st.markdown('<div class="desk-rule"></div>', unsafe_allow_html=True)
with st.sidebar:
    family=st.selectbox('Product family',['Phoenix Autocall','European Option','Athena Autocall','Capital Protected Note','Credit Linked Note'])
    language=st.selectbox('Document language',['EN','FR'])
    kinds=list(KINDS)
    if family=='Capital Protected Note':kinds=kinds[:3]
    if family=='Credit Linked Note':kinds=['Credit reference']
    #kind=st.selectbox('Underlying category',kinds)
    kind=st.selectbox(
    'Underlying category',
    kinds,
    index=kinds.index('Equity index') if 'Equity index' in kinds else 0,    
    format_func=lambda x: 'Credit' if x == 'Credit reference' else x)
    underlying=st.text_input('Reference name','EURO STOXX 50 Index')
    currency=st.selectbox('Currency',['EUR','USD','GBP','CHF'])
    index_variant=st.selectbox('Index convention',['Price Return','Net Total Return','Gross Total Return'],disabled=kind!='Equity index')
    fixing=st.text_input('Reference fixing source','Not specified')
st.markdown('<div class="desk-section">01 / PRODUCT & MARKET PARAMETERS</div>', unsafe_allow_html=True)
a,b,c=st.columns(3)
with a:
    notional=st.number_input('Notional',1000.,100000000.,100000.,step=1000.)
    spot=st.number_input('Initial reference level',0.01,10000000.,100.,step=1.)
    years=st.selectbox('Maturity (years)',list(range(1,11)),index=2)
    issue_date = (
    st.date_input(
        "Issue Date",
        value=date.today(),
        min_value=date(2020, 1, 1),
        max_value=date(2050, 12, 31),
        format="DD/MM/YYYY"
    )
    )
    frequency=st.selectbox('Observations per year',[1,2,4,12],index=2)
    option_type=st.selectbox('Option type',['Call','Put']) if family=='European Option' else 'Call'
    strike=st.number_input('Strike (% of initial)',1.,300.,100.,step=5.)/100 if family in ('European Option','Capital Protected Note') else 1.
with b:
    coupon_rate=st.number_input('Coupon / accrued gain (% p.a.)',0.,100.,8.,step=.25)/100 if family in ('Phoenix Autocall','Athena Autocall','Credit Linked Note') else .08
    coupon_barrier=st.number_input('Coupon barrier (%)',1.,200.,80.,step=1.)/100 if family=='Phoenix Autocall' else .7
    call_barrier=st.number_input('Autocall barrier (%)',1.,200.,105.,step=1.)/100 if family in ('Phoenix Autocall','Athena Autocall') else 1.
    protection_barrier=st.number_input('European downside barrier (%)',1.,99.,60.,step=1.)/100 if family in ('Phoenix Autocall','Athena Autocall') else .6
    first_call=st.number_input('First eligible autocall observation',min_value=1,max_value=max(1,years*frequency-1),value=min(frequency,max(1,years*frequency-1))) if family in ('Phoenix Autocall','Athena Autocall') else 1
    protection=st.number_input('Capital floor at maturity (%)',1.,100.,100.,step=5.)/100 if family=='Capital Protected Note' else 1.
    participation=st.number_input('Upside participation (%)',0.,300.,100.,step=10.)/100 if family=='Capital Protected Note' else 1.
with c:
    rate=st.number_input('Risk-free rate (%)',-20.,50.,3.,step=.25)/100
    dividend=st.number_input('Continuous yield / foreign rate proxy (%)',-10.,50.,2.,step=.25)/100
    volatility=st.number_input('Volatility (%)',.1,200.,20.,step=.5)/100
    paths=st.select_slider('Monte Carlo paths',[5000,10000,30000,50000,100000],value=30000)
    reference_entity=st.text_input('Credit reference entity','Illustrative Reference Entity') if family=='Credit Linked Note' else ''
    credit_hazard=st.number_input('Default intensity (% p.a.)',0.,100.,2.5,step=.5)/100 if family=='Credit Linked Note' else .025
    recovery=st.number_input('Recovery (%)',0.,100.,40.,step=5.)/100 if family=='Credit Linked Note' else .4
params=(family,language,kind,underlying,currency,index_variant,fixing,notional,spot,years,frequency,option_type,strike,coupon_rate,coupon_barrier,call_barrier,protection_barrier,first_call,protection,participation,rate,dividend,volatility,paths,reference_entity,credit_hazard,recovery,issue_date)
if st.button('Calculate indicative model value',type='primary'):
    try:
        m=Market(rate,dividend,volatility)
        if family=='Phoenix Autocall':
            p=Phoenix(underlying,kind,currency,notional,spot,years,frequency,coupon_rate,coupon_barrier,call_barrier,protection_barrier,first_call)
            v=GBMMonteCarloPricer(paths).price(p,m)
        else:
            p=Note(family,underlying,kind,currency,notional,spot,years,frequency,coupon_rate,coupon_barrier,call_barrier,protection_barrier,first_call,strike,participation,protection,credit_hazard,recovery,reference_entity,option_type)
            v=MultiPricer(paths).price(p,m)
        st.session_state['valuation']=(params,p,m,v)
    except ValueError as e:st.error(str(e))
if 'valuation' in st.session_state:
    old,p,m,v=st.session_state['valuation']
    if old!=params:st.warning('Inputs or language changed. Recalculate before exporting.')
    else:
        st.markdown('<div class="desk-section">02 / INDICATIVE VALUATION</div>', unsafe_allow_html=True)
        # Indicative valuation as % of notional
        price_pct = (v.value / notional) * 100
        if family in ('Phoenix Autocall', 'Athena Autocall'):
            x, y, z = st.columns(3)
            x.metric('Indicative model price', f'{price_pct:.2f} %', help=f'Equivalent to {v.value:,.0f} {currency}')
            se_pct = (v.standard_error / notional) * 100
            y.metric('MC standard error', f'{se_pct:.2f} %', help=f'Equivalent to {v.standard_error:,.0f} {currency}')
            z.metric('Early call probability', f'{v.call_probability:.1%}')
        else:
            x, y = st.columns(2)
            x.metric('Indicative model price', f'{price_pct:.2f} %', help=f'Equivalent to {v.value:,.0f} {currency}')
            y.metric('Valuation method', 'Analytical' if v.standard_error == 0 else 'Monte Carlo')
            st.caption(f'Pricing model: {v.model}')
        try:
            if family == 'Phoenix Autocall':
                pdf = TermSheetGenerator(language).build( p, m, v,UnderlyingProfile(kind, underlying, index_variant,fixing_source=fixing),issue_date=issue_date)
            else:pdf=TermSheetGenerator(language).build(p,m,v)
            st.download_button('Download indicative PDF',pdf,file_name=f'{family.replace(" ","_")}_{language}.pdf',mime='application/pdf')
        except Exception as e:st.error(f'PDF generation failed: {e}')

