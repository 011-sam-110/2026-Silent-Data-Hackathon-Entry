"""Generate three test transaction PDFs for compliance engine testing.

Creates:
  test_data/LOW_RISK_Crown_Office_Supplies.pdf   - clean domestic payment
  test_data/MEDIUM_RISK_Savannah_AgriTech.pdf     - elevated flags, review
  test_data/HIGH_RISK_Petrov_Industrial.pdf        - stacked red flags, reject
"""

from pathlib import Path
from fpdf import FPDF

OUT = Path(__file__).resolve().parent.parent / "test_data"
OUT.mkdir(exist_ok=True)


def _make_pdf(filename: str, lines: list[tuple[str, str]]) -> None:
    """Create a single-page PDF from (style, text) pairs.

    style is one of: 'H' (heading), 'S' (subheading), 'B' (body),
    'D' (divider), 'N' (note/small).
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(25, 25, 25)

    for style, text in lines:
        if style == "D":
            pdf.set_draw_color(180, 180, 180)
            pdf.line(25, pdf.get_y(), 185, pdf.get_y())
            pdf.ln(4)
        elif style == "H":
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(20, 20, 60)
            pdf.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
        elif style == "S":
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(60, 60, 60)
            pdf.cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        elif style == "N":
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(100, 100, 100)
            pdf.multi_cell(0, 5, text)
            pdf.ln(2)
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 5.5, text)
            pdf.ln(1)

    path = OUT / filename
    pdf.output(str(path))
    print(f"  Created: {path}")


# =====================================================================
# 1. LOW RISK  - clean domestic invoice payment
#    Expected: score ~8, decision: approve
#    Triggers: vague_details_flag = False (has "invoice", "purchase order")
#              No urgency, no risky countries, amount < threshold
# =====================================================================
_make_pdf("LOW_RISK_Crown_Office_Supplies.pdf", [
    ("H", "TRANSACTION CONFIRMATION"),
    ("D", ""),
    ("S", "Reference: TXN-2026-041401"),
    ("S", "Date: 14 April 2026"),
    ("S", "Value Date: 15 April 2026"),
    ("D", ""),
    ("S", "ORIGINATOR"),
    ("B", "Meridian Holdings Ltd"),
    ("B", "Account: GB82 WEST 1234 5698 90"),
    ("B", "15 Bishopsgate, London EC2N 3AR, United Kingdom"),
    ("B", ""),
    ("S", "BENEFICIARY"),
    ("B", "Crown Office Supplies Ltd"),
    ("B", "Account: GB29 NWBK 6016 1331 9268"),
    ("B", "Sort Code: 60-16-13"),
    ("B", "42 High Street, Manchester M1 4BT, United Kingdom"),
    ("D", ""),
    ("S", "PAYMENT DETAILS"),
    ("B", "Amount: GBP 4,850.00"),
    ("B", "Currency: British Pound Sterling"),
    ("B", "Payment Method: Faster Payment (FPS)"),
    ("B", ""),
    ("S", "PURPOSE OF PAYMENT"),
    ("B", "Payment for invoice INV-2026-0387 covering Q1 2026 office "
          "supplies and stationery as per purchase order PO-2024-112. "
          "Delivery of goods completed and confirmed received on "
          "28 March 2026. Payment within standard 30-day terms."),
    ("B", ""),
    ("S", "AUTHORISATION"),
    ("B", "Approved by: Sarah Chen, Senior Accounts Payable"),
    ("B", "Reviewed by: J. Whitmore, Finance Director"),
    ("B", "Signature: Verified against specimen on file"),
    ("D", ""),
    ("N", "This payment has been processed in accordance with internal "
          "controls and complies with all applicable regulations. "
          "Dual authorisation obtained as per company policy for "
          "payments exceeding GBP 1,000."),
])


# =====================================================================
# 2. MEDIUM RISK  - overseas project payment with urgency + high amount
#    Expected: score ~38, decision: review
#    Triggers: high_amount_flag (+18), medium_risk_country (+8),
#              urgency_flag (+12)
# =====================================================================
_make_pdf("MEDIUM_RISK_Savannah_AgriTech.pdf", [
    ("H", "INTERNATIONAL WIRE TRANSFER REQUEST"),
    ("D", ""),
    ("S", "Reference: WT-2026-04-0892"),
    ("S", "Date: 14 April 2026"),
    ("S", "Priority: Standard"),
    ("D", ""),
    ("S", "ORIGINATOR"),
    ("B", "Hartfield Ventures PLC"),
    ("B", "Account: GB15 HSBC 4012 3456 7890"),
    ("B", "One Canada Square, Canary Wharf, London E14 5AB"),
    ("B", ""),
    ("S", "BENEFICIARY"),
    ("B", "Savannah AgriTech Solutions Ltd"),
    ("B", "SWIFT/BIC: ABORKENAXXX"),
    ("B", "Account: KE02 0200 0056 0012 3456 789"),
    ("B", "Kenyatta Avenue, Nairobi, Kenya"),
    ("D", ""),
    ("S", "PAYMENT DETAILS"),
    ("B", "Amount: USD 62,000.00"),
    ("B", "Currency: United States Dollar"),
    ("B", "Charges: OUR (all charges borne by originator)"),
    ("B", ""),
    ("S", "PURPOSE OF PAYMENT"),
    ("B", "Project funding for agricultural technology deployment in "
          "Kenya. Payment covers Phase 2 equipment procurement and "
          "local contractor retainer per vendor agreement dated "
          "8 February 2026. Equipment includes irrigation monitoring "
          "sensors and satellite uplink hardware for 12 farm sites "
          "across the Central Highlands region."),
    ("B", ""),
    ("S", "ADDITIONAL NOTES"),
    ("B", "This transfer must be processed today as the supplier has "
          "indicated a firm deadline for bulk purchase rates. The "
          "current pricing is only available within an expedited "
          "timeline and represents a time sensitive opportunity to "
          "secure equipment before costs increase in Q2 2026. Failure "
          "to remit funds within the closing window may result in a "
          "15% price increase per the supplier's revised schedule."),
    ("B", ""),
    ("S", "AUTHORISATION"),
    ("B", "Requested by: James Hartfield, Managing Director"),
    ("B", "Compliance pre-check: Completed - standard KYC on file"),
    ("B", "Signature: Verified against specimen on file"),
    ("D", ""),
    ("N", "This transaction has been flagged for standard enhanced due "
          "diligence review given the destination jurisdiction and "
          "transaction value. All supporting documentation is on file "
          "with the compliance department."),
])


# =====================================================================
# 3. HIGH RISK  - offshore transfer with stacked red flags
#    Expected: score 100 (capped), decision: reject
#    Triggers: signature_fail (+20), high_risk_country (+18),
#              high_amount (+18), urgency (+12), vague_details (+8),
#              recipient_out_of_pattern (+14), exit_risk medium (+10)
#    NOTE: upload this with the "Signature verified" checkbox UNCHECKED
# =====================================================================
_make_pdf("HIGH_RISK_Petrov_Industrial.pdf", [
    ("H", "URGENT WIRE TRANSFER - PRIORITY ONE"),
    ("D", ""),
    ("S", "Reference: WT-EMRG-2026-0041"),
    ("S", "Date: 14 April 2026"),
    ("S", "Priority: IMMEDIATE"),
    ("D", ""),
    ("S", "ORIGINATOR"),
    ("B", "Nexus Offshore Holdings"),
    ("B", "Registered: Road Town, Tortola, British Virgin Islands"),
    ("B", "Account: VG12 3456 7890 1234 5678"),
    ("B", ""),
    ("S", "BENEFICIARY"),
    ("B", "New recipient - Petrov Industrial Group OOO"),
    ("B", "SWIFT/BIC: SABRRUMM"),
    ("B", "Account: RU04 0000 0000 0000 0000 0000"),
    ("B", "Presnenskaya Naberezhnaya 12, Moscow, Russia"),
    ("D", ""),
    ("S", "PAYMENT DETAILS"),
    ("B", "Amount: USD 340,000.00"),
    ("B", "Currency: United States Dollar"),
    ("B", "Charges: SHA"),
    ("B", ""),
    ("S", "PURPOSE OF PAYMENT"),
    ("B", "Business matter - miscellaneous operational support and "
          "general payment for project-related services. Execute "
          "immediately. Funds must arrive today without delay."),
    ("B", ""),
    ("S", "INSTRUCTIONS"),
    ("B", "Risk-off mandate: Strategic repositioning requires swift "
          "execution and aggressive expansion into new territory. "
          "Act now to capitalize today on this time-sensitive entry "
          "before the closing window. Scale instantly to seize the "
          "window and capture momentum."),
    ("B", ""),
    ("B", "Do not hold for standard compliance review. This transfer "
          "has been pre-approved at board level and must be processed "
          "immediately as a priority one matter."),
    ("B", ""),
    ("S", "AUTHORISATION"),
    ("B", "Requested by: D. Volkov, Director"),
    ("B", "Signature: UNVERIFIED - specimen mismatch noted"),
    ("D", ""),
    ("N", "WARNING: This transaction has not completed standard "
          "enhanced due diligence procedures. Beneficiary is not in "
          "the approved counterparty register. Signature verification "
          "pending."),
])

print("\nDone. Upload these to the app to test each risk level.")
print("NOTE: For HIGH_RISK, uncheck 'Signature verified' before running.")
