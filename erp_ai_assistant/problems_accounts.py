"""Troubleshooting entries for Accounts, GST (India Compliance) and Payments in the offline Help Guide."""

PROBLEMS = [
	{
		"id": "acc-default-cost-center-missing",
		"title": "Please set default Cost Center in Company",
		"errors": [
			"please set default cost center",
			"please set a default cost center",
			"cost center is required",
			"cost center is mandatory",
			"please set cost center",
		],
		"tags": "cost center default company missing mandatory accounts invoice journal cost centre kaise set kare error aa raha",
		"doctypes": ["Company", "Cost Center", "Sales Invoice", "Purchase Invoice", "Journal Entry"],
		"cause": "The transaction needs a cost center for income or expense rows, but none was selected and the company has no **Default Cost Center**.",
		"solution": (
			"1. Open [Company](/app/company) and select your company.\n"
			"2. Go to the **Accounts** tab, section **Default Accounts**.\n"
			"3. Set **Default Cost Center** (usually **Main - <company abbreviation>**). If none exists, create one in [Cost Center](/app/cost-center).\n"
			"4. Save the company.\n"
			"5. Return to the document, clear and re-select the item or account so the cost center is fetched again, then save.\n\n"
			"**Check:** The **Cost Center** column in the item or account rows is filled and the document saves without the error."
		),
	},
	{
		"id": "acc-default-receivable-payable-missing",
		"title": "Default receivable or payable account is missing",
		"errors": [
			"please set default receivable account",
			"please set default payable account",
			"receivable account is mandatory",
			"payable account is mandatory",
			"debit to is mandatory",
			"credit to is mandatory",
			"party account not found",
		],
		"tags": "default receivable payable account debtors creditors debit to credit to missing customer supplier party account company khata",
		"doctypes": ["Company", "Customer", "Supplier", "Customer Group", "Supplier Group", "Sales Invoice", "Purchase Invoice"],
		"cause": "ERPNext could not find a receivable or payable account for the party. It looks first at the customer or supplier, then at its group, then at the company.",
		"solution": (
			"1. Open [Company](/app/company), go to the **Accounts** tab and set **Default Receivable Account** (for example **Debtors**) and **Default Payable Account** (for example **Creditors**).\n"
			"2. If a specific party needs a different account, open the [Customer](/app/customer) or [Supplier](/app/supplier), go to the **Accounting** tab and add a row for the company in the **Default Accounts** table.\n"
			"3. Save, then reopen the invoice and re-select the party so **Debit To** or **Credit To** is fetched again.\n\n"
			"**Check:** **Debit To** (Sales Invoice) or **Credit To** (Purchase Invoice) shows the correct account and the invoice saves."
		),
	},
	{
		"id": "acc-default-income-expense-missing",
		"title": "Default income or expense account is missing on items",
		"errors": [
			"income account is mandatory",
			"expense account is mandatory",
			"please set default income account",
			"please set default expense account",
			"income account required",
			"expense account required",
		],
		"tags": "income account expense account item default cost of goods sold cogs missing mandatory sales purchase invoice kharcha aamdani",
		"doctypes": ["Company", "Item", "Item Group", "Sales Invoice", "Purchase Invoice"],
		"cause": "Each invoice row needs an income account (sales) or expense account (purchase). None was found on the item, its item group or the company.",
		"solution": (
			"1. Open [Company](/app/company), go to the **Accounts** tab and set **Default Income Account** (for example **Sales**) and **Default Cost of Goods Sold Account**.\n"
			"2. For item-specific accounts, open the [Item](/app/item), go to the **Item Defaults** table and set **Default Income Account** and **Default Expense Account** for the company.\n"
			"3. In the invoice, remove the row and add the item again so the accounts are fetched.\n\n"
			"**Check:** Expand an item row in the invoice. **Income Account** or **Expense Account** is filled."
		),
	},
	{
		"id": "acc-round-off-account-missing",
		"title": "Round Off Account is not set in Company",
		"errors": [
			"please mention round off account",
			"round off account",
			"round off cost center",
			"please set round off account",
		],
		"tags": "round off rounding account cost center paise difference company rounded total roundoff",
		"doctypes": ["Company", "Sales Invoice", "Purchase Invoice", "Journal Entry"],
		"cause": "Small decimal differences are posted to the company's **Round Off Account**. If it is empty, submission fails.",
		"solution": (
			"1. Open [Company](/app/company) and go to the **Accounts** tab, section **Round Off**.\n"
			"2. Set **Round Off Account** and **Round Off Cost Center**. The account is usually an expense account named **Round Off** under **Indirect Expenses**. If it does not exist, create it in [Chart of Accounts](/app/account/view/tree).\n"
			"3. Optionally set **Round Off for Opening** for opening entries.\n"
			"4. Save and submit the document again.\n\n"
			"**Check:** The document submits. Open [General Ledger](/app/query-report/General Ledger) for the voucher to see the small round-off line."
		),
	},
	{
		"id": "acc-fiscal-year-not-found",
		"title": "Fiscal Year not found or date is outside the fiscal year",
		"errors": [
			"fiscal year",
			"not in any active fiscal year",
			"is not in any active fiscal year",
			"fiscal year not found",
			"date is not in fiscal year",
			"please create a new fiscal year",
		],
		"tags": "fiscal year financial year fy not found date outside active april march new year create varsh saal",
		"doctypes": ["Fiscal Year", "Company"],
		"cause": "The posting date falls in a period for which no Fiscal Year exists, or the existing Fiscal Year is disabled or not linked to your company.",
		"solution": (
			"1. Open [Fiscal Year](/app/fiscal-year) and check that a year covering the posting date exists (in India, 1 April to 31 March).\n"
			"2. If it is missing, click [new](/app/fiscal-year/new), enter the **Year Name** (for example 2026-2027), **Year Start Date** and **Year End Date**, and save.\n"
			"3. If the year exists, make sure **Disabled** is unchecked. If the **Companies** table has rows, add your company to it.\n"
			"4. Reload the page (F5) and save the document again.\n\n"
			"**Check:** The document saves, and reports such as [General Ledger](/app/query-report/General Ledger) accept the new fiscal year in their filters."
		),
	},
	{
		"id": "acc-posting-date-future",
		"title": "Posting Date cannot be a future date",
		"errors": [
			"posting date cannot be future date",
			"cannot be a future date",
			"future posting not allowed",
			"posting future date",
		],
		"tags": "posting date future date tomorrow aage ki date backdated set posting time edit posting date purchase receipt grn",
		"doctypes": ["Purchase Receipt"],
		"cause": "A Purchase Receipt cannot have a **Posting Date** later than today, because goods cannot be received on a future date.",
		"solution": (
			"1. In the [Purchase Receipt](/app/purchase-receipt), tick **Edit Posting Date and Time** (shown below the posting date).\n"
			"2. Set **Posting Date** to today or a past date.\n"
			"3. If the date in the form is ahead of today, check the **Time Zone** in [System Settings](/app/system-settings) and the clock of the server.\n"
			"4. Save and submit.\n\n"
			"**Check:** The document submits without the error and shows the corrected date."
		),
	},
	{
		"id": "acc-accounts-frozen",
		"title": "Account is frozen or accounts are frozen till a date",
		"errors": [
			"account is frozen",
			"is frozen",
			"not authorized to add or update entries before",
			"accounts frozen till date",
			"frozen account",
			"you are not authorized to set frozen value",
		],
		"tags": "frozen freeze account locked closed books accounts frozen till date permission role band",
		"doctypes": ["Company", "Account", "Customer", "Supplier"],
		"cause": "Either the account itself is marked **Frozen**, or the posting date is on or before the company's **Accounts Frozen Till Date** and your role is not allowed to post there.",
		"solution": (
			"1. Open [Company](/app/company) and go to the **Accounts Closing** tab.\n"
			"2. Check **Accounts Frozen Till Date**. Either post with a later date, or ask an accounts manager to move this date back.\n"
			"3. If certain users must still post, set **Roles Allowed to Set and Edit Frozen Account Entries** to their role.\n"
			"4. If one account is frozen, open it in [Chart of Accounts](/app/account/view/tree), edit it and set **Frozen** to **No**.\n"
			"5. If a customer or supplier is frozen, open the party, go to the **Settings** tab and untick **Is Frozen**.\n\n"
			"**Check:** The document saves and submits with the intended date."
		),
	},
	{
		"id": "acc-party-account-currency-mismatch",
		"title": "Party account currency does not match the invoice currency",
		"errors": [
			"party account currency",
			"account currency",
			"currency must be same as",
			"accounting entry for party can only be made in currency",
			"invoice currency",
			"billing currency must be equal to",
		],
		"tags": "currency mismatch usd inr foreign party account multi currency customer supplier billing currency dollar",
		"doctypes": ["Customer", "Supplier", "Account", "Sales Invoice", "Purchase Invoice"],
		"cause": "The receivable or payable account is in one currency (for example INR) but the invoice is in another (for example USD), or the party already has entries in a different currency.",
		"solution": (
			"1. Create a receivable or payable account in the foreign currency in [Chart of Accounts](/app/account/view/tree), for example **Debtors USD**, with **Currency** set to USD.\n"
			"2. Open the [Customer](/app/customer) or [Supplier](/app/supplier). In the **Accounting** tab, add that account for the company in the **Default Accounts** table. Set **Billing Currency** to match.\n"
			"3. Create the invoice again in the party's currency.\n"
			"4. A party that already has transactions in one currency cannot be billed in another. Create a separate party if needed.\n\n"
			"**Check:** **Debit To** or **Credit To** shows an account in the same currency as the invoice, and the invoice submits."
		),
	},
	{
		"id": "acc-exchange-rate-not-found",
		"title": "Exchange rate not found",
		"errors": [
			"unable to find exchange rate",
			"exchange rate not found",
			"exchange rate is mandatory",
			"conversion rate is mandatory",
			"please create currency exchange record manually",
		],
		"tags": "exchange rate conversion rate currency usd inr forex not found currency exchange settings",
		"doctypes": ["Currency Exchange", "Currency Exchange Settings", "Accounts Settings"],
		"cause": "The system could not fetch a rate for the currency pair on that date, usually because there is no internet access to the rate provider or no manual rate is saved.",
		"solution": (
			"1. Open [Currency Exchange](/app/currency-exchange/new) and add a record with **Date**, **From Currency**, **To Currency** and **Exchange Rate**.\n"
			"2. Optionally review the provider in [Currency Exchange Settings](/app/currency-exchange-settings).\n"
			"3. To reuse the last saved rate, enable **Allow Stale Exchange Rates** in [Accounts Settings](/app/accounts-settings).\n"
			"4. You can also type the rate directly in the **Exchange Rate** field of the document.\n\n"
			"**Check:** **Exchange Rate** is filled in the document and the totals in company currency are correct."
		),
	},
	{
		"id": "acc-journal-debit-credit-not-equal",
		"title": "Debit and credit are not equal in a Journal Entry",
		"errors": [
			"total debit must be equal to total credit",
			"debit and credit not equal",
			"difference is",
			"total debit total credit",
		],
		"tags": "journal entry debit credit not equal difference balance jv voucher mismatch barabar nahi",
		"doctypes": ["Journal Entry"],
		"cause": "A Journal Entry must balance. The sum of **Debit** must equal the sum of **Credit** across all rows.",
		"solution": (
			"1. Open the [Journal Entry](/app/journal-entry) and look at **Difference (Dr - Cr)** below the accounts table.\n"
			"2. Correct the amounts, or add a row for the missing account.\n"
			"3. You can click **Make Difference Entry** to add a balancing row, then choose the right account for it.\n"
			"4. For foreign currency rows, check the **Exchange Rate** in each row.\n\n"
			"**Check:** **Total Debit** equals **Total Credit** and the entry submits."
		),
	},
	{
		"id": "acc-payment-allocated-more-than-outstanding",
		"title": "Allocated amount is greater than the outstanding amount",
		"errors": [
			"allocated amount cannot be greater than outstanding amount",
			"cannot be greater than outstanding",
			"allocated amount",
			"over allocation",
			"total allocated amount cannot be greater than",
		],
		"tags": "payment entry allocated amount outstanding greater excess advance overpayment allocation references bakaya",
		"doctypes": ["Payment Entry", "Payment Reconciliation"],
		"cause": "A reference row in the payment allocates more than what is still due on that invoice, often because part of it was already paid.",
		"solution": (
			"1. In the [Payment Entry](/app/payment-entry), go to the **Payment References** table.\n"
			"2. Click **Get Outstanding Invoices** to reload current balances.\n"
			"3. Set each **Allocated** value to no more than its **Outstanding** value.\n"
			"4. Any extra amount stays as **Unallocated Amount** and acts as an advance. You can allocate it later with [Payment Reconciliation](/app/payment-reconciliation).\n\n"
			"**Check:** The payment submits, and the invoice shows status **Paid** or **Partly Paid**."
		),
	},
	{
		"id": "acc-outstanding-not-reducing",
		"title": "Invoice outstanding does not reduce after payment",
		"errors": [
			"outstanding not reducing",
			"invoice still unpaid",
			"payment not linked",
			"invoice status overdue after payment",
			"unallocated amount",
		],
		"tags": "outstanding not reducing payment received but invoice unpaid overdue unlinked advance payment reconciliation match paisa mila",
		"doctypes": ["Payment Entry", "Payment Reconciliation", "Sales Invoice", "Purchase Invoice", "Journal Entry"],
		"cause": "The payment was saved without linking it to the invoice, so it sits as an unallocated advance against the party.",
		"solution": (
			"1. Open [Payment Reconciliation](/app/payment-reconciliation).\n"
			"2. Select **Company**, **Party Type**, **Party** and the **Receivable / Payable Account**.\n"
			"3. Click **Get Unreconciled Entries**.\n"
			"4. In the **Invoices** and **Payments** tables, select the invoice and the payment, then click **Allocate**.\n"
			"5. Check the rows in the **Allocation** table, then click **Reconcile**.\n"
			"6. For large volumes, use [Process Payment Reconciliation](/app/process-payment-reconciliation).\n\n"
			"**Check:** The invoice status becomes **Paid** or **Partly Paid**, and [Accounts Receivable](/app/query-report/Accounts Receivable) no longer shows it as fully due."
		),
	},
	{
		"id": "acc-cannot-cancel-invoice-linked-payment",
		"title": "Cannot cancel an invoice that is linked to a payment",
		"errors": [
			"cannot delete or cancel because",
			"is linked with payment entry",
			"cannot cancel because submitted",
			"linked with",
			"cannot cancel invoice",
		],
		"tags": "cancel invoice linked payment entry unlink unreconcile cannot cancel amend delete raddh",
		"doctypes": ["Accounts Settings", "Sales Invoice", "Purchase Invoice", "Payment Entry", "Unreconcile Payment"],
		"cause": "A submitted payment is allocated against the invoice. By default, ERPNext blocks cancellation to protect the payment link.",
		"solution": (
			"Use one of these options:\n\n"
			"1. **Option A:** Open [Accounts Settings](/app/accounts-settings) and enable **Unlink Payment on cancellation of invoice**. Then cancel the invoice. The payment becomes an unallocated advance.\n"
			"2. **Option B:** Open the [Payment Entry](/app/payment-entry), click **Actions** > **UnReconcile**, select the invoice row and click **UnReconcile**. Then cancel the invoice.\n"
			"3. **Option C:** Cancel the payment first, then cancel the invoice.\n\n"
			"After you amend and resubmit the invoice, allocate the payment again with [Payment Reconciliation](/app/payment-reconciliation). With option C, amend and submit the payment instead.\n\n"
			"**Check:** The invoice status shows **Cancelled**. With options A and B, the payment still appears for the party as an unallocated amount."
		),
	},
	{
		"id": "acc-period-closed",
		"title": "Accounting period is closed for this document",
		"errors": [
			"accounting period",
			"is closed",
			"you cannot create or cancel any accounting entries with in the closed accounting period",
			"closed accounting period",
			"period closing voucher",
			"books have been closed",
			"books have been closed till the period ending on",
			"you cannot create/amend any accounting entries till this date",
		],
		"tags": "accounting period closed period closing voucher year end close books locked month closing band",
		"doctypes": ["Accounting Period", "Period Closing Voucher", "Company"],
		"cause": "The posting date falls inside an **Accounting Period** marked closed for this document type, or on or before the end date of a submitted **Period Closing Voucher**.",
		"solution": (
			"1. Open [Accounting Period](/app/accounting-period) and find the period covering the posting date.\n"
			"2. In the **Closed Documents** table, untick **Closed** for the **Document Type**, or post with a date outside the period. Users with the **Exempted Role** can still post in the period.\n"
			"3. If the message says the books have been closed, a [Period Closing Voucher](/app/period-closing-voucher) covers that date. Cancel it only with the accountant's approval, post the entry, then create the voucher again.\n"
			"4. Also check **Accounts Frozen Till Date** on the [Company](/app/company).\n\n"
			"**Check:** The document submits with the intended posting date."
		),
	},
	{
		"id": "acc-budget-exceeded",
		"title": "Annual or monthly budget exceeded",
		"errors": [
			"budget exceeded",
			"budget limit exceeded",
			"annual budget for account",
			"it is already exceeded by",
			"it will be exceeded by",
			"budget for account",
		],
		"tags": "budget exceeded stop warn cost center expense limit material request purchase order budget variance revise budget",
		"doctypes": ["Budget", "Cost Center", "Purchase Order", "Material Request", "Company"],
		"cause": "A [Budget](/app/budget) exists for this account and cost center (or project), and its control action is set to **Stop** when the limit is crossed.",
		"solution": (
			"1. Open [Budget](/app/budget) and find the submitted budget for the cost center and **Account**.\n"
			"2. To change it, click **Actions** > **Revise Budget**. In the new revision, increase **Budget Amount**, or change the action fields (for example **Action if Annual Budget Exceeded on PO**) from **Stop** to **Warn** or **Ignore**. Then submit the revision.\n"
			"3. Users with the **Exception Budget Approver Role** set on the [Company](/app/company) (**Accounts** tab) can override the stop.\n"
			"4. Review spending in [Budget Variance Report](/app/query-report/Budget Variance Report).\n\n"
			"**Check:** The document submits, or shows only a warning instead of an error."
		),
	},
	{
		"id": "acc-tax-template-not-applied",
		"title": "Tax template not applied or tax rows are empty",
		"errors": [
			"taxes not applied",
			"tax rows empty",
			"no taxes",
			"gst not calculated",
			"total taxes and charges zero",
		],
		"tags": "tax template not applied empty taxes and charges gst missing zero tax category tax rule item tax template lagaya nahi",
		"doctypes": ["Sales Taxes and Charges Template", "Purchase Taxes and Charges Template", "Item Tax Template", "Tax Category", "Tax Rule", "Accounts Settings"],
		"cause": "No tax template matched the transaction. Templates are chosen from the tax category, the party address and the company GSTIN. If none matches, the taxes table stays empty.",
		"solution": (
			"1. Open [Accounts Settings](/app/accounts-settings) and make sure **Automatically add taxes from Taxes and Charges Template** is enabled.\n"
			"2. Check that the customer and company addresses have a **GSTIN / UIN** and **GST State**, so the system can pick the **In-State** or **Out-State** template.\n"
			"3. Open [Sales Taxes and Charges Template](/app/sales-taxes-and-charges-template) or [Purchase Taxes and Charges Template](/app/purchase-taxes-and-charges-template) and confirm a template exists for the company with the right **Tax Category**.\n"
			"4. For item-wise rates, set an [Item Tax Template](/app/item-tax-template) in the **Taxes** table on the item's **Tax** tab.\n"
			"5. In the document, select the template in **Sales Taxes and Charges Template** (or **Purchase Taxes and Charges Template**), or re-select the party.\n\n"
			"**Check:** The taxes table shows GST rows and **Total Taxes and Charges** is more than zero."
		),
	},
	{
		"id": "gst-place-of-supply-wrong",
		"title": "Place of Supply is wrong on an invoice",
		"errors": [
			"place of supply",
			"invalid place of supply",
			"place of supply is mandatory",
			"wrong state code",
		],
		"tags": "place of supply pos state code wrong gst state address shipping billing interstate intrastate rajya",
		"doctypes": ["Sales Invoice", "Purchase Invoice", "Address"],
		"cause": "**Place of Supply** is derived from the shipping or billing address of the customer (or the company address for purchases). A wrong or missing **GST State** on that address gives a wrong value.",
		"solution": (
			"1. Open the party's [Address](/app/address) and check **GST State** and **GSTIN / UIN**. The first two digits of the GSTIN must match the state code.\n"
			"2. Save the address.\n"
			"3. In the invoice, re-select **Customer Address** and **Shipping Address Name** so **Place of Supply** is recalculated.\n"
			"4. If needed, edit **Place of Supply** directly. It uses the format **23-Madhya Pradesh**.\n"
			"5. Re-apply the tax template after changing it.\n\n"
			"**Check:** **Place of Supply** shows the correct state and the GST type (CGST+SGST or IGST) matches it."
		),
	},
	{
		"id": "gst-cgst-sgst-vs-igst-wrong",
		"title": "CGST and SGST applied instead of IGST, or the reverse",
		"errors": [
			"cannot charge cgst/sgst for inter-state supplies",
			"cannot charge igst for intra-state supplies",
			"cannot charge igst",
			"cannot charge cgst",
			"wrong gst type",
		],
		"tags": "cgst sgst igst wrong interstate intrastate in-state out-state tax category template gst type galat",
		"doctypes": ["Sales Invoice", "Purchase Invoice", "Sales Taxes and Charges Template", "Tax Category", "Address"],
		"cause": "India Compliance compares the company GSTIN state with **Place of Supply**. The same state needs CGST+SGST. Different states need IGST. The selected template does not match.",
		"solution": (
			"1. Check **Company GSTIN** and **Place of Supply** on the invoice.\n"
			"2. If both states are the same, select the **In-State** template. If they differ, select the **Out-State** template.\n"
			"3. Make sure the templates in [Sales Taxes and Charges Template](/app/sales-taxes-and-charges-template) have the right [Tax Category](/app/tax-category) (**In-State** or **Out-State**).\n"
			"4. For multi-GSTIN branches, check that the correct **Company Address Name** (and its GSTIN) is selected.\n\n"
			"**Check:** Saving the invoice gives no GST error, and the taxes table shows the expected GST heads."
		),
	},
	{
		"id": "gst-invalid-gstin",
		"title": "Invalid GSTIN or GSTIN checksum error",
		"errors": [
			"invalid gstin",
			"gstin checksum",
			"invalid gstin checksum",
			"gstin should be 15 characters",
			"gstin is not valid",
			"first 2 digits of gstin should match with state",
		],
		"tags": "gstin invalid checksum 15 characters format pan state code mismatch gst number galat",
		"doctypes": ["Address", "Customer", "Supplier", "Company", "GSTIN"],
		"cause": "A GSTIN has 15 characters: a 2-digit state code, the 10-character PAN, an entity number, the letter Z and a check digit. A typing error breaks the check digit, or the state code does not match the address.",
		"solution": (
			"1. Copy the GSTIN exactly from the party's GST certificate or the GST portal. Use capital letters and no spaces.\n"
			"2. Make sure the first two digits match the **GST State** of the [Address](/app/address). The number is stored in **GSTIN / UIN**.\n"
			"3. If **Enable API Features** is on in [GST Settings](/app/gst-settings), enable **Autofill Party Information based on GSTIN** so details are fetched from the GSTIN when you create the party.\n"
			"4. For unregistered parties, leave the GSTIN empty and set **GST Category** to **Unregistered**.\n"
			"5. Review saved numbers with [GSTIN Status](/app/query-report/GSTIN Status).\n\n"
			"**Check:** The address or party saves without a GSTIN error."
		),
	},
	{
		"id": "gst-hsn-missing-invalid",
		"title": "HSN/SAC code is missing or has an invalid length",
		"errors": [
			"hsn/sac code",
			"hsn code is mandatory",
			"hsn/sac must exist",
			"invalid hsn",
			"hsn/sac code should be",
			"digits",
		],
		"tags": "hsn sac code missing invalid length 4 6 8 digits item tax gst hsn code mandatory",
		"doctypes": ["Item", "Item Group", "GST HSN Code", "GST Settings", "Sales Invoice"],
		"cause": "**Validate HSN/SAC Code in Sales Items and Transactions** is enabled in GST Settings, and the item has no HSN/SAC code or one with fewer digits than **Minimum HSN/SAC Code Digits**.",
		"solution": (
			"1. Open the [Item](/app/item) and set **HSN/SAC**. It must exist in [GST HSN Code](/app/gst-hsn-code).\n"
			"2. Check the required length in [GST Settings](/app/gst-settings) under **Minimum HSN/SAC Code Digits** (6 digits for turnover above 5 crore, otherwise 4).\n"
			"3. You can also set **HSN/SAC** on the [Item Group](/app/item-group) so new items inherit it.\n"
			"4. In the invoice, remove and re-add the item so the code is fetched.\n\n"
			"**Check:** Every item row shows **HSN/SAC** and the invoice saves."
		),
	},
	{
		"id": "gst-ewaybill-failed",
		"title": "e-Waybill generation failed or API is not configured",
		"errors": [
			"e-waybill",
			"ewaybill",
			"e waybill generation failed",
			"api features are not enabled",
			"gst credential",
			"vehicle no",
			"transporter id",
			"distance",
		],
		"tags": "e-waybill ewaybill eway bill failed api not configured credential threshold 50000 vehicle transporter distance part a part b",
		"doctypes": ["GST Settings", "GST Credential", "Sales Invoice", "Delivery Note", "e-Waybill Log"],
		"cause": "e-Waybill generation needs **Enable API Features** and **Enable e-Waybill Features** in GST Settings, valid credentials for the company GSTIN, and transport details on the document. It is required only above the threshold value.",
		"solution": (
			"1. Open [GST Settings](/app/gst-settings). Tick **Enable API Features** and enter the India Compliance **API Secret**.\n"
			"2. Tick **Enable e-Waybill Features**. Check **Default Threshold Value for e-Waybill Generation** (normally 50,000) and the state-wise table **e-Waybill Threshold for Intrastate**.\n"
			"3. In the **Credentials** tab, add the e-Waybill username and password for each company GSTIN.\n"
			"4. On the invoice, fill **Transporter** (or **GST Transporter ID**), **Vehicle No** or **Transport Receipt No**, **Mode of Transport** and **Distance (in km)**.\n"
			"5. On the submitted invoice, click **e-Waybill** > **Generate**. Read the exact error in the message or in [e-Waybill Log](/app/e-waybill-log), and correct the field it names.\n\n"
			"**Check:** **e-Waybill No.** is filled on the invoice and **e-Waybill Status** shows **Generated**."
		),
	},
	{
		"id": "gst-einvoice-errors",
		"title": "e-Invoice (IRN) generation failed",
		"errors": [
			"e-invoice",
			"einvoice",
			"irn",
			"duplicate irn",
			"e-invoice not applicable",
			"e-invoice generation failed",
			"invalid buyer gstin",
		],
		"tags": "e-invoice einvoice irn qr code generation failed duplicate irn nic portal api applicable from b2b",
		"doctypes": ["GST Settings", "Sales Invoice", "Address", "Item"],
		"cause": "e-Invoice is required for B2B invoices when the company crosses the turnover limit. Generation fails when API settings, applicability dates, addresses, GSTIN, HSN or item values are wrong.",
		"solution": (
			"1. Open [GST Settings](/app/gst-settings) and tick **Enable API Features**. The **e-Invoice** section then appears.\n"
			"2. Tick **Enable e-Invoicing** and set **e-Invoice Applicable From**.\n"
			"3. If only some companies need it, tick **Apply e-Invoice for Selected Companies** instead and fill the **e-Invoice Applicable Companies** table.\n"
			"4. Check that the customer and company addresses have a pincode, city and correct GSTIN, and that every item has a valid **HSN/SAC**.\n"
			"5. On the submitted invoice, click **e-Invoice** > **Generate**. Fix the field named in the error and try again.\n"
			"6. For **Duplicate IRN**, enable **Fetch e-Invoice details from GST Portal** so the existing IRN is fetched instead of a new one being generated.\n"
			"7. Note the **e-Invoice Reporting Time Limit (in Days)** for older invoices.\n\n"
			"**Check:** **e-Invoice Status** on the invoice shows **Generated**, and the IRN and QR code appear on the print."
		),
	},
	{
		"id": "gst-reverse-charge",
		"title": "Reverse charge GST is not calculated correctly",
		"errors": [
			"reverse charge",
			"rcm",
			"reverse charge not applied",
			"is reverse charge",
		],
		"tags": "reverse charge rcm gst unregistered supplier purchase invoice tax category self invoice legal gta",
		"doctypes": ["Purchase Invoice", "Supplier", "Tax Category", "GST Settings", "Purchase Taxes and Charges Template"],
		"cause": "Reverse charge needs the **Is Reverse Charge** flag on the document and a template that posts GST as both payable and input credit. Without both, the GST lines are wrong or missing.",
		"solution": (
			"1. On the [Supplier](/app/supplier), tick **Reverse Charge Applicable** if all their supplies are under RCM.\n"
			"2. Use a [Purchase Taxes and Charges Template](/app/purchase-taxes-and-charges-template) for RCM, linked to the [Tax Category](/app/tax-category) **Reverse Charge In-State** or **Reverse Charge Out-State** (both have **Is Reverse Charge** ticked).\n"
			"3. On the [Purchase Invoice](/app/purchase-invoice), tick **Is Reverse Charge** and select the RCM template.\n"
			"4. For purchases from unregistered suppliers, review **Enable Reverse Charge for Purchase from Unregistered Supplier** and **Invoice Value Threshold for Reverse Charge** in [GST Settings](/app/gst-settings).\n\n"
			"**Check:** The GST rows do not increase the amount payable to the supplier, and [GSTR-3B Details](/app/query-report/GSTR-3B Details) lists the invoice under reverse charge."
		),
	},
	{
		"id": "acc-unrealized-profit-loss-missing",
		"title": "Unrealized Profit / Loss account missing on internal transfer",
		"errors": [
			"unrealized profit / loss account",
			"unrealized profit",
			"please set unrealized",
			"unrealized profit loss account",
		],
		"tags": "unrealized profit loss account internal transfer internal customer supplier branch transfer gstin stock transfer",
		"doctypes": ["Company", "Sales Invoice", "Purchase Invoice", "Delivery Note"],
		"cause": "Transfers between branches of the same company using an internal customer or supplier book any margin to the **Unrealized Profit / Loss Account**. It is not set on the company or the document.",
		"solution": (
			"1. Create an account such as **Unrealized Profit** in [Chart of Accounts](/app/account/view/tree) if none exists.\n"
			"2. Open [Company](/app/company), go to the **Accounts** tab and set **Unrealized Profit / Loss Account**.\n"
			"3. Reopen the invoice. The **Unrealized Profit / Loss Account** field is fetched, or you can set it directly.\n"
			"4. Save and submit.\n\n"
			"**Check:** The invoice submits, and the [General Ledger](/app/query-report/General Ledger) shows the transfer margin in that account."
		),
	},
	{
		"id": "acc-inter-company-invoice-not-created",
		"title": "Inter-company invoice or order is not created",
		"errors": [
			"inter company",
			"internal customer",
			"internal supplier",
			"no internal supplier found",
			"no internal customer found",
			"not allowed for",
		],
		"tags": "inter company internal customer supplier branch invoice not created make inter company purchase invoice allowed to transact with",
		"doctypes": ["Customer", "Supplier", "Sales Invoice", "Purchase Invoice", "Sales Order", "Purchase Order"],
		"cause": "ERPNext creates the counter document only when an internal customer and an internal supplier are set up and linked to the right companies.",
		"solution": (
			"1. Open the [Customer](/app/customer) that represents the other company or branch. In the **Accounting** tab, tick **Is Internal Customer**, set **Represents Company**, and add your company to **Allowed to transact with**.\n"
			"2. Do the same on the matching [Supplier](/app/supplier) with **Is Internal Supplier**.\n"
			"3. Submit the [Sales Invoice](/app/sales-invoice) to that internal customer.\n"
			"4. Click **Create** > **Inter Company Purchase Invoice**. For a branch of the same company, the button is **Internal Purchase Invoice**.\n\n"
			"**Check:** Both invoices show each other in **Inter Company Invoice Reference**."
		),
	},
	{
		"id": "acc-opening-balance-mismatch",
		"title": "Opening balances do not match or the Trial Balance shows a difference",
		"errors": [
			"opening balance",
			"temporary opening",
			"opening mismatch",
			"trial balance not matching",
			"difference in opening",
		],
		"tags": "opening balance mismatch trial balance temporary opening difference opening invoice creation tool journal migration shuru",
		"doctypes": ["Journal Entry", "Opening Invoice Creation Tool", "Account", "Stock Reconciliation"],
		"cause": "Opening entries were posted in parts (accounts, party invoices, stock), and the balancing amounts remain in **Temporary Opening** or were posted twice.",
		"solution": (
			"1. Post party openings with [Opening Invoice Creation Tool](/app/opening-invoice-creation-tool), account openings with a [Journal Entry](/app/journal-entry/new) where **Is Opening** is set to **Yes**, and stock openings with a [Stock Reconciliation](/app/stock-reconciliation/new) whose **Purpose** is **Opening Stock**.\n"
			"2. Use the same opening date for all of them (the day before the first live transaction).\n"
			"3. Run [Trial Balance](/app/query-report/Trial Balance) on that date. The **Temporary Opening** account should be zero once everything is entered.\n"
			"4. If it is not zero, compare it with your old books and look for missing or duplicate entries in [General Ledger](/app/query-report/General Ledger) filtered on **Temporary Opening**.\n\n"
			"**Check:** **Temporary Opening** shows a zero balance and the Trial Balance totals match your previous books."
		),
	},
	{
		"id": "acc-bank-reconciliation-not-matching",
		"title": "Bank reconciliation does not match the bank statement",
		"errors": [
			"bank reconciliation",
			"bank balance not matching",
			"clearance date",
			"bank transaction unmatched",
			"no matching vouchers",
			"no matching bank transactions found",
		],
		"tags": "bank reconciliation brs not matching statement clearance date bank transaction import unmatched cheque passbook",
		"doctypes": ["Bank Reconciliation Tool", "Bank Transaction", "Bank Statement Import", "Bank Clearance", "Bank Account"],
		"cause": "Payments in ERPNext have no **Clearance Date**, were posted to a different bank account, or the bank statement has entries (charges, interest) not yet recorded.",
		"solution": (
			"1. Import the statement with [Bank Statement Import](/app/bank-statement-import), linked to the right [Bank Account](/app/bank-account).\n"
			"2. Open [Bank Reconciliation Tool](/app/bank-reconciliation-tool). Select the **Bank Account**, **From Date** and **To Date**, and enter the **Closing Balance** from the bank statement.\n"
			"3. Match each bank line with its Payment Entry or Journal Entry. For unrecorded charges, create the entry from the tool.\n"
			"4. For simple cases, set **Clearance Date** in [Bank Clearance](/app/bank-clearance).\n"
			"5. Review [Bank Reconciliation Statement](/app/query-report/Bank Reconciliation Statement).\n\n"
			"**Check:** The difference in the Bank Reconciliation Tool is zero."
		),
	},
	{
		"id": "acc-tds-not-deducted",
		"title": "TDS is not deducted on a purchase invoice or payment",
		"errors": [
			"tds not deducted",
			"tax withholding",
			"tds not applied",
			"tax withholding category",
			"tds missing",
		],
		"tags": "tds not deducted tax withholding category 194c 194j threshold supplier purchase invoice payment lower deduction certificate kata nahi",
		"doctypes": ["Tax Withholding Category", "Supplier", "Purchase Invoice", "Payment Entry", "Lower Deduction Certificate"],
		"cause": "TDS is applied only when the supplier has a **Tax Withholding Category**, the document has **Consider for Tax Withholding** ticked, and the single-transaction or cumulative threshold is crossed.",
		"solution": (
			"1. Open [Tax Withholding Category](/app/tax-withholding-category). In the **Rates** table, check that a row's **From Date** and **To Date** cover the posting date, and review its **Tax Withholding Rate**, **Transaction Threshold** and **Cumulative Threshold**. In the **Accounts** table, check that your company has an account.\n"
			"2. On the [Supplier](/app/supplier), set **Tax Withholding Category**.\n"
			"3. On the [Purchase Invoice](/app/purchase-invoice) or [Payment Entry](/app/payment-entry), tick **Consider for Tax Withholding**.\n"
			"4. To deduct below the threshold, tick **Ignore Tax Withholding Threshold**.\n"
			"5. If a [Lower Deduction Certificate](/app/lower-deduction-certificate) exists for the supplier, the lower rate is used.\n\n"
			"**Check:** The document shows TDS in the **Tax Withholding Entries** table or the taxes table, and the deduction appears in [Tax Withholding Details](/app/query-report/Tax Withholding Details)."
		),
	},
	{
		"id": "acc-customer-credit-limit-crossed",
		"title": "Credit limit crossed for a customer",
		"errors": [
			"credit limit has been crossed",
			"credit limit has been crossed for customer",
			"credit limit crossed",
			"credit limit",
			"overdue limit",
		],
		"tags": "credit limit crossed customer outstanding bypass credit limit check sales order invoice udhaar seema",
		"doctypes": ["Customer", "Customer Group", "Sales Order", "Sales Invoice", "Accounts Settings"],
		"cause": "The customer's outstanding amount plus this document is more than the **Credit Limit** set for the company on the customer or customer group.",
		"solution": (
			"1. Open the [Customer](/app/customer), go to the **Accounting** tab and find the **Credit & Overdue Limits** table.\n"
			"2. In the row for your company, increase **Credit Limit**, or tick **Bypass credit limit check at sales order** to allow orders and check only at invoice.\n"
			"3. Users with the role set in **Role allowed to bypass credit limit** in [Accounts Settings](/app/accounts-settings) can submit beyond the limit.\n"
			"4. Collect payment and review dues in [Accounts Receivable](/app/query-report/Accounts Receivable).\n\n"
			"**Check:** The order or invoice submits without the credit limit message."
		),
	},
	{
		"id": "acc-gst-accounts-not-set",
		"title": "GST accounts are not set in GST Settings",
		"errors": [
			"gst accounts",
			"please set gst accounts",
			"not a valid gst account",
			"gst account not found",
		],
		"tags": "gst accounts settings input output cgst sgst igst cess account not set gst settings accounts table",
		"doctypes": ["GST Settings", "GST Account", "Account"],
		"cause": "India Compliance identifies GST rows using the **Accounts** table in GST Settings. If the company's input and output accounts are not listed, taxes cannot be validated or reported.",
		"solution": (
			"1. Open [GST Settings](/app/gst-settings) and go to the **Accounts** tab.\n"
			"2. In the **Accounts** table, add rows for your company with **Account Type** set to **Input** (purchases), **Output** (sales), **Purchase Reverse Charge** and **Sales Reverse Charge**. In each row, set **CGST Account**, **SGST / UTGST Account**, **IGST Account** and **Cess Account**.\n"
			"3. Make sure the tax templates use exactly these accounts.\n"
			"4. Save and reload the invoice.\n\n"
			"**Check:** The invoice saves, and [GST Balance](/app/query-report/GST Balance) shows the GST accounts."
		),
	},
	{
		"id": "acc-supplier-invoice-duplicate",
		"title": "Supplier invoice number already exists",
		"errors": [
			"supplier invoice no exists in purchase invoice",
			"supplier invoice no",
			"bill no already exists",
			"duplicate supplier invoice",
		],
		"tags": "supplier invoice number duplicate bill no exists purchase invoice unique check twice entry dobara",
		"doctypes": ["Purchase Invoice", "Accounts Settings"],
		"cause": "**Check Supplier invoice number uniqueness** is on in Accounts Settings, and another Purchase Invoice from the same supplier already uses this **Supplier Invoice No**.",
		"solution": (
			"1. Search [Purchase Invoice](/app/purchase-invoice) for the same **Supplier Invoice No** and supplier to see if the bill was already entered.\n"
			"2. If it is a true duplicate, do not submit the new one.\n"
			"3. If the earlier invoice is wrong, cancel it and amend it.\n"
			"4. If your suppliers reuse numbers across years, review the setting in [Accounts Settings](/app/accounts-settings).\n\n"
			"**Check:** Only one Purchase Invoice exists for that supplier bill number."
		),
	},
]
