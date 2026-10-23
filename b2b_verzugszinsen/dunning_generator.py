"""
b2b_verzugszinsen.dunning_generator
==================================
Generierung von rechtlich und kaufmännisch fundierten 3-stufigen Mahnschreiben
für Deutschland (§ 288 BGB), Österreich (§ 456, 458 UGB) und Schweiz (Art. 104 OR / Art. 67 SchKG).

Die 3 Mahnstufen:
1. ZAHLUNGSERINNERUNG:
   - Freundlicher, professioneller Ton
   - Prüfungsbitte, keine Eskalation
   - Keine Mahngebühr, Zinsen rein informativ
2. 1. MAHNUNG:
   - Förmliche Aufforderung mit Verzugseintritt
   - Geltendmachung der taggenauen Verzugszinsen
   - Gesetzliche 40-€-Schadenspauschale (§ 288 Abs. 5 BGB / § 458 UGB)
3. 2. MAHNUNG / BETREIBUNGSANKÜNDIGUNG:
   - Letzte außergerichtliche Frist (3-5 Tage)
   - Deutschland / Österreich: Ankündigung des gerichtlichen Mahnverfahrens / Mahnbescheid
   - Schweiz: Betreibungsankündigung gemäß Art. 67 SchKG beim Betreibungsamt

HINWEIS GEMÄSS § 2 RDG / ART. 404 OR:
Reine mathematische und kaufmännische Berechnungshilfe. Keine Rechtsberatung!
Online-Live-Rechner: https://dach-digitalwerk.netlify.app/mahnung-verzugszinsen-rechner/
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

from .interest_calculator import (
    Jurisdiction,
    DebtorType,
    InterestCalculationResult,
    calculate_interest,
)


class DunningLevel(int, Enum):
    """Mahnstufen."""
    PAYMENT_REMINDER = 1      # Zahlungserinnerung
    FIRST_DUNNING = 2         # 1. Mahnung (mit Zinsen & Pauschale)
    FINAL_DUNNING = 3         # 2. Mahnung / Betreibungsankündigung (SchKG / Mahnbescheid)


@dataclass
class DunningParty:
    """Angaben zu Gläubiger oder Schuldner."""
    company_name: str
    contact_person: Optional[str] = None
    street: str = ""
    postal_code: str = ""
    city: str = ""
    country: str = "Deutschland"
    email: Optional[str] = None
    iban: Optional[str] = None
    bic: Optional[str] = None
    bank_name: Optional[str] = None


@dataclass
class DunningLetter:
    """Repräsentiert ein strukturiertes Mahnschreiben."""
    level: DunningLevel
    creditor: DunningParty
    debtor: DunningParty
    invoice_number: str
    invoice_date: datetime.date
    due_date: datetime.date
    letter_date: datetime.date
    calculation: InterestCalculationResult
    deadline_days: int = 7
    custom_reference: Optional[str] = None

    @property
    def currency(self) -> str:
        return "CHF" if self.calculation.jurisdiction == Jurisdiction.CH else "EUR"

    @property
    def payment_deadline(self) -> datetime.date:
        return self.letter_date + datetime.timedelta(days=self.deadline_days)

    @property
    def subject(self) -> str:
        if self.level == DunningLevel.PAYMENT_REMINDER:
            return f"Zahlungserinnerung zu Rechnung Nr. {self.invoice_number}"
        elif self.level == DunningLevel.FIRST_DUNNING:
            return f"1. Mahnung zu Rechnung Nr. {self.invoice_number} (Verzug gemäß {self._get_short_statute()})"
        else:
            if self.calculation.jurisdiction == Jurisdiction.CH:
                return f"LETZTE MAHNUNG & BETREIBUNGSANKÜNDIGUNG (Art. 67 SchKG) - Rechnung {self.invoice_number}"
            else:
                return f"LETZTE MAHNUNG vor gerichtlichem Mahnverfahren - Rechnung {self.invoice_number}"

    def _get_short_statute(self) -> str:
        if self.calculation.jurisdiction == Jurisdiction.DE:
            return "§ 288 BGB"
        elif self.calculation.jurisdiction == Jurisdiction.AT:
            return "§ 456, 458 UGB"
        else:
            return "Art. 104 OR"

    def to_text(self) -> str:
        """Erzeugt das Mahnschreiben als sauberen Plain-Text."""
        curr = self.currency
        deadline_str = self.payment_deadline.strftime("%d.%m.%Y")
        letter_date_str = self.letter_date.strftime("%d.%m.%Y")
        invoice_date_str = self.invoice_date.strftime("%d.%m.%Y")
        due_date_str = self.due_date.strftime("%d.%m.%Y")

        cred = self.creditor
        deb = self.debtor

        lines = []
        # Absenderzeile
        lines.append(f"{cred.company_name} | {cred.street} | {cred.postal_code} {cred.city}")
        lines.append("")
        # Empfänger
        lines.append(deb.company_name)
        if deb.contact_person:
            lines.append(f"z. Hd. {deb.contact_person}")
        lines.append(deb.street)
        lines.append(f"{deb.postal_code} {deb.city}")
        lines.append(deb.country)
        lines.append("")
        lines.append(f"Datum: {letter_date_str}")
        lines.append("")
        lines.append(f"BETREFF: {self.subject}")
        lines.append("=" * len(f"BETREFF: {self.subject}"))
        lines.append("")

        salutation = f"Sehr geehrte Damen und Herren,"
        if deb.contact_person:
            salutation = f"Sehr geehrte(r) Herr/Frau {deb.contact_person},"
        lines.append(salutation)
        lines.append("")

        if self.level == DunningLevel.PAYMENT_REMINDER:
            lines.append(
                f"bei Durchsicht unserer Buchhaltung haben wir festgestellt, dass unsere Rechnung Nr. {self.invoice_number} "
                f"vom {invoice_date_str} mit Fälligkeit zum {due_date_str} noch nicht beglichen wurde."
            )
            lines.append(
                "Sicherlich handelt es sich hierbei nur um ein vorübergehendes Versehen in Ihrem Hause."
            )
            lines.append("")
            lines.append(
                f"Wir bitten Sie daher höflich, den offenen Rechnungsbetrag von {self.calculation.principal:,.2f} {curr} "
                f"bis zum {deadline_str} auf das unten angegebene Geschäftskonto zu überweisen."
            )
            lines.append("")
            lines.append("Sollten Sie die Überweisung bereits vorgenommen haben, betrachten Sie dieses Schreiben bitte als gegenstandslos.")

        elif self.level == DunningLevel.FIRST_DUNNING:
            lines.append(
                f"auf unsere vorangegangene Mitteilung zu Rechnung Nr. {self.invoice_number} vom {invoice_date_str} "
                f"(Fälligkeit: {due_date_str}) konnten wir leider noch keinen Zahlungseingang verbuchen."
            )
            lines.append(
                f"Ihr Unternehmen befindet sich seit dem {(self.due_date + datetime.timedelta(days=1)).strftime('%d.%m.%Y')} "
                f"gemäß {self.calculation.statutory_basis} im Verzug ({self.calculation.days_overdue} Verzugstage)."
            )
            lines.append("")
            lines.append("Forderungsaufstellung:")
            lines.append(f"  - Hauptforderung:                             {self.calculation.principal:,.2f} {curr}")
            lines.append(f"  - Verzugszinsen ({self.calculation.effective_rate_percent:.2f} % p.a. taggenau): {self.calculation.accrued_interest:,.2f} {curr}")
            if self.calculation.flat_fee > 0:
                fee_statute = "§ 288 Abs. 5 BGB" if self.calculation.jurisdiction == Jurisdiction.DE else "§ 458 UGB"
                lines.append(f"  - Gesetzliche Schadenspauschale ({fee_statute}): {self.calculation.flat_fee:,.2f} {curr}")
            lines.append(f"  -------------------------------------------------------------")
            lines.append(f"  OFFENE GESAMTFORDRUNG:                        {self.calculation.total_due:,.2f} {curr}")
            lines.append("")
            lines.append(
                f"Bitte überweisen Sie den fälligen Gesamtbetrag von {self.calculation.total_due:,.2f} {curr} "
                f"spätestens bis zum {deadline_str}."
            )

        else:  # FINAL_DUNNING
            lines.append(
                f"trotz Mahnung und Nachfristsetzung ist der Ausgleich unserer Rechnung Nr. {self.invoice_number} "
                f"vom {invoice_date_str} bis heute nicht erfolgt."
            )
            lines.append("")
            lines.append("Aktuelle Forderungsaufstellung per heute:")
            lines.append(f"  - Hauptforderung:                             {self.calculation.principal:,.2f} {curr}")
            lines.append(f"  - Verzugszinsen ({self.calculation.effective_rate_percent:.2f} % p.a. taggenau): {self.calculation.accrued_interest:,.2f} {curr}")
            if self.calculation.flat_fee > 0:
                lines.append(f"  - Gesetzliche Schadenspauschale:              {self.calculation.flat_fee:,.2f} {curr}")
            lines.append(f"  -------------------------------------------------------------")
            lines.append(f"  GESAMTFORDERUNG:                              {self.calculation.total_due:,.2f} {curr}")
            lines.append("")

            if self.calculation.jurisdiction == Jurisdiction.CH:
                lines.append(
                    f"DIES IST UNSERE LETZTE AUSSERGERICHTLICHE MAHNUNG (BETREIBUNGSANKÜNDIGUNG GEMÄSS ART. 67 SchKG)."
                )
                lines.append(
                    f"Wir fordern Sie letztmalig auf, den Gesamtbetrag von {self.calculation.total_due:,.2f} {curr} "
                    f"strikt bis zum {deadline_str} (Zahlungseingang) zu begleichen."
                )
                lines.append(
                    "Sollte die Zahlung nicht fristgerecht eintreffen, werden wir ohne weitere Ankündigung "
                    "das Betreibungsbegehren beim zuständigen Betreibungsamt Ihres Sitzes einreichen. "
                    "Sämtliche hierdurch entstehenden Amts- und Verfahrenskosten gehen zu Ihren Lasten."
                )
            else:
                lines.append(
                    f"DIES IST DIE LETZTE AUSSERGERICHTLICHE ZAHLUNGSAUFFORDERUNG."
                )
                lines.append(
                    f"Wir fordern Sie auf, den Betrag von {self.calculation.total_due:,.2f} {curr} "
                    f"unverzüglich, spätestens bis zum {deadline_str}, auf unser Bankkonto zu überweisen."
                )
                lines.append(
                    "Nach fruchtlosem Ablauf dieser letzten Frist werden wir unverzüglich und ohne weitere Vorwarnung "
                    "einen gerichtlichen Mahnbescheid beantragen bzw. die Angelegenheit unserer Rechtsabteilung / "
                    "einem Inkassodienstleister zur Titulierung und Zwangsvollstreckung übergeben. "
                    "Die dadurch entstehenden beträchtlichen Mehrkosten haben Sie als Verzugsschaden vollumfänglich zu tragen."
                )

        lines.append("")
        lines.append("Bankverbindung:")
        lines.append(f"  Kontoinhaber: {cred.company_name}")
        if cred.bank_name:
            lines.append(f"  Kreditinstitut: {cred.bank_name}")
        if cred.iban:
            lines.append(f"  IBAN: {cred.iban}")
        if cred.bic:
            lines.append(f"  BIC: {cred.bic}")
        lines.append(f"  Verwendungszweck: {self.invoice_number} / {deb.company_name}")
        lines.append("")
        lines.append("Mit freundlichen Grüßen,")
        lines.append(f"{cred.company_name}")
        if cred.contact_person:
            lines.append(cred.contact_person)
        lines.append("")
        lines.append("--------------------------------------------------------------------------------")
        lines.append("Hinweis gemäß § 2 RDG / Art. 404 OR: Reine Zinsmathematik & kaufmännische Berechnungshilfe.")
        lines.append("Erstellt mit DACH Digitalwerk Verzugszinsen-Engine:")
        lines.append("Online-Rechner: https://dach-digitalwerk.netlify.app/mahnung-verzugszinsen-rechner/")
        return "\n".join(lines)

    def to_markdown(self) -> str:
        """Erzeugt das Mahnschreiben als formatiertes Markdown."""
        text = self.to_text()
        return f"```text\n{text}\n```"


def create_dunning_letter(
    level: Union[DunningLevel, int],
    creditor_name: str,
    debtor_name: str,
    invoice_number: str,
    principal: float,
    due_date: Union[datetime.date, str],
    calculation_date: Optional[Union[datetime.date, str]] = None,
    letter_date: Optional[Union[datetime.date, str]] = None,
    jurisdiction: Union[Jurisdiction, str] = Jurisdiction.DE,
    debtor_type: Union[DebtorType, str] = DebtorType.B2B,
    creditor_iban: Optional[str] = None,
    creditor_bic: Optional[str] = None,
    creditor_bank: Optional[str] = None,
    creditor_street: str = "",
    creditor_city: str = "",
    debtor_street: str = "",
    debtor_city: str = "",
    deadline_days: int = 7,
    custom_base_rate: Optional[float] = None,
) -> DunningLetter:
    """
    Hilfsfunktion zur komfortablen Erstellung eines Mahnschreibens mit automatischer Zinsberechnung.
    """
    if isinstance(level, int):
        level = DunningLevel(level)
    if isinstance(due_date, str):
        due_date = datetime.date.fromisoformat(due_date)
    if letter_date is None:
        letter_date = datetime.date.today()
    elif isinstance(letter_date, str):
        letter_date = datetime.date.fromisoformat(letter_date)

    calc_date = calculation_date if calculation_date is not None else letter_date

    # Include flat fee only for level 2 and 3 if B2B
    include_flat = (level != DunningLevel.PAYMENT_REMINDER)

    calc_res = calculate_interest(
        principal=principal,
        due_date=due_date,
        calculation_date=calc_date,
        jurisdiction=jurisdiction,
        debtor_type=debtor_type,
        custom_base_rate=custom_base_rate,
        include_flat_fee=include_flat,
    )

    creditor = DunningParty(
        company_name=creditor_name,
        street=creditor_street,
        city=creditor_city,
        iban=creditor_iban,
        bic=creditor_bic,
        bank_name=creditor_bank,
    )

    debtor = DunningParty(
        company_name=debtor_name,
        street=debtor_street,
        city=debtor_city,
    )

    return DunningLetter(
        level=level,
        creditor=creditor,
        debtor=debtor,
        invoice_number=invoice_number,
        invoice_date=due_date - datetime.timedelta(days=14),  # typisches Rechnungsdatum 14 Tage vor Fälligkeit
        due_date=due_date,
        letter_date=letter_date,
        calculation=calc_res,
        deadline_days=deadline_days,
    )
