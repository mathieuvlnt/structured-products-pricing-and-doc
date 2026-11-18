"""Single document pipeline for five product families.

Only product terms and scenario data vary; PDF tables, page theme, cover and
section rendering are shared across all families.
"""
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from documentation.cover import add_cover
from documentation.regulatory import regulatory_paragraphs
from documentation.contract_terms import conditional_terms, important_information
from documentation.graphique import payoff_chart
from datetime import date
import calendar
from documentation.theme import BROWN, TAUPE, SAND, IVORY, CHARCOAL, GRID, page_chrome
NAVY=BROWN; PALE=IVORY


def underlying_risks(kind, lang):
    disclosures = {
        "Share": {
            "FR": (
                "Le cours de l'action de référence dépend notamment des résultats financiers, "
                "des perspectives économiques, de la politique de dividendes et des décisions "
                "stratégiques de la société concernée. Des événements propres à cette société "
                "peuvent entraîner une baisse importante du cours, indépendamment de "
                "l'évolution générale des marchés actions.",

                "Les opérations sur titres, telles que les divisions d'actions, fusions, "
                "offres publiques, suspensions de cotation ou radiations, peuvent entraîner "
                "des ajustements contractuels du produit. L'investisseur ne détient pas "
                "directement l'action et ne bénéficie ni des droits de vote ni des "
                "dividendes attachés à celle-ci."
            ),
            "EN": (
                "The reference share price depends on the company's financial results, "
                "economic outlook, dividend policy and strategic decisions. "
                "Company-specific events may cause a significant decline in the share "
                "price independently of broader equity market performance.",

                "Corporate actions, including stock splits, mergers, tender offers, "
                "trading suspensions or delistings, may result in contractual adjustments "
                "to the product. Investors do not directly own the reference share "
                "and are not entitled to voting rights or dividends."
            )
        },

        "Equity index": {
            "FR": (
                "La performance de l'indice dépend de l'évolution des actions qui le "
                "composent et peut être affectée par des concentrations sectorielles "
                "ou géographiques. L'administrateur de l'indice peut modifier sa "
                "composition, ses pondérations ou sa méthodologie de calcul, "
                "ce qui peut influencer son niveau et sa performance.",

                "Les modalités de traitement des dividendes dépendent de la version "
                "de l'indice utilisée, notamment Price Return, Gross Total Return "
                "ou Net Total Return. Les rebalancements, interruptions de publication "
                "et événements de marché exceptionnels peuvent affecter les "
                "constatations. L'investisseur ne détient pas directement les "
                "actions composant l'indice."
            ),
            "EN": (
                "The index performance depends on the underlying constituent shares "
                "and may be affected by sector or geographical concentration. "
                "The index administrator may change its composition, weightings "
                "or calculation methodology, potentially affecting its level "
                "and performance.",

                "Dividend treatment depends on the relevant index version, including "
                "Price Return, Gross Total Return or Net Total Return. Rebalancing, "
                "publication disruptions and extraordinary market events may affect "
                "observations. Investors do not directly own the index constituents."
            )
        },

        "ETF / Fund": {
            "FR": (
                "La performance du fonds dépend de sa stratégie d'investissement, "
                "de la composition de son portefeuille et des conditions de marché. "
                "Les frais de gestion, les coûts de transaction et les écarts de "
                "réplication peuvent réduire sa performance par rapport à son "
                "indice de référence éventuel.",

                "La liquidité du fonds, les restrictions de souscription ou de rachat, "
                "les suspensions de calcul de valeur liquidative et les écarts entre "
                "le prix de marché et la valeur liquidative peuvent affecter les "
                "constatations. Le produit ne confère pas de propriété directe "
                "sur les parts du fonds."
            ),
            "EN": (
                "Fund performance depends on its investment strategy, portfolio "
                "composition and market conditions. Management fees, transaction "
                "costs and tracking differences may reduce performance relative "
                "to any applicable benchmark.",

                "Fund liquidity, subscription or redemption restrictions, "
                "suspensions of net asset value calculations and differences "
                "between market price and NAV may affect observations. "
                "The product does not provide direct ownership of fund units."
            )
        },

        "FX": {
            "FR": (
                "Les taux de change sont sensibles aux décisions de politique "
                "monétaire, aux différentiels de taux d'intérêt, aux perspectives "
                "économiques et aux flux internationaux de capitaux. Les interventions "
                "des banques centrales ou les événements géopolitiques peuvent "
                "entraîner des variations rapides et importantes des devises.",

                "Les conventions de cotation des paires de devises, les sources "
                "de fixing, les restrictions de convertibilité et les perturbations "
                "des marchés de change peuvent affecter la valorisation et les "
                "constatations du produit. Une exposition en devise étrangère "
                "peut également créer un risque de conversion."
            ),
            "EN": (
                "Exchange rates are sensitive to monetary policy decisions, "
                "interest-rate differentials, economic expectations and "
                "international capital flows. Central bank interventions "
                "or geopolitical events may cause rapid and substantial "
                "currency movements.",

                "Currency pair quotation conventions, fixing sources, "
                "convertibility restrictions and foreign-exchange market "
                "disruptions may affect product valuation and observations. "
                "Foreign-currency exposure may also introduce conversion risk."
            )
        },

        "Commodity": {
            "FR": (
                "Les prix des matières premières dépendent notamment de l'offre "
                "et de la demande physiques, des niveaux de stocks, des conditions "
                "météorologiques, des coûts de production et des événements "
                "géopolitiques. Certains marchés présentent une forte saisonnalité, "
                "une volatilité élevée et des épisodes de liquidité réduite.",

                "Lorsque le sous-jacent repose sur des contrats à terme, "
                "sa performance peut être influencée par la structure de la "
                "courbe des futures, les situations de contango ou de backwardation "
                "et les modalités de roulement des contrats. L'évolution de cette "
                "référence peut différer sensiblement de celle du prix spot. "
                "Le produit ne prévoit aucune livraison physique."
            ),
            "EN": (
                "Commodity prices depend on physical supply and demand, "
                "inventory levels, weather conditions, production costs "
                "and geopolitical developments. Certain markets exhibit "
                "significant seasonality, high volatility and periods "
                "of reduced liquidity.",

                "Where the underlying references futures contracts, performance "
                "may be affected by the futures curve structure, contango "
                "or backwardation and contract rolling conventions. "
                "The reference performance may differ materially from spot "
                "price movements. The product does not provide physical delivery."
            )
        },

        "Credit reference": {
            "FR": (
                "La qualité de crédit de l'entité de référence peut se détériorer "
                "en raison de difficultés financières, d'une hausse de son "
                "endettement ou de conditions économiques défavorables. "
                "Un événement de crédit contractuellement défini, tel qu'un "
                "défaut de paiement ou une restructuration applicable, "
                "peut entraîner une perte significative en capital.",

                "Les conséquences d'un événement de crédit dépendent notamment "
                "des définitions contractuelles, des obligations de référence, "
                "des modalités de règlement et du taux de recouvrement. "
                "Le risque de crédit de l'entité de référence est distinct "
                "du risque de crédit de l'émetteur du produit, auquel "
                "l'investisseur demeure également exposé."
            ),
            "EN": (
                "The reference entity's creditworthiness may deteriorate "
                "due to financial difficulties, increasing leverage "
                "or adverse economic conditions. A contractually defined "
                "credit event, such as failure to pay or an applicable "
                "restructuring, may result in a substantial loss of principal.",

                "The consequences of a credit event depend on contractual "
                "definitions, reference obligations, settlement provisions "
                "and recovery rates. Reference entity credit risk is separate "
                "from the product issuer's credit risk, to which investors "
                "remain exposed."
            )
        }
    }

    if kind not in disclosures:
        raise ValueError(f"Unsupported underlying category: {kind}")

    if lang not in ("FR", "EN"):
        raise ValueError(f"Unsupported language: {lang}")

    return disclosures[kind][lang]

class TermSheetGenerator:
    def __init__(self,language='EN'):
        if language not in ('EN','FR'):raise ValueError('Unsupported language')
        self.fr=language=='FR'; self.lang=language
        ss=getSampleStyleSheet()
        self.title=ParagraphStyle('V4Title',parent=ss['Heading1'],fontSize=16,leading=20,textColor=NAVY,spaceAfter=12)
        self.head=ParagraphStyle('V4Head',parent=ss['Heading2'],fontSize=11,leading=15,textColor=NAVY,spaceBefore=10,spaceAfter=7)
        self.body=ParagraphStyle('V4Body',parent=ss['BodyText'],fontSize=9,leading=14,spaceAfter=8,textColor=CHARCOAL)
        self.small=ParagraphStyle('V4Small',parent=ss['BodyText'],fontSize=8,leading=12,spaceAfter=6,textColor=CHARCOAL)
    def t(self,en,fr):return fr if self.fr else en
    def p(self,x,style=None):return Paragraph(escape(str(x)),style or self.body)
    def build(self,p,m,v,profile=None,cover_photo=None,issue_date=None):
        family=getattr(p,'family','Phoenix Autocall')
        #if family == 'Phoenix Autocall':
        issue_date = issue_date or date.today()
        maturity_year = issue_date.year + p.years

        maturity_day = min(
        issue_date.day,
        calendar.monthrange(maturity_year, issue_date.month)[1]
        )   

        maturity_date = issue_date.replace(
        year=maturity_year,
        day=maturity_day
        )
        if self.fr:
            issue_date_str = issue_date.strftime("%d/%m/%Y")
            maturity_date_str = maturity_date.strftime("%d/%m/%Y")
        else:
            issue_date_str = issue_date.strftime("%d %B %Y")
            maturity_date_str = maturity_date.strftime("%d %B %Y")

        kind=getattr(p,'kind',getattr(p,'underlying_type',None))
        buf=BytesIO(); doc=SimpleDocTemplate(buf,pagesize=(210*mm,297*mm),leftMargin=18*mm,rightMargin=18*mm,topMargin=20*mm,bottomMargin=18*mm)
        story=[];a=story.append
        def h(en,fr):a(self.p(self.t(en,fr),self.head))
        def tx(en,fr):a(self.p(self.t(en,fr)))
        def table(rows, header=True):
            tb=Table([[self.p(x,self.small) for x in row] for row in rows],colWidths=[67*mm,107*mm],hAlign='LEFT')
            tb.setStyle(TableStyle([('ROWBACKGROUNDS',(0,0 if not header else 1),(-1,-1),[IVORY,colors.white] if not header else [colors.white,IVORY]),('BACKGROUND',(0,0),(-1,0),IVORY if not header else PALE),('LINEBELOW',(0,0),(-1,-1),.3,GRID),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]));a(tb)
        fmt = lambda x: f'{x:,.0f}'.replace(",", " ") if self.fr else f'{x:,.0f}'
        pct = lambda x: f'{100*x:.0f}%'
        a(self.p(self.t('STRUCTURED INVESTMENTS | INDICATIVE TERMS','PRODUITS STRUCTURÉS | CONDITIONS INDICATIVES'),self.title))
        a(self.p(family+' — '+p.underlying,self.head))
        # One shared summary-table renderer for all five families. The rows are
        # product-specific data, not separate PDF layout engines.
        if family == 'Phoenix Autocall':
            a(self.p(self.t('CONDITIONAL COUPON AUTOCALL NOTE',
                            'NOTE AUTOCALL À COUPONS CONDITIONNELS'), self.title))
            a(self.p(self.t('Linked to ', 'Indexée sur ') + p.underlying))
            a(self.p(self.t('Capital at risk | Preliminary indicative terms',
                            'Capital à risque | Conditions indicatives préliminaires'), self.head))
            h('PRODUCT OVERVIEW', 'PRÉSENTATION DU PRODUIT')
            tx('This fictional note provides periodic conditional coupons and may redeem early if the autocall condition is met. Capital is exposed to downside at maturity if the final protection barrier is breached. Neither coupons nor principal repayment are guaranteed.',
               'Cette note fictive prévoit des coupons périodiques conditionnels et peut être remboursée par anticipation si la condition de rappel est remplie. Le capital est exposé à la baisse à échéance lorsque la barrière de protection finale n’est pas respectée. Aucun coupon ni remboursement du capital n’est garanti.')
        h('SUMMARY TERMS','CARACTÉRISTIQUES PRINCIPALES')
        kind_labels={'Share':('Share','Action'),'Equity index':('Equity index','Indice actions'),
                     'ETF / Fund':('ETF / Fund','ETF / Fonds'),'FX':('FX','Change'),
                     'Commodity':('Commodity','Matière première'),
                     'Credit':('Credit','Crédit')}
        kind_label=self.t(*kind_labels.get(kind,(str(kind),str(kind))))
        # Shared core fields, with product-specific terms appended in the same table.
        if family == 'Phoenix Autocall':
            rows=[
                (self.t('Issuer','Émetteur'),'Bank Name' if not self.fr else 'Nom de la banque'),
                (self.t('Guarantor','Garant'),'Guarantor Name' if not self.fr else 'Nom du garant'),
                (self.t('Structure','Structure'),'Phoenix Autocall - no coupon memory' if not self.fr else 'Phoenix Autocall - Pas de coupon mémoire'),
                (self.t('Underlying','Sous-jacent'),p.underlying),
                (self.t('Underlying category','Catégorie de sous-jacent'),kind_label),
                (self.t('Currency / notional','Devise / nominal'),f'{p.currency} / {fmt(p.notional)}'),
                #(self.t('Initial reference level','Niveau initial de référence'),fmt(p.spot)),
                (self.t('Issue Price',"Prix d'émission"),'100% of the Total Nominal Amount' if not self.fr else '100% du Montant Nominal Total'),

                (self.t('Reference asset','Actif de référence'),self.t('Listed share','Action cotée') if kind=='Share' else kind_label),
                (self.t('Maturity','Maturité'),f'{p.years} '+self.t('years','ans')),
                (self.t('Issue Date', "Date d'émission"),issue_date_str),
                (self.t('Maturity Date', "Date d'échéance"),maturity_date_str),

                (self.t('Observation frequency','Fréquence des observations'),f'{p.frequency} '+self.t('per year','par an')),
                (self.t('Conditional coupon','Coupon conditionnel'),f'{pct(p.coupon_rate)} '+self.t('per annum','par an')+f' / {pct(p.coupon_rate/p.frequency)} '+self.t('per period','par période')),
                (self.t('Coupon barrier','Barrière de coupon'),pct(p.coupon_barrier)),
                (self.t('Autocall barrier','Barrière de rappel'),pct(p.call_barrier)),
                (self.t('First autocall observation','Première observation de rappel'),str(p.first_call)),
                (self.t('European protection barrier','Barrière de protection européenne'),pct(p.protection_barrier)),
                #(self.t('Indicative model value','Valeur indicative du modèle'),f'{fmt(v.value)} {p.currency} ({pct(v.value/p.notional)})'),
                
            ]
        else:
            rows=[(self.t('Issuer','Émetteur'),'Bank Name' if not self.fr else 'Nom de la banque'),
                (self.t('Guarantor','Garant'),'Guarantor Name' if not self.fr else  'Nom du garant'),
                (self.t('Term','Caractéristique'),self.t('Indicative value','Valeur indicative')),
                  (self.t('Product','Produit'),family),(self.t('Underlying','Sous-jacent'),p.underlying),
                  (self.t('Asset Class',"Classe d'actif"),'Credit' if kind == 'Credit reference' else kind_label),
                  (self.t('Denomination / currency','Nominal / devise'),f'{fmt(p.notional)} {p.currency}'),
                  #(self.t('Initial reference level','Niveau initial'),fmt(p.spot)),
                  (self.t('Issue Price',"Prix d'émission"),'100% of the Total Nominal Amount' if not self.fr else '100% du Montant Nominal Total'),
                  (self.t('Maturity','Maturité'),f'{p.years} '+self.t('years','ans')),
                (self.t('Issue Date', "Date d'émission"),issue_date_str),
                (self.t('Maturity Date', "Date d'échéance"),maturity_date_str),
                  #(self.t('Indicative model value','Valeur indicative'),f'{fmt(v.value)} {p.currency} ({pct(v.value/p.notional)})'),
                  #(self.t('Pricing model','Modèle de valorisation'),getattr(v,'model','GBM Monte Carlo (constant volatility)'))
                  ]
            if family=='European Option':rows += [(self.t('Option','Option'),p.option_type),(self.t('Strike / initial','Strike / initial'),pct(p.strike))]
            elif family=='Athena Autocall':rows += [(self.t('Autocall barrier','Barrière de rappel'),pct(p.call_barrier)),(self.t('Protection barrier','Barrière de protection'),pct(p.protection_barrier)),(self.t('Accrued gain','Gain cumulé'),pct(p.coupon_rate)+' '+self.t('per year','par an')),(self.t('First call observation','Première observation de rappel'),str(p.first_call))]
            elif family=='Capital Protected Note':rows += [(self.t('Protected principal fraction','Fraction protégée du capital'),pct(p.protection)),(self.t('Upside participation','Participation à la hausse'),pct(p.participation)),(self.t('Call strike','Strike du call'),pct(p.strike))]
            else:rows += [(self.t('Reference entity','Entité de référence'),p.reference_entity),(self.t('Coupon rate','Taux de coupon'),pct(p.coupon_rate)),(self.t('Default intensity (annual)','Intensité de défaut annuelle'),pct(p.credit_hazard)),(self.t('Assumed recovery','Recouvrement supposé'),pct(p.recovery))]
        table(rows,header=family!='Phoenix Autocall')
                
        a(PageBreak())
        a(self.p(self.t('PART A — CONTRACTUAL PRODUCT TERMS','PARTIE A — CONDITIONS CONTRACTUELLES DU PRODUIT'),self.title))
        h('Product description','Description du produit')
        if family=='Phoenix Autocall':
            tx('This Phoenix pays a conditional coupon at each observation when the reference ratio is at or above the coupon barrier. From the first eligible autocall observation, a ratio at or above the autocall barrier triggers early redemption of principal and terminates future payments. If no early redemption occurs, principal is repaid at maturity only if the final ratio meets the European protection barrier; otherwise the redemption follows the final ratio. No coupon memory applies.', 'Ce Phoenix verse un coupon conditionnel à chaque constatation lorsque le ratio de référence atteint la barrière de coupon. À partir de la première constatation éligible, le franchissement de la barrière de rappel déclenche le remboursement anticipé du nominal et met fin aux paiements futurs. Sans rappel, le nominal est remboursé à échéance si la barrière européenne de protection est respectée ; sinon le remboursement suit le ratio final. Les coupons ne sont pas mémorisés.')
        elif family=='European Option':
            tx(f'At maturity, the {p.option_type.lower()} pays notional multiplied by the positive part of the underlying ratio minus strike (call), or strike minus ratio (put). The option buyer pays a premium and may lose it in full.',f'À échéance, le {p.option_type.lower()} verse le nominal multiplié par la partie positive du ratio final moins le strike (call), ou du strike moins le ratio (put). L’acheteur verse une prime qu’il peut perdre intégralement.')
        elif family=='Athena Autocall':
            tx('This illustrative Athena pays no periodic coupons. If the underlying meets the autocall barrier on an eligible observation, the note redeems at principal plus a simple annual gain accrued from inception. Otherwise, at maturity the investor receives principal plus the accrued gain if the final autocall condition is met; principal if above the European protection barrier; or principal multiplied by the final ratio if below it.', 'Cet Athena illustratif ne verse pas de coupon périodique. Si le sous-jacent atteint la barrière de rappel à une observation éligible, le nominal et un gain annuel simple cumulé depuis l’origine sont remboursés. Sinon, à échéance : nominal et gain si la condition de rappel finale est remplie ; nominal si la barrière européenne de protection est respectée ; sinon nominal multiplié par le ratio final.')
        elif family=='Capital Protected Note':
            tx('At maturity, redemption equals the protected fraction of principal plus participation in the positive performance above strike. Protection is contractual at scheduled maturity only and remains subject to issuer credit risk; it is not a deposit guarantee.', 'À échéance, le remboursement correspond à la fraction protégée du nominal augmentée de la participation à la performance positive au-dessus du strike. La protection est contractuelle uniquement à l’échéance prévue et demeure soumise au risque de crédit de l’émetteur ; elle ne constitue pas une garantie de dépôt.')
        else:
            tx('The note pays a contractual running coupon until maturity or a credit event. Under the simplified recovery-at-default convention, a credit event terminates the note and pays the assumed recovery fraction of principal at the event time. If no event occurs, principal is repaid at maturity. Real CLNs require defined credit events, settlement rules and reference obligations.', 'La note verse un coupon courant jusqu’à échéance ou jusqu’à un événement de crédit. Selon la convention simplifiée de recouvrement au défaut, un événement met fin à la note et déclenche le versement de la fraction de recouvrement supposée. Sans événement, le nominal est remboursé à échéance. Une véritable CLN exige des définitions d’événements de crédit, des règles de règlement et des obligations de référence.')
        h('Indicative contractual definitions','Définitions contractuelles indicatives')
        table([(self.t('Defined term','Terme défini'),self.t('Illustrative application','Application illustrative'))]+conditional_terms(p,self.lang))
        h('Model / market conventions','Conventions de marché et de modèle')
        table([(self.t('Assumption','Hypothèse'),self.t('Value','Valeur')),(self.t('Risk-free discount rate','Taux sans risque'),pct(m.rate)),(self.t('Carry / foreign yield proxy','Portage / rendement étranger'),pct(m.dividend)),(self.t('Constant volatility','Volatilité constante'),pct(m.volatility)),(self.t('Model','Modèle'),getattr(v,'model','GBM Monte Carlo (constant volatility)'))])
        tx('Underlying reference and dates are illustrative. Market fixing source, business-day calendars, disruption events, settlement conventions and corporate-action adjustment terms have not been legally defined.', 'La référence et les dates sont illustratives. La source de constatation, les calendriers, perturbations, conventions de règlement et ajustements d’opérations sur titres ne sont pas définis juridiquement.')
        a(PageBreak())
        a(self.p(self.t('ILLUSTRATIVE REDEMPTION EXAMPLES','EXEMPLES ILLUSTRATIFS DE REMBOURSEMENT'),self.title))
        if family=='Credit Linked Note':
            table([(self.t('Credit scenario','Scénario de crédit'),self.t('Principal outcome (excludes prior coupons)','Capital remboursé (hors coupons déjà versés)')),(self.t('No credit event','Aucun événement de crédit'),f'{fmt(p.notional)} {p.currency}'),(self.t('Credit event; assumed recovery','Événement de crédit ; recouvrement supposé'),f'{fmt(p.notional*p.recovery)} {p.currency}')])
            tx('The illustrative recovery rate is an assumption, not an estimated recovery on a named entity. Coupons stop upon a credit event.','Le taux de recouvrement est une hypothèse, non une estimation pour une entité donnée. Les coupons cessent en cas d’événement de crédit.')
        elif family=='Phoenix Autocall':
            cases=[]
            for label,ratio in [('Severe downside',.35),('Moderate downside',.8),('Flat',1.0)]:
                path=[max(0.0,min(p.call_barrier-.01,.75))]*(p.periods-1)+[ratio]
                flows=p.cashflows(path)
                cases.append((label,f'{ratio:.0%}',f'{fmt(sum(f["redemption"] for f in flows))} {p.currency}'))
            path=[max(0.0,min(p.call_barrier-.01,.75))]*(p.first_call-1)+[max(p.call_barrier,1.05)] + [1.]*(p.periods-p.first_call)
            flows=p.cashflows(path)
            cases.append(('Early autocall',f'{path[p.first_call-1]:.0%}',f'{fmt(sum(f["redemption"] for f in flows))} {p.currency}'))
            table([(self.t('Illustrative scenario','Scénario illustratif'),self.t('Final / call ratio and principal redemption','Ratio final / de rappel et remboursement du capital'))]+[(self.t(x,{'Severe downside':'Forte baisse','Moderate downside':'Baisse modérée','Flat':'Stable','Early autocall':'Rappel anticipé'}.get(x,x)),f'{y} / {z}') for x,y,z in cases])
            tx('Principal redemptions shown exclude conditional coupons. The early-call case satisfies the selected autocall barrier at the first eligible observation; all other cases assume no earlier autocall.', 'Les remboursements de capital présentés excluent les coupons conditionnels. Le scénario de rappel satisfait la barrière à la première constatation éligible ; les autres scénarios supposent l’absence de rappel antérieur.')
        else:
            cases=[]
            
            #for label,ratio in [('Severe downside',.35),('Moderate downside',.8),('Flat',1.0),('Upside',1.3)]:
            scenarios = [
            (self.t('Severe downside', 'Forte baisse'), 0.35),
            (self.t('Moderate downside', 'Baisse modérée'), 0.80),
            (self.t('Flat', 'Stable'), 1.00),
            (self.t('Upside', 'Hausse'), 1.30),
            ]

            for label, ratio in scenarios:    
                if family=='Athena Autocall':
                    path=[min(.8,p.call_barrier-.05)]*(p.periods-1)+[ratio]
                    outcome=p.cashflows(path)[-1]['redemption']
                else:outcome=p.cashflows([ratio]*p.periods)[-1]['redemption']
                cases.append((label,f'{ratio:.0%}',f'{fmt(outcome)} {p.currency}'))
            table([(self.t('Illustrative scenario','Scénario illustratif'),self.t('Final underlying ratio / redemption','Ratio final / remboursement'))]+[(x,f'{y} / {z}') for x,y,z in cases])
            tx('For Athena, the examples assume no earlier autocall and a constant below-call level before the final observation. Results are contractual examples, not probabilities or PRIIPs scenarios.', 'Pour Athena, les exemples supposent l’absence de rappel préalable et un niveau inférieur à la barrière avant la dernière observation. Il s’agit d’exemples contractuels, non de probabilités ou de scénarios PRIIPs.')
        
        h(
    'ILLUSTRATIVE PAYOFF AT MATURITY',
    'REMBOURSEMENT ILLUSTRATIF À ÉCHÉANCE'
)

        a(Spacer(1, 8))

        a(payoff_chart(p, self.lang))

        a(Spacer(1, 8))

        if family in ('Phoenix Autocall', 'Athena Autocall'):
            tx(
        'Illustration of principal redemption at maturity only, '
        'assuming no early autocall. Coupons and additional '
        'payments are excluded.',
        'Illustration du remboursement du capital à échéance '
        'uniquement, en l’absence de rappel anticipé. '
        'Les coupons et paiements complémentaires sont exclus.'
    )

        elif family == 'European Option':
            tx(
        'Gross option payoff at maturity, excluding '
        'the initial premium and transaction costs.',
        'Payoff brut de l’option à échéance, '
        'hors prime initiale et frais de transaction.'
    )

        elif family == 'Capital Protected Note':
            tx(
        'Illustrative maturity repayment, subject to '
        'issuer credit risk.',
        'Remboursement illustratif à échéance, '
        'sous réserve du risque de crédit de l’émetteur.'
    )

        elif family == 'Credit Linked Note':
            tx(
        'Illustrative principal repayment with or without '
        'a credit event. Coupons are excluded.',
        'Remboursement illustratif du capital avec ou sans '
        'événement de crédit. Les coupons sont exclus.'
    )
        
        h('Pricing interpretation','Interprétation de la valorisation')
        tx('The indicated price is a simplified risk-neutral present value, not a tradable quote. It excludes issuer funding spread, hedging costs, transaction costs, distribution fees and model calibration to market surfaces.', 'Le prix indiqué est une valeur actuelle risque-neutre simplifiée, et non une cotation exécutable. Il exclut le spread de financement de l’émetteur, les coûts de couverture, de transaction, de distribution et la calibration aux surfaces de marché.')
        a(PageBreak())
        if family=='Phoenix Autocall':
            a(self.p(self.t('OBSERVATION & CASH-FLOW MECHANICS','MÉCANISMES DE CONSTATATION ET DE FLUX'),self.title))
            h('Conditional coupons','Coupons conditionnels')
            tx(f'At each of the {p.periods} scheduled observations, the illustrative coupon is {pct(p.coupon_rate/p.frequency)} of notional if the reference ratio is at least {pct(p.coupon_barrier)}. Otherwise no coupon is paid for that observation; missed coupons are not carried forward.', f'À chacune des {p.periods} constatations, le coupon illustratif est de {pct(p.coupon_rate/p.frequency)} du nominal si le ratio atteint {pct(p.coupon_barrier)}. À défaut, aucun coupon n’est versé pour la période et les coupons manqués ne sont pas reportés.')
            h('Automatic early redemption','Remboursement anticipé automatique')
            tx(f'Beginning at observation {p.first_call}, before maturity, a reference ratio at or above {pct(p.call_barrier)} causes automatic repayment of 100% of notional. No subsequent coupon or principal payment is due.', f'À compter de la constatation {p.first_call}, avant échéance, un ratio au moins égal à {pct(p.call_barrier)} entraîne le remboursement automatique de 100 % du nominal. Aucun paiement ultérieur de coupon ou de capital n’est dû.')
            h('Final redemption without autocall','Remboursement final sans rappel')
            table([(self.t('Final reference ratio','Ratio final'),self.t('Principal redemption','Remboursement du nominal')),(self.t('At least','Au moins')+' '+pct(p.protection_barrier),f'{fmt(p.notional)} {p.currency}'),(self.t('Below','Inférieur à')+' '+pct(p.protection_barrier),self.t('Notional × final ratio','Nominal × ratio final'))])
            h('Contractual limitations','Limites contractuelles')
            tx('Actual fixing dates, business-day adjustments, calculation-agent determinations, disruption events, issuer credit terms and settlement mechanics must be specified in definitive legal documentation.', 'Les dates de constatation, ajustements calendaires, décisions de l’agent de calcul, perturbations, conditions de crédit de l’émetteur et modalités de règlement doivent être définis dans la documentation juridique définitive.')
            a(PageBreak())
        a(self.p(self.t('PART B — IMPORTANT INVESTOR INFORMATION','PARTIE B — INFORMATIONS IMPORTANTES POUR LES INVESTISSEURS'),self.title))
        h('Structure-specific risks','Risques propres à la structure')
        descriptions={
            'Phoenix Autocall':('Conditional coupons can be missed; early redemption limits upside and creates reinvestment risk. If the final protection test fails, capital loss can be substantial or total. The investor bears issuer credit and secondary-market liquidity risk.', 'Les coupons conditionnels peuvent ne pas être versés ; le rappel limite le potentiel de gain et crée un risque de réinvestissement. Si le test final de protection échoue, la perte en capital peut être importante ou totale. L’investisseur supporte les risques de crédit de l’émetteur et de liquidité.'),
            'European Option':('The buyer can lose the entire premium; option value depends on time to expiry, volatility and rates. Exercise is European only.', 'L’acheteur peut perdre toute la prime ; la valeur dépend de l’échéance, de la volatilité et des taux. L’exercice est uniquement européen.'),
            'Athena Autocall':('Early redemption limits future upside and creates reinvestment risk. If protection fails at maturity, principal can be lost in full; no periodic coupons are paid.', 'Le rappel anticipé limite le potentiel futur et crée un risque de réinvestissement. En cas de franchissement de la barrière à échéance, la perte peut atteindre la totalité du capital ; aucun coupon périodique n’est versé.'),
            'Capital Protected Note':('Protection only applies at scheduled maturity and is subject to issuer default. Early sale may produce a loss; participation may be capped by contractual terms in a real note.', 'La protection ne s’applique qu’à échéance et reste soumise au défaut de l’émetteur. Une cession anticipée peut générer une perte ; la participation peut être plafonnée dans une émission réelle.'),
            'Credit Linked Note':('A credit event can cause immediate substantial loss of principal. Recovery is uncertain; issuer and reference-entity credit exposures can coexist.', 'Un événement de crédit peut entraîner une perte immédiate et importante du capital. Le recouvrement est incertain ; les risques de crédit de l’émetteur et de l’entité de référence peuvent se cumuler.')}
        tx(*descriptions[family])
        h('Underlying-specific risk factors','Risques propres au sous-jacent')
        for paragraph in underlying_risks(kind,self.lang):a(self.p(paragraph))
        if family=='Credit Linked Note':
            h('Credit reference and definitions','Référence de crédit et définitions')
            tx(f'The reference entity is labelled {p.reference_entity}. No ISDA definitions, deliverable obligations, succession provisions or auction settlement mechanism are implemented.',f'L’entité de référence est désignée {p.reference_entity}. Aucune définition ISDA, obligation livrable, disposition de succession ni procédure de règlement par enchères n’est implémentée.')
        h('Product and reference disclosures','Informations sur le produit et la référence')
        for paragraph in regulatory_paragraphs(family,kind,self.lang):
            a(self.p(paragraph,self.small))
        a(self.p(important_information(family,kind,self.lang),self.small))
        h('Issuer, liquidity and legal limitations','Émetteur, liquidité et limites juridiques')
        tx('An actual issued note carries issuer credit risk and may have no liquid secondary market. No issuer, guarantor, ISIN, listing, fees or offering jurisdiction has been specified.', 'Une note effectivement émise comporte un risque de crédit de l’émetteur et peut être dépourvue de marché secondaire liquide. Aucun émetteur, garant, ISIN, cotation, frais ou juridiction de commercialisation n’est défini.')
        def footer(canvas,document):
            page_chrome(canvas,document,self.lang,total=5 if family=='Phoenix Autocall' else 4,left=18*mm,right=18*mm)
        doc.build(story,onFirstPage=footer,onLaterPages=footer)
        return add_cover(buf.getvalue(),p,self.lang,photo_bytes=cover_photo)

