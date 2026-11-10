# Sample Output: SOP + Training Packet

*Illustrative only, using a fictional operator ("Example Cannabis Distribution," a licensed wholesale distributor) to demonstrate the output shape. Not a real SOP; the specific numbers and citations below are placeholders and must be confirmed against actual state requirements before use.*

---

## Phase 1 output: the SOP

**SOP Title:** Outbound Wholesale Order Fulfillment and Manifest Verification
**SOP ID:** WHS-002
**License Type and Number:** Wholesale Distribution, placeholder state license #
**Effective Date:** 2026-08-24
**Last Reviewed:** 2026-08-24
**Next Review Date:** 2027-02-24 (6 months; flagged as high-risk area, see Phase 3 logic)
**Document Owner (role):** Warehouse Operations Manager
**Version:** 1.0
**Revision History:** 1.0, 2026-08-24, initial version
**Approvals:** Warehouse Operations Manager, Compliance Lead

### 1. Purpose

Ensure every outbound wholesale order is picked accurately, verified against the sales order, and accompanied by a matching METRC transfer manifest before it leaves the facility.

### 2. Scope

Applies to: warehouse pickers, warehouse leads, and compliance/inventory staff at Example Cannabis Distribution's licensed wholesale facility. Out of scope: retail point-of-sale transactions and direct-to-consumer delivery, covered in separate SOPs.

### 3. Regulatory References

State track-and-trace requirements for licensee-to-licensee transfers (METRC or state equivalent manifest rules), and any state requirement that a physical or digital manifest accompany the transport vehicle (confirm exact statute/rule citation with compliance counsel; not populated here since none was supplied).

### 4. Definitions

**Manifest**: the METRC-generated transfer document listing every item, quantity, and weight in a shipment. **Pick discrepancy**: any mismatch between the sales order and what's physically picked.

### 5. Roles and Responsibilities

- Executes the pick: Warehouse Picker
- Verifies the pick against the sales order: Warehouse Lead (a different person than the picker)
- Finalizes and signs the METRC manifest: Compliance/Inventory Manager
- Confirms carrier/driver handoff: Warehouse Lead

The person who picks the order is never the person who verifies it or finalizes the manifest. Three distinct roles touch every outbound shipment.

### 6. Step-by-Step Procedure

**Step 1: Pull the sales order**
1. Open the confirmed sales order in the order management system.

**What you should see:** A list of SKUs, quantities, and the receiving licensee's information.

**Step 2: Pick the order**
1. Pick each item listed on the sales order from its assigned inventory location.
2. Record the actual picked quantity and weight for each item.

**Warning:** Do not substitute a different batch or SKU without a documented order change first.

**Step 3: Verify the pick**
1. A second person, the Warehouse Lead, compares the picked items against the sales order, line by line.

**What you should see:** Picked quantities and weights matching the sales order exactly, or a documented discrepancy.

**Step 4: Generate and verify the METRC manifest**
1. Generate the transfer manifest in METRC using the verified pick.
2. Confirm every line item, quantity, and weight on the manifest matches the verified pick.

**Warning:** Never let a shipment leave without a manifest that matches what was actually picked. A mismatch here is a licensing violation, not just a paperwork error.

**Step 5: Hand off to the carrier or driver**
1. Confirm the driver has a copy of the manifest (physical or digital, per state requirement).
2. Record the departure time and driver name on the shipping log.

**What you should see:** Signed acknowledgment from the driver.

**Step 6: Confirm delivery and close the order**
1. On confirmation of delivery, record the proof of delivery in the order system.
2. Trigger the invoice.

### 7. Controls, Thresholds, and Variance Handling

- Reconciliation cadence: every outbound order, before it leaves the facility
- Variance threshold: zero tolerance on unit count (operator's rule). Weight variance threshold: CONFIRM: [state rule or the scale's certified tolerance]. Until it's confirmed, any weight mismatch holds the shipment. Any unit-count mismatch, or a weight variance beyond the confirmed threshold, holds the shipment until resolved.
- Escalation protocol: Warehouse Lead notifies the Compliance/Inventory Manager immediately; the shipment does not leave until the discrepancy is resolved and documented
- Documentation: discrepancy log, filed with the order record

### 8. Records and Retention

- Records produced: verified pick sheet, METRC manifest, shipping log, proof of delivery
- Stored: order management system and METRC
- Retention: CONFIRM: retention period for transfer records in [state]
- Access: Warehouse Operations Manager and Compliance Lead; pickers can view but not alter finalized records

### 9. Training Requirements

- Roles requiring training: all warehouse pickers, warehouse leads, compliance/inventory staff
- Method: practical demonstration (shadow a full outbound order end to end), followed by a written comprehension check
- Retraining cadence: at each scheduled review (every 6 months), and before any revised version of this SOP takes effect or after a METRC platform change
- Records kept in: employee training log (see Phase 2 output below)

### 10. Review and Revision

- Next scheduled review: 2027-02-24
- Immediate review triggers: any manifest or inventory discrepancy pattern, a state track-and-trace rule change, or a change in the order/METRC system

---

## Phase 2 output: the training packet

### Quick-reference summary (post near the pick station)

1. Pull the sales order.
2. Pick each item and record the actual quantity and weight.
3. Have a second person verify the pick against the order.
4. Generate the METRC manifest and check it matches the verified pick exactly.
5. Confirm the driver has the manifest before the truck leaves.
6. Record delivery confirmation and trigger the invoice.
7. Never let a shipment leave without a manifest that matches what was picked.

### Comprehension check

1. **(Critical)** (True/False) It's fine for the same person to pick the order and verify it, as long as they're careful.
2. **(Critical)** What must the manifest match exactly before a shipment can leave?
3. **(Critical)** (Multiple choice) The picked weight comes in 2% under the sales order. You should: (a) round up on the manifest to match the order, (b) ship it anyway since it's close, (c) hold the shipment and notify the Compliance/Inventory Manager, (d) fix it after the truck leaves.
4. Who finalizes and signs the METRC manifest?
5. (Short answer) Why does the driver need a copy of the manifest before leaving?

### Answer key (for the trainer only)

1. False. A second person verifies the pick (Section 5, segregation of duties; Section 6, step 3).
2. The verified pick: every package, quantity and weight (Section 6, step 4).
3. (c). Any mismatch holds the shipment until the Compliance/Inventory Manager resolves it (Section 7).
4. The Compliance/Inventory Manager (Section 5).
5. So the load is documented while it's on the road and matches what was picked (Section 6, step 5). Accept any answer that says the shipment must travel with a matching manifest.

### Pass rule

Pass: questions 1, 2 and 3 all correct, and at least 4 of 5 correct overall. Otherwise the trainer reviews the missed steps with the employee, who retakes the check before picking or verifying orders unsupervised. Record each attempt in the log below.

### Sign-off / attestation log template

| Employee | Role | Date Trained | Method | Trainer | Score | Result (Pass / Retrain and retest) | Retest Date | Signature |
|---|---|---|---|---|---|---|---|---|
| | Warehouse Picker | | Shadow + written check | | | | | |
| | Warehouse Lead | | Shadow + written check | | | | | |
| | Compliance/Inventory Manager | | Shadow + written check | | | | | |

### Retraining trigger

Retrain at this SOP's next scheduled review (2027-02-24), and before any revised version takes effect or after a METRC platform change.

---

## Phase 3 output: review cadence

This SOP touches inventory accuracy and licensee-to-licensee transfer compliance, both high-risk areas, so it's set to a 6-month review cycle rather than the standard 12-month default, with the trigger events listed in Section 10 forcing an earlier review regardless of schedule.
