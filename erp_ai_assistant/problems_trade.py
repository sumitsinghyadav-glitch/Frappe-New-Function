"""Troubleshooting entries for Buying and Selling problems in ERPNext v16 (offline Help Guide)."""

PROBLEMS = [
	{
		"id": "item-rate-zero-price-not-fetched",
		"title": "Item rate is zero or the price is not fetched",
		"errors": [
			"rate is zero",
			"rate not fetched",
			"price not coming",
			"item price not found",
			"price list rate is 0",
			"price list not found",
			"price list is disabled or does not exist",
		],
		"tags": "rate zero price missing item price price list selling buying rate nahi aa raha rate 0 daam keemat kaise set kare",
		"doctypes": ["Item Price", "Price List", "Selling Settings", "Buying Settings", "Sales Order", "Purchase Order"],
		"cause": "ERPNext fetches the rate from an Item Price record for the selected Price List. If no Item Price exists for that item, price list, UOM and currency, or the Price List is disabled, the rate stays zero.",
		"solution": (
			"1. Open the document and note the **Price List** in the **Currency and Price List** section.\n"
			"2. Open [Item Price](/app/item-price) and check that a record exists for the item with that **Price List**, the same **UOM** and the same currency.\n"
			"3. If it is missing, create one with [new Item Price](/app/item-price/new).\n"
			"4. Open [Price List](/app/price-list) and confirm the list is enabled and marked **Selling** or **Buying** as needed.\n"
			"5. Set defaults on the **Pricing** tab: **Default Price List** in [Selling Settings](/app/selling-settings) and **Default Buying Price List** in [Buying Settings](/app/buying-settings). You can also tick **Use prices from Default Price List as fallback** in Selling Settings.\n"
			"6. Remove and re-add the item row so the rate is fetched again.\n\n"
			"**Check:** The **Price List Rate** and **Rate** columns show the expected value. The report [Item-wise Price List Rate](/app/query-report/Item-wise Price List Rate) also lists all prices."
		),
	},
	{
		"id": "pricing-rule-not-applied",
		"title": "Pricing Rule or discount is not applied",
		"errors": [
			"pricing rule not applied",
			"discount not applied",
			"scheme not working",
			"multiple price rules exists with same criteria",
			"please resolve conflict by assigning priority",
		],
		"tags": "pricing rule discount scheme offer promotional not applied not working priority conflict discount nahi lag raha chhoot",
		"doctypes": ["Pricing Rule", "Promotional Scheme", "Sales Order", "Sales Invoice", "Purchase Order"],
		"cause": "A Pricing Rule applies only when every condition matches: Selling or Buying, company, dates, item or group, party, and minimum quantity. It is skipped if the document has **Ignore Pricing Rule** ticked, and it raises an error when two rules match with the same priority.",
		"solution": (
			"1. Open the rule in [Pricing Rule](/app/pricing-rule) and confirm **Disable** is not ticked.\n"
			"2. Confirm **Selling** or **Buying** is ticked for the right side, and **Company** matches.\n"
			"3. Check **Apply On** (Item Code, Item Group, Brand or Transaction) and that your item is listed.\n"
			"4. Check **Applicable For** (Customer, Customer Group, Territory, Supplier and so on) matches the party.\n"
			"5. Check **Valid From**, **Valid Up To** and **Min Qty (As Per Stock UOM)** against the document date and quantity.\n"
			"6. On the document, make sure **Ignore Pricing Rule** is not ticked.\n"
			"7. If two rules match, tick **Has Priority** and set a different **Priority** on each, or tick **Apply Multiple Pricing Rules**.\n"
			"8. Re-enter the quantity on the item row to trigger the rule again.\n\n"
			"**Check:** The item row shows a value in **Pricing Rules** and the discount appears in **Discount (%) on Price List Rate with Margin** or **Rate**."
		),
	},
	{
		"id": "additional-discount-not-applied",
		"title": "Additional discount is not applied correctly",
		"errors": [
			"discount not reflecting",
			"additional discount not working",
			"discount applied on wrong amount",
			"discount amount cannot be greater than",
		],
		"tags": "additional discount percentage amount grand total net total apply discount on discount galat discount kam nahi hua",
		"doctypes": ["Sales Invoice", "Purchase Invoice", "Sales Order", "Purchase Order", "Quotation"],
		"cause": "The additional discount is calculated on either **Grand Total** or **Net Total**, as chosen in **Apply Additional Discount On**. Entering both a percentage and an amount, or choosing the wrong base, gives an unexpected result.",
		"solution": (
			"1. Scroll to the **Additional Discount** section of the document.\n"
			"2. Set **Apply Additional Discount On** to **Net Total** (before tax) or **Grand Total** (after tax).\n"
			"3. Enter only one of **Additional Discount Percentage** or **Additional Discount Amount**.\n"
			"4. For a discount on one item only, use **Discount (%) on Price List Rate with Margin** in the item row instead.\n"
			"5. Save the document again so totals are recalculated.\n\n"
			"**Check:** **Net Total**, **Total Taxes and Charges** and **Grand Total** match your expected figures."
		),
	},
	{
		"id": "customer-credit-limit-crossed",
		"title": "Customer credit limit has been crossed",
		"errors": [
			"credit limit has been crossed for customer",
			"credit limit crossed",
			"please contact your administrator to extend the credit limits",
			"overdue limit",
		],
		"tags": "credit limit crossed exceeded customer overdue sales order sales invoice delivery note bypass credit limit badhana udhaar limit",
		"doctypes": ["Customer", "Customer Group", "Accounts Settings", "Sales Order", "Sales Invoice"],
		"cause": "The customer's outstanding amount plus this document exceeds the **Credit Limit** set for the customer (or its Customer Group) for this company.",
		"solution": (
			"1. Check what the customer owes in [Accounts Receivable](/app/query-report/Accounts Receivable).\n"
			"2. Collect payment against old invoices with a [Payment Entry](/app/payment-entry/new), or\n"
			"3. Open the [Customer](/app/customer), go to the **Credit & Overdue Limits** table and raise **Credit Limit** for the company.\n"
			"4. To allow the Sales Order but check only at invoice time, tick **Bypass credit limit check at sales order** in the same row.\n"
			"5. To let a senior user approve such documents, set **Role allowed to bypass credit limit** on the **Credit Limits** tab of [Accounts Settings](/app/accounts-settings).\n\n"
			"**Check:** Submit the document again; it submits without the credit limit message."
		),
	},
	{
		"id": "over-billing-allowance-exceeded",
		"title": "Cannot overbill: over billing allowance exceeded",
		"errors": [
			"cannot overbill for item",
			"to allow over-billing, please set allowance in accounts settings",
			"over billing",
			"billed amount more than ordered",
		],
		"tags": "overbill over billing allowance invoice more than order amount rate higher extra billing zyada bill",
		"doctypes": ["Accounts Settings", "Item", "Sales Invoice", "Purchase Invoice"],
		"cause": "The invoice amount for an item is higher than the amount on the linked Sales Order, Purchase Order or receipt, and the difference is above the allowed percentage.",
		"solution": (
			"1. First confirm the rate on the invoice is correct. If the order rate was wrong, amend the order instead.\n"
			"2. To allow a margin for all items, set **Over Billing Allowance (%)** on the **Credit Limits** tab of [Accounts Settings](/app/accounts-settings).\n"
			"3. To allow it for one item only, set **Over Billing Allowance (%)** on the [Item](/app/item).\n"
			"4. To let a specific role bill above the limit, set **Role Allowed to over bill** on the same tab.\n\n"
			"**Check:** The invoice submits, and the order shows the correct **% Billed**."
		),
	},
	{
		"id": "purchase-order-required",
		"title": "Purchase Order is required before Purchase Receipt or Invoice",
		"errors": [
			"purchase order required",
			"purchase order is mandatory",
			"as per the buying settings if purchase order required",
			"user need to create purchase order first",
		],
		"tags": "purchase order required mandatory buying settings po required purchase receipt purchase invoice direct bina po ke",
		"doctypes": ["Buying Settings", "Purchase Order", "Purchase Receipt", "Purchase Invoice", "Supplier"],
		"cause": "In Buying Settings, **Is Purchase Order required for Purchase Invoice & Receipt creation?** is set to **Yes**, so receipts and invoices must be created from a Purchase Order.",
		"solution": (
			"1. Preferred: create a [Purchase Order](/app/purchase-order/new), submit it, then use **Create > Purchase Receipt** or **Create > Purchase Invoice**.\n"
			"2. To allow direct entries for everyone, open [Buying Settings](/app/buying-settings), **Transaction Settings** tab, and set **Is Purchase Order required for Purchase Invoice & Receipt creation?** to **No**.\n"
			"3. To exempt only one supplier, open the [Supplier](/app/supplier) and tick **Allow purchase invoice creation without purchase order**.\n\n"
			"**Check:** The Purchase Receipt or Invoice saves and submits without the message."
		),
	},
	{
		"id": "purchase-receipt-required",
		"title": "Purchase Receipt is required before Purchase Invoice",
		"errors": [
			"purchase receipt required",
			"purchase receipt is mandatory",
			"as per the buying settings if purchase reciept required",
			"user need to create purchase receipt first",
		],
		"tags": "purchase receipt required mandatory buying settings pr required grn purchase invoice bina receipt ke",
		"doctypes": ["Buying Settings", "Purchase Receipt", "Purchase Invoice", "Supplier"],
		"cause": "In Buying Settings, **Is Purchase Receipt required for Purchase Invoice creation?** is set to **Yes**, so a Purchase Invoice must be made from a Purchase Receipt.",
		"solution": (
			"1. Preferred: submit a [Purchase Receipt](/app/purchase-receipt/new), then use **Create > Purchase Invoice**.\n"
			"2. If the goods and the bill arrive together, set this setting to **No** (step 3) and tick **Update Stock** on the Purchase Invoice.\n"
			"3. To relax the rule, open [Buying Settings](/app/buying-settings), **Transaction Settings** tab, and set **Is Purchase Receipt required for Purchase Invoice creation?** to **No**.\n"
			"4. To exempt one supplier, tick **Allow purchase invoice creation without purchase receipt** on the [Supplier](/app/supplier).\n\n"
			"**Check:** The Purchase Invoice submits without the message."
		),
	},
	{
		"id": "sales-order-required",
		"title": "Sales Order is required before Delivery Note or Sales Invoice",
		"errors": [
			"sales order required for item",
			"sales order is mandatory",
			"as per selling settings sales order required",
		],
		"tags": "sales order required mandatory selling settings so required delivery note sales invoice direct bina order ke",
		"doctypes": ["Selling Settings", "Sales Order", "Delivery Note", "Sales Invoice", "Customer"],
		"cause": "In Selling Settings, **Is Sales Order required to create Sales Invoice/Delivery Note?** is set to **Yes**.",
		"solution": (
			"1. Preferred: create and submit a [Sales Order](/app/sales-order/new), then use **Create > Delivery Note** or **Create > Sales Invoice**.\n"
			"2. To allow direct entries, open [Selling Settings](/app/selling-settings), **Transaction** tab, and set **Is Sales Order required to create Sales Invoice/Delivery Note?** to **No**.\n"
			"3. To exempt one customer, open the [Customer](/app/customer) and tick **Allow sales invoice creation without sales order**.\n\n"
			"**Check:** The Delivery Note or Sales Invoice submits without the message."
		),
	},
	{
		"id": "delivery-note-required",
		"title": "Delivery Note is required before Sales Invoice",
		"errors": [
			"delivery note required for item",
			"delivery note is mandatory",
			"as per selling settings delivery note required",
		],
		"tags": "delivery note required mandatory selling settings dn required challan sales invoice bina challan ke",
		"doctypes": ["Selling Settings", "Delivery Note", "Sales Invoice", "Customer"],
		"cause": "In Selling Settings, **Is Delivery Note required to create Sales Invoice?** is set to **Yes**.",
		"solution": (
			"1. Preferred: submit a [Delivery Note](/app/delivery-note/new), then use **Create > Sales Invoice**.\n"
			"2. To relax the rule, open [Selling Settings](/app/selling-settings), **Transaction** tab, and set **Is Delivery Note required to create Sales Invoice?** to **No**. You can then tick **Update Stock** on the Sales Invoice.\n"
			"3. To exempt one customer, tick **Allow sales invoice creation without delivery note** on the [Customer](/app/customer).\n\n"
			"**Check:** The Sales Invoice submits without the message."
		),
	},
	{
		"id": "cannot-create-purchase-receipt-from-po",
		"title": "Cannot create Purchase Receipt from Purchase Order",
		"errors": [
			"purchase receipt button not showing",
			"create purchase receipt missing",
			"all items have already been received",
			"purchase order is not submitted",
			"purchase order is closed",
			"purchase order is on hold",
		],
		"tags": "purchase receipt create button missing po not submitted fully received closed on hold grn nahi ban raha maal receive",
		"doctypes": ["Purchase Order", "Purchase Receipt"],
		"cause": "The **Create > Purchase Receipt** option appears only for a submitted Purchase Order that still has quantity to receive and is not Closed or On Hold.",
		"solution": (
			"1. Open the [Purchase Order](/app/purchase-order). If its status is **Draft**, submit it.\n"
			"2. If the status is **On Hold**, use **Status > Resume**. If it is **Closed**, use **Status > Re-open**.\n"
			"3. Check **% Received**. If it is 100%, all quantity is already received; see linked receipts in the **Connections** tab.\n"
			"4. If you need to receive more than ordered, create a new Purchase Order, or set **Over Delivery/Receipt Allowance (%)** in [Stock Settings](/app/stock-settings) or on the [Item](/app/item).\n"
			"5. If **Is Subcontracted** is ticked, receive goods through a Subcontracting Receipt instead.\n\n"
			"**Check:** **Create > Purchase Receipt** is visible and the receipt fetches the pending quantity."
		),
	},
	{
		"id": "po-stuck-to-receive-and-bill",
		"title": "Purchase Order is stuck in To Receive and Bill status",
		"errors": [
			"status to receive and bill",
			"purchase order status not updating",
			"po still pending",
			"po not completed",
		],
		"tags": "purchase order status to receive and bill to bill to receive pending not completed close po status update nahi hua",
		"doctypes": ["Purchase Order", "Purchase Receipt", "Purchase Invoice"],
		"cause": "The status changes only when receipts and invoices are created from the Purchase Order (so they are linked) and are submitted. Entries made separately, or left in draft, do not update the order.",
		"solution": (
			"1. Open the [Purchase Order](/app/purchase-order) and check **% Received** and **% Billed**.\n"
			"2. Make sure the Purchase Receipt and Purchase Invoice were created using **Create** on this order and are submitted, not draft.\n"
			"3. If an invoice was made separately, cancel it and amend it. Delete the item rows, then use **Get Items From > Purchase Order** so the rows are linked.\n"
			"4. If the remaining quantity will never arrive, use **Status > Close** on the order.\n"
			"5. Use [Purchase Order Analysis](/app/query-report/Purchase Order Analysis) to see pending quantity and amount.\n\n"
			"**Check:** The status shows **Completed** or **Closed**."
		),
	},
	{
		"id": "sales-return-not-updating-stock",
		"title": "Sales return does not update stock",
		"errors": [
			"stock not increased after return",
			"credit note not updating stock",
			"sales return stock not added",
		],
		"tags": "sales return credit note stock not updated return maal wapas stock nahi badha delivery note return update stock",
		"doctypes": ["Sales Invoice", "Delivery Note", "Stock Ledger Entry"],
		"cause": "A Credit Note (Sales Invoice with **Is Return (Credit Note)**) moves stock only when **Update Stock** is ticked. If goods were sent on a Delivery Note, the return must be made from that Delivery Note.",
		"solution": (
			"1. If the goods left on a [Delivery Note](/app/delivery-note), open it and use **Create > Sales Return**. Submit it.\n"
			"2. Then create the Credit Note from the original [Sales Invoice](/app/sales-invoice) with **Create > Return / Credit Note** for the money side.\n"
			"3. If the original Sales Invoice had **Update Stock** ticked, make the return from that invoice and keep **Update Stock** ticked.\n"
			"4. Confirm the warehouse on the return rows is correct.\n\n"
			"**Check:** [Stock Ledger](/app/query-report/Stock Ledger) shows a positive entry for the returned quantity."
		),
	},
	{
		"id": "credit-debit-note-wrong-invoice",
		"title": "Credit Note or Debit Note made against the wrong invoice",
		"errors": [
			"return against wrong invoice",
			"credit note wrong invoice",
			"debit note wrong invoice",
			"returned qty exceeds",
			"cannot be returned more than",
		],
		"tags": "credit note debit note return against wrong invoice galat invoice change return against purchase return sales return",
		"doctypes": ["Sales Invoice", "Purchase Invoice"],
		"cause": "The **Return Against** field links the note to the original invoice and cannot be changed after submission. Return quantity is also limited to what was on that invoice.",
		"solution": (
			"1. Open the submitted note and click **Cancel**.\n"
			"2. Open the correct original [Sales Invoice](/app/sales-invoice) or [Purchase Invoice](/app/purchase-invoice).\n"
			"3. Use **Create > Return / Credit Note** (sales) or **Create > Return / Debit Note** (purchase) from it.\n"
			"4. Adjust quantities as negative values not exceeding the original quantities, then submit.\n"
			"5. To charge a customer more because of a rate increase (no goods moved), create a Sales Invoice with **Is Rate Adjustment Entry (Debit Note)** ticked instead.\n\n"
			"**Check:** The new note shows the correct **Return Against** and the original invoice outstanding is reduced."
		),
	},
	{
		"id": "duplicate-supplier-invoice-number",
		"title": "Supplier Invoice No already exists",
		"errors": [
			"supplier invoice no exists in purchase invoice",
			"duplicate supplier invoice",
			"bill no already exists",
		],
		"tags": "supplier invoice no duplicate bill no already exists purchase invoice same bill number vendor invoice dobara",
		"doctypes": ["Purchase Invoice", "Accounts Settings"],
		"cause": "**Check Supplier invoice number uniqueness** is enabled in Accounts Settings, and another Purchase Invoice from the same supplier in this fiscal year already uses the same **Supplier Invoice No**.",
		"solution": (
			"1. Search [Purchase Invoice](/app/purchase-invoice) by **Supplier Invoice No** to find the existing entry.\n"
			"2. If it is the same bill, do not enter it again; you may have a duplicate.\n"
			"3. If it is a genuinely different bill, correct the **Supplier Invoice No** to match the supplier's document exactly.\n"
			"4. Only if your suppliers legitimately repeat numbers, untick **Check Supplier invoice number uniqueness** in [Accounts Settings](/app/accounts-settings).\n\n"
			"**Check:** The Purchase Invoice saves without the duplicate message."
		),
	},
	{
		"id": "quotation-expired",
		"title": "Quotation has expired and cannot be converted",
		"errors": [
			"validity period of this quotation has ended",
			"quotation expired",
			"cannot create sales order from expired quotation",
		],
		"tags": "quotation expired valid till validity sales order create quotation purani ho gayi expire",
		"doctypes": ["Quotation", "Sales Order", "Selling Settings", "CRM Settings"],
		"cause": "The quotation's **Valid Till** date has passed, so its status is **Expired** and a Sales Order cannot be made from it by default.",
		"solution": (
			"1. Preferred: create a new [Quotation](/app/quotation/new) (or **Duplicate** the old one) with a later **Valid Till** date, submit it and convert it.\n"
			"2. To allow Sales Orders from expired quotations, tick **Allow Sales Order creation for expired Quotation** in [Selling Settings](/app/selling-settings).\n"
			"3. To change the default validity for new quotations, set **Default Quotation Validity Days** in [CRM Settings](/app/crm-settings).\n\n"
			"**Check:** **Create > Sales Order** works from the quotation."
		),
	},
	{
		"id": "customer-supplier-disabled-or-blocked",
		"title": "Customer or Supplier is disabled, frozen or on hold",
		"errors": [
			"is disabled",
			"is blocked so this transaction cannot proceed",
			"supplier is on hold",
			"customer is frozen",
			"supplier is frozen",
			"cannot select disabled",
		],
		"tags": "customer supplier disabled blocked hold frozen block supplier hold type party nahi aa raha band hai",
		"doctypes": ["Customer", "Supplier"],
		"cause": "The party has **Disabled** ticked, **Is Frozen** ticked, or (for suppliers) **Block Supplier** ticked with a **Hold Type** that covers invoices, payments or all transactions.",
		"solution": (
			"1. Open the [Customer](/app/customer) or [Supplier](/app/supplier).\n"
			"2. Untick **Disabled** if the party should be active.\n"
			"3. For a supplier, untick **Block Supplier**, or change **Hold Type** and the release date if the block is temporary.\n"
			"4. If **Is Frozen** is ticked, only users with the role set in **Roles Allowed to Set and Edit Frozen Account Entries** on the [Company](/app/company) can transact. Untick it, or ask an authorised user.\n"
			"5. Save, then reload the transaction and select the party again.\n\n"
			"**Check:** The party can be selected and the document submits."
		),
	},
	{
		"id": "payment-terms-due-date-wrong",
		"title": "Due date or payment schedule is wrong",
		"errors": [
			"due date cannot be before posting date",
			"payment schedule total must equal grand total",
			"total payment amount in payment schedule must be equal to grand",
			"due date wrong",
		],
		"tags": "payment terms due date payment schedule credit days template due date galat overdue invoice",
		"doctypes": ["Payment Terms Template", "Sales Invoice", "Purchase Invoice", "Customer", "Supplier", "Accounts Settings"],
		"cause": "The due date comes from the **Payment Terms Template** on the party or the order. A wrong template, a changed total after the schedule was built, or a manual date before the posting date causes these errors.",
		"solution": (
			"1. Check the **Payment Terms Template** on the [Customer](/app/customer) or [Supplier](/app/supplier) and in [Payment Terms Template](/app/payment-terms-template).\n"
			"2. On the invoice, open the **Payment Schedule** table; clear the rows and reselect the **Payment Terms Template** so it rebuilds with the current total.\n"
			"3. Make sure the due date (**Payment Due Date** on a Sales Invoice, **Due Date** on a Purchase Invoice, and each **Due Date** in the schedule) is on or after **Posting Date**.\n"
			"4. To carry terms from the order, tick **Automatically fetch Payment Terms from Order/Quotation** in [Accounts Settings](/app/accounts-settings).\n"
			"5. To skip the party default once, tick **Ignore Default Payment Terms Template** on the invoice.\n\n"
			"**Check:** The **Payment Schedule** total equals **Grand Total**, and [Accounts Receivable](/app/query-report/Accounts Receivable) shows the correct due date."
		),
	},
	{
		"id": "drop-ship-setup",
		"title": "Drop ship: supplier delivers directly to the customer",
		"errors": [
			"drop ship not working",
			"purchase order not created for drop ship",
			"supplier delivers to customer",
		],
		"tags": "drop ship dropship supplier delivers to customer direct delivery bina warehouse supplier se seedha customer",
		"doctypes": ["Item", "Sales Order", "Purchase Order", "Sales Invoice", "Purchase Invoice"],
		"cause": "Drop ship works only when the Sales Order row has **Supplier delivers to Customer** ticked and a supplier set. The Purchase Order must then be created from the Sales Order.",
		"solution": (
			"1. On the [Item](/app/item), tick **Delivered by Supplier (Drop Ship)** and set a default supplier in **Item Defaults**, or set it per row.\n"
			"2. In the [Sales Order](/app/sales-order/new) item row, confirm **Supplier delivers to Customer** is ticked and **Supplier** is filled. Submit.\n"
			"3. Use **Create > Purchase Order**. In the **Select Items** dialog, select the rows, set the supplier if needed and click **Create Purchase Order**. Submit the order. Its rows show **To be Delivered to Customer** ticked.\n"
			"4. No Delivery Note or Purchase Receipt is needed. When the supplier confirms delivery, use **Status > Deliver (Dropship)** on the Purchase Order.\n"
			"5. Bill normally with a Sales Invoice and a Purchase Invoice.\n\n"
			"**Check:** The Sales Order shows delivery as complete and no stock moved in your warehouse."
		),
	},
	{
		"id": "subcontracting-supplied-items",
		"title": "Subcontracting: raw materials are not supplied or consumed",
		"errors": [
			"supplied items not found",
			"raw materials not transferred",
			"please select bom for item",
			"supplier warehouse mandatory",
			"job worker warehouse",
			"consumed qty",
		],
		"tags": "subcontracting subcontract job work raw material supplied items consumed bom job worker warehouse transfer material to supplier",
		"doctypes": ["Purchase Order", "Subcontracting Order", "Subcontracting Receipt", "Stock Entry", "Buying Settings", "BOM"],
		"cause": "In v16, subcontracting runs through a Subcontracting Order. Raw materials must be sent to the **Job Worker Warehouse** by a Stock Entry before the finished goods are received, and each finished good item needs a BOM.",
		"solution": (
			"1. Create a [Purchase Order](/app/purchase-order/new) with **Is Subcontracted** ticked. In each row, enter the service item and its **Finished Good**. Submit it.\n"
			"2. Use **Create > Subcontracting Order** on the Purchase Order, or tick **Auto create Subcontracting Order** in [Buying Settings](/app/buying-settings). On the [Subcontracting Order](/app/subcontracting-order), set **Job Worker Warehouse** and confirm each finished good has a BOM. Submit it.\n"
			"3. On the Subcontracting Order, use **Transfer > Material to Supplier** to create a [Stock Entry](/app/stock-entry) that sends the raw materials. Submit it.\n"
			"4. When the finished goods arrive, use **Create > Subcontracting Receipt** on the Subcontracting Order. Check the **Consumed Items** table, then submit.\n"
			"5. The consumption basis is set by **Backflush raw materials of subcontract based on** on the **Subcontracting Settings** tab of Buying Settings.\n\n"
			"**Check:** The Subcontracting Order shows supplied and received quantities, and the finished goods appear in [Stock Balance](/app/query-report/Stock Balance)."
		),
	},
	{
		"id": "inter-company-party-not-found",
		"title": "Internal customer or supplier not found for inter-company transaction",
		"errors": [
			"no internal customer found",
			"no internal supplier found",
			"found for inter company transactions",
			"internal customer not found",
			"represents company",
		],
		"tags": "inter company internal customer internal supplier represents company branch transfer gstin intercompany invoice nahi ban raha",
		"doctypes": ["Customer", "Supplier", "Sales Invoice", "Purchase Invoice", "Sales Order", "Purchase Order"],
		"cause": "An inter-company document needs a Customer with **Is Internal Customer** and a Supplier with **Is Internal Supplier**, each with **Represents Company** set and the other company listed in **Allowed to transact with**.",
		"solution": (
			"1. Open or create a [Customer](/app/customer) for the receiving company. Tick **Is Internal Customer**, set **Represents Company**, and add the selling company in **Allowed to transact with**.\n"
			"2. Open or create a [Supplier](/app/supplier) for the selling company. Tick **Is Internal Supplier**, set **Represents Company**, and add the buying company in **Allowed to transact with**.\n"
			"3. For branch transfers between GSTINs of the same company, the address of each party must have the correct GSTIN.\n"
			"4. Submit the Sales Invoice, then use **Create > Inter Company Purchase Invoice**. For a transfer within the same company, the option is **Create > Internal Purchase Invoice**.\n\n"
			"**Check:** The Purchase Invoice is created with the internal supplier and links back to the Sales Invoice."
		),
	},
	{
		"id": "naming-series-wrong",
		"title": "Document number or naming series is wrong",
		"errors": [
			"naming series mandatory",
			"wrong document number",
			"series not starting from 1",
			"duplicate name",
			"already exists",
		],
		"tags": "naming series document number prefix series counter change number galat number invoice number format reset",
		"doctypes": ["Document Naming Settings", "Sales Invoice", "Purchase Order", "Buying Settings", "Selling Settings"],
		"cause": "Each document type uses a naming series with its own counter. The wrong series is selected, the series list is not set up, or the counter was not set to the next number.",
		"solution": (
			"1. Open [Document Naming Settings](/app/document-naming-settings).\n"
			"2. Select the document type and edit **Series List for this Transaction**. The first line is the default series.\n"
			"3. Use **Try a Naming Series** to preview the next number.\n"
			"4. To change the next number, select the series prefix and set **Current Value** in the **Update Series Counter** section.\n"
			"5. On the document, pick the correct **Series** before saving. The name cannot be changed after submit; cancel and amend if needed.\n"
			"6. Customer and Supplier naming is set by **Customer Naming By** in [Selling Settings](/app/selling-settings) and **Supplier Naming By** in [Buying Settings](/app/buying-settings).\n\n"
			"**Check:** A new document receives the expected number."
		),
	},
	{
		"id": "taxes-not-copied-pr-to-pi",
		"title": "Taxes are not copied from Purchase Receipt to Purchase Invoice",
		"errors": [
			"taxes not fetched in purchase invoice",
			"gst not coming in purchase invoice",
			"tax missing",
			"taxes and charges not copied",
		],
		"tags": "taxes gst not copied purchase invoice purchase receipt tax template igst cgst sgst tax nahi aaya",
		"doctypes": ["Purchase Receipt", "Purchase Invoice", "Purchase Taxes and Charges Template", "Item Tax Template", "Accounts Settings"],
		"cause": "Taxes are copied only when the invoice is created from the receipt. They may also be recalculated by tax category, address or Item Tax Template, which can clear or change them.",
		"solution": (
			"1. Create the invoice from the [Purchase Receipt](/app/purchase-receipt) with **Create > Purchase Invoice**, not by typing items manually.\n"
			"2. If taxes are blank, select the **Purchase Taxes and Charges Template** on the invoice.\n"
			"3. Check the supplier address and company address GSTINs, and the **Tax Category**; a change here selects a different template.\n"
			"4. Check that each item has the right **Item Tax Template** (GST rate).\n"
			"5. In [Accounts Settings](/app/accounts-settings), confirm **Automatically add taxes from Taxes and Charges Template** and **Automatically add Taxes and Charges from Item Tax Template** are ticked.\n\n"
			"**Check:** The **Purchase Taxes and Charges** table matches the receipt, and **Total Taxes and Charges** is correct."
		),
	},
	{
		"id": "rejected-qty-handling",
		"title": "How to handle rejected quantity on Purchase Receipt",
		"errors": [
			"rejected warehouse is mandatory against rejected item",
			"accepted qty + rejected qty must be equal to received quantity",
			"rejected qty",
			"rejected warehouse",
		],
		"tags": "rejected qty rejected warehouse quality fail damaged return to supplier purchase receipt kharab maal reject",
		"doctypes": ["Purchase Receipt", "Purchase Invoice", "Warehouse", "Buying Settings"],
		"cause": "When some received items fail inspection, the receipt must split **Received Quantity** into **Accepted Quantity** and **Rejected Quantity**, and rejected stock needs a **Rejected Warehouse**.",
		"solution": (
			"1. Create a [Warehouse](/app/warehouse) for rejected goods and tick **Is Rejected Warehouse**.\n"
			"2. In the [Purchase Receipt](/app/purchase-receipt) row, enter **Accepted Quantity** and **Rejected Quantity** so they add up to **Received Quantity**.\n"
			"3. Set **Rejected Warehouse** in the row or in the header.\n"
			"4. To send the goods back, open the receipt and use **Create > Purchase Return**. Tick **Return Qty from Rejected Warehouse** on the return row.\n"
			"5. To decide whether rejected quantity is billed, set **Bill for rejected quantity in Purchase Invoice** in [Buying Settings](/app/buying-settings).\n\n"
			"**Check:** [Stock Balance](/app/query-report/Stock Balance) shows the rejected quantity in the rejected warehouse only."
		),
	},
]
