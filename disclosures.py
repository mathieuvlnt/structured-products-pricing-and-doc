"""Original illustrative disclosure blocks; not legal documentation."""
from dataclasses import dataclass

@dataclass(frozen=True)
class UnderlyingProfile:
    kind: str
    name: str
    index_variant: str = 'Price Return'
    sponsor: str = 'Not specified'
    fixing_source: str = 'Not specified'

    def __post_init__(self):
        if self.kind not in ('Equity index', 'Share', 'ETF / Fund', 'FX', 'Commodity'):
            raise ValueError('Unsupported underlying type')
        if self.index_variant not in ('Price Return','Net Total Return','Gross Total Return'):
            raise ValueError('Invalid index variant')

def disclosure_blocks(profile, language):
    """Return (heading, paragraph) pairs specific to the reference asset."""
    fr=language=='FR'
    if profile.kind=='Equity index':
        blocks=[
            ('Index methodology and composition', 'Méthodologie et composition de l’indice',
             'The index sponsor may amend its methodology, eligibility criteria, weighting rules or constituent composition. Rebalancing, corporate actions and index adjustments can change the reference level and the note’s outcome.',
             'L’administrateur de l’indice peut modifier sa méthodologie, les critères d’éligibilité, les règles de pondération ou sa composition. Les rebalancements, opérations sur titres et ajustements peuvent modifier son niveau et le résultat de la note.'),
            ('Index publication and disruption', 'Publication et perturbation de l’indice',
             'Index levels may be delayed, corrected, suspended or discontinued. A real issuance would require contractual fallback and adjustment rules, including a calculation-agent process; no such fallback is implemented in this prototype.',
             'La publication de l’indice peut être retardée, corrigée, suspendue ou interrompue. Une émission réelle exigerait des règles contractuelles de substitution et d’ajustement ainsi qu’une procédure d’agent de calcul ; aucun mécanisme de ce type n’est implémenté ici.'),
            ('Index return convention and dividends', 'Convention de rendement et dividendes',
             f'The selected reference is described as a {profile.index_variant} index. Price-return indices generally exclude reinvested constituent dividends, whereas total-return variants incorporate dividends according to their methodology. The investor does not own the index constituents or receive their dividends directly.',
             f'La référence est décrite comme un indice {profile.index_variant}. Les indices Price Return ne réinvestissent généralement pas les dividendes, contrairement aux variantes Total Return selon leur méthodologie. L’investisseur ne détient pas les actions composant l’indice et ne perçoit pas directement leurs dividendes.'),
            ('Index concentration and exposure', 'Concentration et exposition à l’indice',
             'An index can be concentrated in particular sectors, countries or issuers. Diversification within an index does not protect against a broad market decline or the loss of principal under this payoff.',
             'Un indice peut présenter une concentration sectorielle, géographique ou par émetteur. La diversification interne ne protège pas contre une baisse généralisée du marché ni contre la perte en capital prévue par ce payoff.'),
        ]
    elif profile.kind=='Share':
        blocks=[
            ('Corporate actions and adjustment events', 'Opérations sur titres et événements d’ajustement',
             'Stock splits, special dividends, rights issues, mergers, tender offers and other corporate actions can affect the share price. An actual note would require defined adjustment and extraordinary-event provisions.',
             'Les divisions d’actions, dividendes exceptionnels, émissions de droits, fusions, offres publiques et autres opérations sur titres peuvent affecter le cours. Une note réelle nécessiterait des dispositions d’ajustement et d’événements extraordinaires.'),
            ('Trading suspension and delisting', 'Suspension de cotation et radiation',
             'Trading halts, delisting, exchange closure or insufficient liquidity may prevent a normal fixing and impair valuation or hedging. Contractual disruption and fallback procedures would be required.',
             'Les suspensions, radiations, fermetures de marché ou une liquidité insuffisante peuvent empêcher une constatation normale et affecter la valorisation ou la couverture. Des règles contractuelles de perturbation et de substitution seraient nécessaires.'),
            ('Dividends and ownership', 'Dividendes et détention',
             'The investor does not hold the underlying shares and has no voting rights or entitlement to dividends. Expected dividend assumptions influence the indicative valuation.',
             'L’investisseur ne détient pas les actions sous-jacentes et ne bénéficie ni de droits de vote ni de droits aux dividendes. Les hypothèses de dividendes attendus influencent la valorisation indicative.'),
            ('Single-name concentration', 'Concentration sur un émetteur',
             'The note is linked to a single company: adverse company-specific developments can cause a sharp decline and a substantial loss of principal.',
             'La note est exposée à une seule société : des événements défavorables propres à celle-ci peuvent provoquer une forte baisse et une perte importante du capital.'),
        ]
    else:
        from documentation.multi_termsheet import underlying_risks
        paragraphs=underlying_risks(profile.kind,language)
        return [(('Reference-market and disruption risks' if not fr else 'Risques de marché et de perturbation'),paragraphs[0]), (('Additional reference-specific risks' if not fr else 'Autres risques propres à la référence'),paragraphs[1])]
    return [(a if not fr else b, c if not fr else d) for a,b,c,d in blocks]
