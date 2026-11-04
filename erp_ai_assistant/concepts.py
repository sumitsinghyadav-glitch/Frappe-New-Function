"""Concept entries for the offline Help Guide.

Each entry explains how ERPNext v16 works internally (data model, ledgers,
settings and customisation) for business users and implementers. The Help
Guide matches questions against title, tags and doctypes, and shows the body
as Markdown. Names were verified against the live v16 system (read-only).
"""

CONCEPTS = [
	{
		"id": "doctype-document-model",
		"title": "DocTypes and the Document Model",
		"tags": "doctype document model data structure table database schema field column child table parent parenttype parentfield tab table name kya hai structure kaise store hota hai data model erpnext internal",
		"doctypes": ["DocType", "DocField", "Customize Form"],
		"body": """Everything in ERPNext is built on **DocTypes**. A DocType is a definition of a type of record, such as **Sales Invoice**, **Item** or **Employee**.

**How it is stored:**
- Each DocType has its own database table named `tab<DocType Name>`. For example, Sales Invoice records live in `tabSales Invoice` and items in `tabItem`.
- Each field on the form becomes a column in that table (for example `customer`, `posting_date`, `grand_total`).
- Every row has standard columns: `name` (primary key), `owner`, `creation`, `modified`, `modified_by`, `docstatus` and `idx`.

**Child tables:** Grid sections such as the **Items** table on a Sales Invoice are separate DocTypes marked **Is Child Table**. Their rows live in their own table (for example `tabSales Invoice Item`) and point back to the parent through three columns:
- `parent` = name of the parent document (for example `SINV-26-00005`)
- `parenttype` = parent DocType (`Sales Invoice`)
- `parentfield` = field name of the grid (`items`)

**Single DocTypes:** Settings screens such as [Stock Settings](/app/stock-settings) are **Single** DocTypes. They are marked **Is Single**, have one record only, and are stored as key-value rows in `tabSingles`.

**Where the definitions (metadata) live:** the structure of every form is itself stored as data:
- `tabDocType`: one row per DocType (name, module, is single, is submittable, naming rule).
- `tabDocField`: one row per field, with `fieldname`, `label`, `fieldtype` (Data, Link, Table, Check…), `options` (the linked DocType or select values), `reqd` and display rules.
- `tabDocPerm`: the role permissions of each DocType (read, write, create, submit, cancel).
- Changes made for your company are kept separately so upgrades do not overwrite them: new fields in `tabCustom Field` and changed properties in `tabProperty Setter`.

**Where to see it:** Open [DocType](/app/doctype) to view a definition, or [Customize Form](/app/customize-form) to see all fields of a form with their types.

**Example:** A Sales Invoice with 3 items creates 1 row in `tabSales Invoice`, 3 rows in `tabSales Invoice Item` and one row per tax line in `tabSales Taxes and Charges`.""",
	},
	{
		"id": "link-and-dynamic-link",
		"title": "Link Fields and Dynamic Links",
		"tags": "link field dynamic link foreign key relation relationship reference party_type party reference_doctype reference_name connection linked document kaise jude hain",
		"doctypes": ["DocField", "Contact", "Address", "Payment Entry"],
		"body": """**Link field:** A field that stores the `name` of a record in another DocType. It works like a foreign key. For example, **Customer** on a Sales Order is a Link to the Customer DocType. The field stores the customer ID, and the form fetches related details.

**Dynamic Link:** A pair of fields where the first field holds a DocType name and the second holds a record of that DocType. The target DocType can change per record.
- In [Payment Entry](/app/payment-entry), **Party Type** (Customer, Supplier, Employee) decides what **Party** points to.
- In [Journal Entry](/app/journal-entry) accounts rows, **Reference Type** and **Reference Name** link to an invoice or order.
- [Address](/app/address) and [Contact](/app/contact) use a **Links** child table with **Link Document Type** and **Link Name**, so one address can belong to several customers or suppliers.

**Why it matters:**
1. You cannot delete a record that is linked from another record. ERPNext shows "Cannot delete or cancel because ... is linked with ...".
2. Renaming a record updates every Link field that points to it.
3. The **Connections** tab on a form lists linked documents.

**Fetch From:** A field can copy a value from a linked record (for example **Customer Name** fetched from **Customer**).""",
	},
	{
		"id": "naming-series-and-autoname",
		"title": "Document Naming, Naming Series and Autoname",
		"tags": "naming series name id primary key autoname document number prefix format SINV PUR-ORD .YY. .#### series reset change number kaise badle numbering rename",
		"doctypes": ["Document Naming Settings", "Document Naming Rule", "DocType"],
		"body": """Every document has a unique **ID** stored in the `name` column. It is the primary key of the table.

**How the name is set (autoname):**
- **Naming Series:** a pattern such as `PUR-ORD-.YYYY.-` followed by a counter. Example: `PUR-ORD-2026-00017`.
- **By field:** the value of a field, for example **Item Code** for Items or **Leave Type Name** for Leave Types.
- **Prompt:** the user types the name.
- **Hash:** a random ID.
- **Expression:** a format such as `format:HOST-{#####}`.

**Where to manage it:**
1. Open [Document Naming Settings](/app/document-naming-settings).
2. In **Select Transaction**, choose the document type (for example Sales Invoice).
3. Edit the **Series List for this Transaction**, or change the current counter value of a prefix.
4. Use [Document Naming Rule](/app/document-naming-rule) to apply a different series based on conditions, for example one series per branch or company.

**Counters** are stored in `tabSeries` (one row per prefix with its current number).

**Notes:**
- An amended document gets a suffix, for example `SINV-26-00005-1`.
- Renaming is possible only when the DocType allows it, through the title menu **Rename**.""",
	},
	{
		"id": "docstatus-draft-submit-cancel-amend",
		"title": "Document Status: Draft, Submitted, Cancelled and Amend",
		"tags": "docstatus draft submitted cancelled cancel amend amendment submit kya hota hai 0 1 2 edit after submit cannot edit submitted document badalna",
		"doctypes": ["Sales Invoice", "Purchase Invoice", "Stock Entry", "Journal Entry"],
		"body": """Transaction DocTypes that are **Submittable** follow a three-state life cycle, stored in the `docstatus` column:

| docstatus | Status | Meaning |
|---|---|---|
| 0 | Draft | Saved but not final. You can edit or delete it. No ledger entries exist. |
| 1 | Submitted | Final. Ledger entries (stock, GL, payment) are posted. Most fields are locked. |
| 2 | Cancelled | Reversed. Ledger entries are cancelled or reversed. The record is kept for audit. |

**Amend:**
1. Cancel the submitted document.
2. Click **Amend**. A new draft is created with a name such as `SINV-26-00005-1`, linked through the **Amended From** field.
3. Correct it and submit again.

**Allow on Submit:** Some fields (for example remarks or certain dates) can be edited after submission because they are marked **Allow on Submit**.

**Cancel order:** You must cancel dependent documents first. For example, cancel the Sales Invoice before the Delivery Note it was created from. Payments are unlinked from a cancelled invoice automatically when **Unlink Payment on cancellation of invoice** is ticked in [Accounts Settings](/app/accounts-settings).

The visible **Status** field (for example "Unpaid", "To Bill", "Completed") is a separate business status computed from the document. It is not the same as `docstatus`.""",
	},
	{
		"id": "stock-ledger-entry",
		"title": "Stock Ledger Entry: How Stock Movements Are Recorded",
		"tags": "stock ledger entry sle stock movement inward outward actual_qty qty_after_transaction valuation stock history maal ka record kahan store hota hai stock kaise calculate hota hai",
		"doctypes": ["Stock Ledger Entry", "Stock Entry", "Purchase Receipt", "Delivery Note"],
		"body": """Every stock movement creates one row in **Stock Ledger Entry** (table `tabStock Ledger Entry`) per item, warehouse and transaction line.

**Created by:** Purchase Receipt, Delivery Note, Stock Entry, Stock Reconciliation, and Sales or Purchase Invoices with **Update Stock** ticked.

**Key columns:**
- `item_code`, `warehouse`, `posting_date`, `posting_time`
- `actual_qty`: positive for inward, negative for outward
- `qty_after_transaction`: running balance in that warehouse
- `incoming_rate`, `valuation_rate`, `stock_value`, `stock_value_difference`
- `voucher_type`, `voucher_no`: the source document
- `is_cancelled`: set to 1 when the source document is cancelled

**How to see it:**
- [Stock Ledger](/app/query-report/Stock Ledger) for item-wise movement history.
- [Stock Balance](/app/query-report/Stock Balance) for opening, in, out and closing quantities and values.
- From any submitted stock document, use **View > Stock Ledger**.

**Example:** Receiving 10 pipes into *Gwalior Plant - Ssy* creates an SLE with `actual_qty = 10`. Transferring 4 to *Indore Depot - Ssy* creates two SLEs: -4 in Gwalior and +4 in Indore.

Stock Ledger Entries are never edited by hand. To correct stock, cancel and amend the source document or use a Stock Reconciliation.""",
	},
	{
		"id": "bin-current-stock",
		"title": "Bin: Current Stock per Item and Warehouse",
		"tags": "bin actual qty projected qty reserved qty ordered qty current stock available stock kitna hai item warehouse balance stock summary",
		"doctypes": ["Bin", "Item", "Warehouse"],
		"body": """**Bin** (table `tabBin`) holds one row per **Item + Warehouse** combination. It is a fast summary of the current position, updated whenever stock or orders change.

**Main quantities:**
- **Actual Qty:** physical stock now (from Stock Ledger Entries).
- **Ordered Qty:** on open Purchase Orders, not yet received.
- **Reserved Qty:** on open Sales Orders, not yet delivered.
- **Requested Qty:** on open Material Requests.
- **Planned Qty:** to be produced by open Work Orders.
- **Reserved Qty for Production**, **Reserved Qty for Subcontract** and **Reserved Qty for Production Plan:** raw materials needed by Work Orders, subcontracting and Production Plans.
- **Projected Qty** = Actual + Ordered + Requested + Planned - Reserved - Reserved for Production - Reserved for Subcontract - Reserved for Production Plan.

**How to see it:**
- The [Stock Summary](/app/stock-balance) page, or the **Stock Levels** section on the Item form.
- [Stock Projected Qty](/app/query-report/Stock Projected Qty) report.
- [Item Balance (Simple)](/app/query-report/Item Balance %28Simple%29) reads the balance quantity directly from Bin.

**Note:** The Stock Ledger is the source of truth. Bin is a cached total. If they ever disagree, the system can recalculate Bin from the ledger.""",
	},
	{
		"id": "valuation-methods-fifo-moving-average",
		"title": "Valuation Methods: FIFO, Moving Average and LIFO",
		"tags": "valuation method fifo moving average lifo stock queue valuation rate cost of goods sold rate kaise nikalta hai stock value item valuation",
		"doctypes": ["Stock Settings", "Item", "Stock Ledger Entry"],
		"body": """The valuation method decides the cost at which stock leaves a warehouse.

**Methods available:**
- **FIFO (First In, First Out):** the oldest purchase cost is used first. ERPNext keeps a `stock_queue` on each Stock Ledger Entry, a list of [quantity, rate] lots still in stock.
- **Moving Average:** each receipt recalculates one average rate. Outward entries use that average.
- **LIFO:** the latest cost is used first.

**Where to set it:**
1. System default: [Stock Settings](/app/stock-settings) > **Default Valuation Method**.
2. Per item: **Valuation Method** field on the [Item](/app/item). This overrides the default.
3. You cannot change an item's method after it has stock transactions.

**Example (FIFO):** Receive 10 at 100, then 10 at 120. Issue 15. Cost = 10 x 100 + 5 x 120 = 1,600. The queue keeps 5 at 120.

**Example (Moving Average):** Same receipts give an average of 110. Issue 15 costs 1,650.

**Batch items** may use batch-wise valuation unless **Do not use Batch-wise Valuation** is ticked in Stock Settings.

Check rates in [Stock Ledger](/app/query-report/Stock Ledger) (**Valuation Rate** column).""",
	},
	{
		"id": "perpetual-inventory-accounts",
		"title": "Perpetual Inventory and Stock Accounts",
		"tags": "perpetual inventory stock in hand stock received but not billed srbnb inventory account stock adjustment account accounting of stock stock gl entry stock value mismatch",
		"doctypes": ["Company", "Warehouse", "Account", "Purchase Receipt"],
		"body": """With **Perpetual Inventory**, every stock transaction also posts accounting entries, so the stock value in the books always matches the stock ledger.

**Settings:** On the [Company](/app/company): **Enable Perpetual Inventory**, **Default Inventory Account**, **Stock Received But Not Billed** and **Stock Adjustment Account**. A Warehouse can have its own **Account**.

**How the entries flow (purchase):**
1. **Purchase Receipt:** Debit *Stock In Hand* (inventory account), Credit *Stock Received But Not Billed* (SRBNB).
2. **Purchase Invoice:** Debit *SRBNB*, Credit *Supplier (Creditors)*, plus GST input accounts.
3. After both, SRBNB nets to zero for that purchase.

**Sales:** A Delivery Note posts Debit *Cost of Goods Sold*, Credit *Stock In Hand*. The Sales Invoice posts income and debtors.

**Stock Adjustment Account** absorbs differences from Stock Reconciliation and valuation corrections.

**How to check:**
- [Stock and Account Value Comparison](/app/query-report/Stock and Account Value Comparison)
- [General Ledger](/app/query-report/General Ledger) filtered by the inventory or SRBNB account.

A growing SRBNB balance usually means receipts that were never invoiced.""",
	},
	{
		"id": "gl-entry-general-ledger",
		"title": "GL Entry and the General Ledger",
		"tags": "gl entry general ledger accounting entry debit credit voucher journal ledger posting kahan dikhega account balance trial balance books of accounts",
		"doctypes": ["GL Entry", "Journal Entry", "Account"],
		"body": """Every submitted accounting transaction creates rows in **GL Entry** (table `tabGL Entry`). This is the general ledger.

**Created by:** Sales and Purchase Invoices, Payment Entry, Journal Entry, Purchase Receipt and Delivery Note (with perpetual inventory), Stock Entry, Asset depreciation, Payroll Entry, Expense Claim and more.

**Key columns:** `account`, `debit`, `credit`, `party_type`, `party`, `cost_center`, `posting_date`, `voucher_type`, `voucher_no`, `against_voucher`, `company`, `is_cancelled`, and any accounting dimensions.

**Rules:**
- Total debit equals total credit for each voucher.
- Entries are never edited. Cancelling a voucher marks its entries cancelled and posts reverse entries.

**How to see it:**
- [General Ledger](/app/query-report/General Ledger): filter by account, party or voucher.
- [Trial Balance](/app/query-report/Trial Balance), [Balance Sheet](/app/query-report/Balance Sheet), [Profit and Loss Statement](/app/query-report/Profit and Loss Statement).
- From a submitted document: **View > Accounting Ledger**.

**Example:** A Sales Invoice of 1,000 plus 18% GST posts Debit Debtors 1,180, Credit Sales 1,000, Credit Output CGST 90 and Output SGST 90.""",
	},
	{
		"id": "payment-ledger-entry-outstanding",
		"title": "Payment Ledger Entry and Outstanding Amounts",
		"tags": "payment ledger entry outstanding amount receivable payable reconciliation unpaid invoice due kitna baki hai advance allocation party balance ple",
		"doctypes": ["Payment Ledger Entry", "Payment Entry", "Payment Reconciliation"],
		"body": """**Payment Ledger Entry** (table `tabPayment Ledger Entry`) tracks what each party owes or is owed, invoice by invoice. ERPNext uses it to calculate **Outstanding Amount** on invoices and in receivable and payable reports.

**How it works:**
- An invoice creates a row against itself (positive for receivables).
- A payment or credit note creates a row with `against_voucher_no` = the invoice, reducing its outstanding.
- An unallocated advance stays against the payment itself until it is reconciled.

**Key columns:** `party_type`, `party`, `account`, `voucher_type`, `voucher_no`, `against_voucher_type`, `against_voucher_no`, `amount`, `due_date`, `delinked`.

**How to see it:**
- [Accounts Receivable](/app/query-report/Accounts Receivable) and [Accounts Payable](/app/query-report/Accounts Payable)
- [Payment Ledger](/app/query-report/Payment Ledger)
- [General and Payment Ledger Comparison](/app/query-report/General and Payment Ledger Comparison) to find mismatches.

**Linking payments to invoices:** Use [Payment Reconciliation](/app/payment-reconciliation) to allocate advances and unlinked payments against invoices.

If outstanding looks wrong, use [Repost Payment Ledger](/app/repost-payment-ledger) to rebuild it.""",
	},
	{
		"id": "repost-item-valuation-backdated",
		"title": "Repost Item Valuation and Backdated Entries",
		"tags": "repost item valuation backdated entry back date purchase receipt stock value recalculate reposting queued pending riv purani date entry valuation galat",
		"doctypes": ["Repost Item Valuation", "Stock Reposting Settings", "Stock Ledger Entry"],
		"body": """When you post or cancel a stock transaction with a **past date**, every later stock entry for that item and warehouse may have a wrong balance or valuation. ERPNext fixes this with **Repost Item Valuation** (RIV).

**How it works:**
1. A backdated or cancelled stock transaction creates a [Repost Item Valuation](/app/repost-item-valuation) record with status **Queued**.
2. A background job recalculates `qty_after_transaction`, valuation rates and stock values for all later Stock Ledger Entries.
3. It then reposts the related GL Entries so accounts match stock.
4. Status changes to **In Progress**, then **Completed**, or **Failed** with an error log.

**Settings:** [Stock Reposting Settings](/app/stock-reposting-settings) controls when reposting runs (**Limit timeslot for Stock Reposting**, **Start Time**, **End Time**), **Enable Parallel Reposting**, and **Notify Reposting Error to Role**.

**Check:**
- Open [Repost Item Valuation](/app/repost-item-valuation) and filter **Status = Queued** or **Failed**.
- Reports may show old values until the queue finishes.

**Tip:** Avoid backdated entries where possible. Many backdated entries on busy items create long reposting queues.""",
	},
	{
		"id": "chart-of-accounts-account-types",
		"title": "Chart of Accounts and Account Types",
		"tags": "chart of accounts coa account tree group ledger account type root type asset liability income expense equity receivable payable bank cash naya account kaise banaye",
		"doctypes": ["Account", "Company"],
		"body": """The **Chart of Accounts** is a tree of [Account](/app/account) records per company, stored in `tabAccount`.

**Structure:**
- **Root Type:** Asset, Liability, Equity, Income or Expense. It decides where the account appears in the Balance Sheet or Profit and Loss.
- **Is Group:** group accounts organise the tree. Only non-group (ledger) accounts can be used in transactions.
- **Account Type:** special behaviour, for example **Receivable**, **Payable**, **Bank**, **Cash**, **Stock**, **Tax**, **Cost of Goods Sold**, **Stock Received But Not Billed**, **Fixed Asset**, **Depreciation**, **Accumulated Depreciation**, **Round Off**, **Chargeable**.

**Why Account Type matters:**
- Receivable and Payable accounts require a **Party** on every entry.
- Bank and Cash accounts appear in Payment Entry mode of payment.
- Tax accounts appear in tax templates.

**How to view or edit:** Open [Chart of Accounts](/app/account/view/tree), select the company, then add a child account under the right group.

**Example:** Add "Freight Inward" under *Direct Expenses* with Account Type **Chargeable** to use it in purchase taxes and charges.""",
	},
	{
		"id": "cost-center-accounting-dimensions",
		"title": "Cost Centers and Accounting Dimensions",
		"tags": "cost center accounting dimension branch department project dimension profit center segment reporting dimension wise report vibhag",
		"doctypes": ["Cost Center", "Accounting Dimension", "Accounting Dimension Filter"],
		"body": """**Cost Center** is a built-in dimension for income and expense analysis. Each GL Entry for an income or expense account carries a `cost_center`.

**Accounting Dimension** lets you add your own dimensions, such as **Branch**, **Department** or **Project**.

**How dimensions work:**
1. Create one in [Accounting Dimension](/app/accounting-dimension) and choose the **Reference Document Type** (for example Branch).
2. ERPNext adds a custom field for that dimension to transactions and to `tabGL Entry`.
3. Every GL Entry then stores the dimension value.
4. Use [Accounting Dimension Filter](/app/accounting-dimension-filter) to restrict which values are allowed with which accounts.

**Difference:**
- Cost Center is a tree, supports budgets and cost allocation.
- Accounting Dimensions are flexible tags for reporting. You can mark them mandatory for Balance Sheet or Profit and Loss accounts.

**Reports:**
- [Dimension-wise Accounts Balance Report](/app/query-report/Dimension-wise Accounts Balance Report)
- [Profit and Loss Statement](/app/query-report/Profit and Loss Statement) filtered by cost center or dimension.""",
	},
	{
		"id": "fiscal-year-accounting-period",
		"title": "Fiscal Year, Accounting Period and Frozen Accounts",
		"tags": "fiscal year financial year accounting period close period lock period frozen accounts till date period closing voucher year end closing april march saal band karna",
		"doctypes": ["Fiscal Year", "Accounting Period", "Period Closing Voucher", "Company"],
		"body": """**Fiscal Year:** [Fiscal Year](/app/fiscal-year) defines the financial year (for India, 1 April to 31 March). Every posting date must fall in a fiscal year that exists for the company.

**Accounting Period:** [Accounting Period](/app/accounting-period) closes a date range for selected document types. List the document types in **Closed Documents**. ERPNext then blocks new or cancelled entries in that range for those documents, except for the **Exempted Role**. Use it for monthly GST closing.

**Accounts Frozen Till Date:** On the [Company](/app/company), **Accounts Frozen Till Date** blocks accounting entries on or before that date. Only users with the role set in **Roles Allowed to Set and Edit Frozen Account Entries** can post in that range.

**Period Closing Voucher:** [Period Closing Voucher](/app/period-closing-voucher) transfers the Profit and Loss balance to a retained earnings (equity) account at year end.

**Common error:** "Date ... is not in any active Fiscal Year". Create the next fiscal year. If the **Companies** table on the fiscal year is filled, add your company to it.""",
	},
	{
		"id": "company-multi-company-inter-company",
		"title": "Company, Multi-Company and Inter-Company Transactions",
		"tags": "company multi company group company parent company inter company internal customer internal supplier subsidiary consolidated sister concern dusri company",
		"doctypes": ["Company", "Customer", "Supplier"],
		"body": """Almost every transaction and master (Account, Warehouse, Cost Center) belongs to one [Company](/app/company). Each company has its own chart of accounts, defaults and books.

**Multi-company:**
- One site can hold several companies. Use **Is Group** and **Parent Company** to build a group tree.
- Reports have a **Company** filter. [Consolidated Trial Balance](/app/query-report/Consolidated Trial Balance) and the consolidated financial statement combine group companies.
- Use User Permissions on Company to restrict users to one company.

**Inter-company transactions:**
1. Mark a [Customer](/app/customer) as **Is Internal Customer** and select the company in **Represents Company**.
2. Mark a [Supplier](/app/supplier) as **Is Internal Supplier** in the same way.
3. A Sales Invoice to the internal customer can then create the matching Purchase Invoice in the other company.
4. Inter-company Journal Entries are also supported.

In this system the company is **Sumit**.""",
	},
	{
		"id": "multi-gstin-branches-internal-transfer",
		"title": "Multi-GSTIN Branches and Internal Stock Transfers",
		"tags": "multi gstin branch gstin company address internal transfer stock transfer between branches delivery note internal customer gst on transfer state to state transfer gwalior indore",
		"doctypes": ["Address", "Customer", "Supplier", "Delivery Note", "Stock Entry"],
		"body": """One company can have several **GSTINs**, one per state registration. In ERPNext, each GSTIN is stored on a company [Address](/app/address) (fields **GSTIN / UIN** and **GST State**). Transactions select the **Company Address**, and that sets the company GSTIN.

**Transfers between branches:**
- **Same GSTIN (same state):** use a [Stock Entry](/app/stock-entry/new) of type **Material Transfer**. No GST applies.
- **Different GSTINs:** GST law treats this as a supply. Use an internal sale:
  1. Create an internal [Customer](/app/customer) with **Is Internal Customer** ticked and your own company in **Represents Company**. Create an internal [Supplier](/app/supplier) in the same way.
  2. Create a **Delivery Note** or **Sales Invoice** from the sending branch to that customer, with the receiving branch address. GST is charged.
  3. Create the **Purchase Receipt** or **Purchase Invoice** at the receiving branch against the internal supplier. Input tax credit is taken.

**Goods in transit:** Internal transfers can move stock into a transit warehouse until received.

**Rate:** By default internal transfers use valuation rate. [Stock Settings](/app/stock-settings) > **Allow internal transfers at user-defined rate** allows a different rate.""",
	},
	{
		"id": "taxes-templates-tax-category",
		"title": "Taxes: Tax Templates, Item Tax Templates and Tax Category",
		"tags": "tax template sales taxes and charges template purchase taxes and charges template item tax template tax category tax rule gst rate kaise lagta hai igst cgst sgst 5 12 18 28 40",
		"doctypes": ["Sales Taxes and Charges Template", "Purchase Taxes and Charges Template", "Item Tax Template", "Tax Category", "Tax Rule"],
		"body": """Taxes are applied in layers:

1. **Taxes and Charges Template** ([Sales](/app/sales-taxes-and-charges-template), [Purchase](/app/purchase-taxes-and-charges-template)): a list of tax accounts and rates, for example *Output Tax CGST 9%* and *Output Tax SGST 9%*. It fills the **Taxes and Charges** table of a transaction.
2. **Item Tax Template** ([Item Tax Template](/app/item-tax-template)): an item-level rate per tax account, for example *GST 5%*. Set it on the Item or Item Group under **Taxes**. It overrides the template rate for that item line.
3. **Tax Category** ([Tax Category](/app/tax-category)): a label such as *In-State*, *Out-State* or *Reverse Charge*. Templates and item tax rows are linked to a category, so the right one is picked.
4. **Tax Rule** ([Tax Rule](/app/tax-rule)): chooses a template automatically based on party, address or category.

**Stored in:** `tabSales Taxes and Charges` / `tabPurchase Taxes and Charges` (child rows on each document). The item-wise breakup is saved in **Item Wise Tax Detail** rows.

**Example:** An item with Item Tax Template *GST 18%*, sold within the state, gets CGST 9% and SGST 9%. Sold to another state, it gets IGST 18%.""",
	},
	{
		"id": "gst-place-of-supply",
		"title": "GST Place of Supply, Intra-State and Inter-State",
		"tags": "gst place of supply pos intra state inter state igst cgst sgst state code gst category registered unregistered sez export reverse charge kaun sa gst lagega",
		"doctypes": ["Sales Invoice", "Address", "Customer", "GST Settings"],
		"body": """The India Compliance app decides which GST applies by comparing two states:

- **Company GSTIN state:** from the **Company Address**.
- **Place of Supply:** usually the customer's billing or shipping address state, shown in the **Place of Supply** field (for example `23-Madhya Pradesh`).

**Rule:**
- Same state: **CGST + SGST** (intra-state).
- Different states: **IGST** (inter-state).
- SEZ and exports: IGST, or zero-rated with or without payment of tax.

**Inputs that matter:**
1. **GST Category** on the Customer or Supplier and address (for example Registered Regular, Registered Composition, Unregistered, SEZ, Overseas).
2. **GSTIN / UIN** and **GST State** on the addresses.
3. The **Tax Category** and tax template, which India Compliance sets automatically when the addresses are correct.

**Settings:** [GST Settings](/app/gst-settings) controls e-Invoice, e-Waybill, reverse charge and validation behaviour.

**Reports:** [GSTR-1](/app/gstr-1) for outward supply, [GST Balance](/app/query-report/GST Balance) for tax account balances.

**Common issue:** Wrong tax type on an invoice usually means the customer address has the wrong state or GSTIN.""",
	},
	{
		"id": "price-list-item-price-pricing-rule",
		"title": "Price Lists, Item Prices and Pricing Rules",
		"tags": "price list item price pricing rule discount rate selling price buying price standard selling standard buying margin scheme rate kaise aata hai daam",
		"doctypes": ["Price List", "Item Price", "Pricing Rule", "Promotional Scheme"],
		"body": """**Price List** ([Price List](/app/price-list)): a named list such as *Standard Selling* or *Standard Buying*, with a currency and a flag for buying, selling or both.

**Item Price** ([Item Price](/app/item-price)): one row per item, price list and optionally UOM, customer or supplier, and validity dates. Stored in `tabItem Price`.

**Pricing Rule** ([Pricing Rule](/app/pricing-rule)): conditions that change the rate or give a discount or free item. Conditions can be item, item group, brand, customer, territory, quantity range or date range.

**How the rate is set on a transaction:**
1. The **Price List Rate** is fetched from Item Price for the selected price list.
2. Applicable Pricing Rules are applied (discount percentage, discount amount, or a fixed rate).
3. The result is the **Rate**. A user can override it if allowed.

**When several Pricing Rules match the same item and customer:**
- Rules outside the quantity or amount range are dropped, then the rule with the highest **Priority** (a number set on the rule; higher wins) is kept.
- If more than one is left, the more specific rule wins (for example a rule for the item code beats one for its item group; a rule for the customer beats one for the customer group or territory).
- If they still tie, the transaction stops with *Multiple Price Rules exists with same criteria*: set different priorities to resolve it.
- **Apply Multiple Pricing Rules** (on the rule, under **Advanced Settings**): tick it on rules that should stack, so their discounts apply one after another instead of only the winner.

**Settings:** [Stock Settings](/app/stock-settings) has **Auto insert Item Price if missing** and **Update existing Price List Rate**.

**Example:** Item Price 500 on *Standard Selling*. A Pricing Rule gives 10% for 100 units or more. An order of 120 units gets a rate of 450.""",
	},
	{
		"id": "uom-conversion-factor",
		"title": "Units of Measure and Conversion Factor",
		"tags": "uom unit of measure stock uom conversion factor box piece kg nos meter purchase uom sales uom stock qty unit badalna conversion",
		"doctypes": ["UOM", "UOM Conversion Factor", "Item"],
		"body": """**Stock UOM** is the unit in which an item's stock is kept, for example *Nos* or *Kg*. On the Item it is the **Default Unit of Measure** field. All Stock Ledger Entries use this unit.

**Transaction UOM** can be different. Each item line has **UOM**, **UOM Conversion Factor** and **Qty as per Stock UOM**:
- **Qty as per Stock UOM** = **Qty** x **UOM Conversion Factor**.

**Where to set conversions:**
1. On the [Item](/app/item), open the **UOM** tab and add each UOM with its conversion factor to the stock UOM.
2. General conversions between UOMs (for example Kg to Gram) are in [UOM Conversion Factor](/app/uom-conversion-factor).
3. Set **Default Purchase Unit of Measure** and **Default Sales Unit of Measure** on the item if needed.

**Settings:** [Stock Settings](/app/stock-settings) has **Default Stock UOM** and options such as **Allow to edit stock UOM qty for Sales documents** and **Allow to edit stock UOM qty for Purchase documents**.

**Example:** Stock UOM *Nos*. Purchase UOM *Box* with factor 12. Buying 5 Box adds 60 Nos to stock.

**Note:** The stock UOM cannot be changed after the item has transactions. Create a new item instead.""",
	},
	{
		"id": "batch-serial-and-batch-bundle",
		"title": "Batch, Serial Number and Serial and Batch Bundle",
		"tags": "batch serial number serial no serial and batch bundle expiry batch wise stock serialised item tracking has batch no has serial no lot number imei",
		"doctypes": ["Batch", "Serial No", "Serial and Batch Bundle", "Item"],
		"body": """**Batch** tracks a lot of an item, often with an expiry date. **Serial No** tracks each single unit.

**Enable on the Item:** tick **Has Batch No** and/or **Has Serial No**, and optionally set naming series and **Has Expiry Date**.

**Serial and Batch Bundle (v15 and v16):**
- Transactions no longer store serial or batch numbers in a text field. Each item line links to a [Serial and Batch Bundle](/app/serial-and-batch-bundle) record.
- The bundle has an entries table (`tabSerial and Batch Entry`) listing each serial or batch with its quantity and rate.
- The Stock Ledger Entry stores the bundle in `serial_and_batch_bundle`.

**Settings in [Stock Settings](/app/stock-settings):**
- **Pick Serial / Batch Based On** (FIFO, LIFO, Expiry)
- **Auto create Serial and Batch Bundle for outward**
- **Use Serial / Batch fields** to show the simple fields on forms
- **Allow negative stock for Batch**

**Reports:** [Batch-Wise Balance History](/app/query-report/Batch-Wise Balance History), [Serial No Ledger](/app/query-report/Serial No Ledger), and the [Serial No](/app/serial-no) list.""",
	},
	{
		"id": "warehouse-tree-goods-in-transit",
		"title": "Warehouse Tree and Goods in Transit",
		"tags": "warehouse tree group warehouse transit warehouse goods in transit stores location godown warehouse type parent warehouse material in transit",
		"doctypes": ["Warehouse", "Stock Entry", "Warehouse Type"],
		"body": """[Warehouse](/app/warehouse) records form a tree per company.

**Group and leaf:**
- Warehouses marked **Is Group Warehouse** (for example *All Warehouses - Ssy*) only organise the tree and roll up stock in reports.
- Only leaf warehouses can hold stock and be used in transactions.

**Warehouse Type:** A label such as *Transit*. Set **Default In-Transit Warehouse** on the Company and mark the transit warehouse with **Warehouse Type = Transit**.

**Goods in transit flow:**
1. Create a [Stock Entry](/app/stock-entry/new) of type **Material Transfer** from the source warehouse to the transit warehouse, with **Add to Transit** ticked.
2. When the goods arrive, open that entry and use **End Transit**. This creates a second transfer from transit to the target warehouse.
3. Stock in transit stays visible in [Stock Balance](/app/query-report/Stock Balance) under the transit warehouse.

**Accounting:** With perpetual inventory, each warehouse (or its parent) maps to an inventory account.

**View the tree:** [Warehouse tree](/app/warehouse/view/tree).""",
	},
	{
		"id": "roles-permissions-user-permissions",
		"title": "Roles, Permissions, User Permissions and Permission Levels",
		"tags": "role permission user permission permission level perm level access restrict user role profile not permitted insufficient permission kisko access hai share",
		"doctypes": ["Role", "User", "User Permission", "Role Profile", "Custom DocPerm"],
		"body": """Access in ERPNext has three layers.

**1. Role permissions (what a role can do on a DocType):**
- Set in [Role Permissions Manager](/app/permission-manager).
- Rights include Read, Write, Create, Delete, Submit, Cancel, Amend, Report, Export, Import, Print, Email, Share.
- Stored in `tabDocPerm` (standard) and `tabCustom DocPerm` (your changes).
- Assign roles on the [User](/app/user) form, or through a [Role Profile](/app/role-profile).

**2. User Permissions (which records a user can see):**
- [User Permission](/app/user-permission) restricts a user to specific values, for example **Company = Sumit** or **Warehouse = Gwalior Plant - Ssy**.
- Every document linked to other values is then hidden from that user.

**3. Permission Levels (which fields a role can see or edit):**
- Each field has a **Perm Level** (0 by default). Grant level 1 or higher to selected roles to protect sensitive fields such as rates.

**Other tools:**
- **If Owner:** limits a role to documents the user created.
- **Share:** gives one user access to one document.
- [Permission Inspector](/app/permission-inspector) explains why a user can or cannot access a record.""",
	},
	{
		"id": "workflow-vs-docstatus",
		"title": "Workflow States and Approval vs Document Status",
		"tags": "workflow approval workflow state transition approver pending approval approved rejected workflow action docstatus difference approval kaise lagaye",
		"doctypes": ["Workflow", "Workflow State", "Workflow Action", "Workflow Action Master"],
		"body": """A **Workflow** adds approval steps on top of the standard Draft / Submitted / Cancelled life cycle.

**Parts:**
- [Workflow State](/app/workflow-state): names such as *Pending Approval*, *Approved*, *Rejected*.
- [Workflow](/app/workflow): for one DocType, lists **States** (each mapped to a docstatus 0, 1 or 2 and an editing role) and **Transitions** (from state, action, to state, allowed role, optional condition).
- [Workflow Action](/app/workflow-action): pending approval tasks created for users who can act.

**How it relates to docstatus:**
- The workflow state is stored in a field such as `workflow_state`.
- Each state maps to a docstatus. For example *Pending Approval* = 0 (Draft), *Approved* = 1 (Submitted), *Cancelled* = 2.
- When a workflow is active, the **Submit** button is replaced by the workflow **Actions** menu.

**Example:** Purchase Order: Draft, then *Pending Approval* (Purchase User), then *Approved* by Purchase Manager, which submits the document.

**Leave approval** uses its own **Leave Approver** on the Employee or Department, and can also use a workflow.""",
	},
	{
		"id": "customization-methods",
		"title": "Customization Methods: Custom Field, Property Setter, Scripts and Apps",
		"tags": "customization customize form custom field property setter client script server script custom doctype custom app what is customized kya customize kiya hai change form add field hostel",
		"doctypes": ["Custom Field", "Property Setter", "Customize Form", "Client Script", "Server Script", "DocType"],
		"body": """ERPNext can be changed without editing core code. Each method stores its changes in a different place:

| Method | Use | Stored in |
|---|---|---|
| [Customize Form](/app/customize-form) | Add fields, change labels, hide or require fields on a standard form | Custom Field and Property Setter |
| [Custom Field](/app/custom-field) | A new field on an existing DocType | `tabCustom Field` |
| [Property Setter](/app/property-setter) | Override a property (label, hidden, mandatory, options, default) | `tabProperty Setter` |
| [Client Script](/app/client-script) | JavaScript on the form (validations, auto-fill, buttons) | `tabClient Script` |
| [Server Script](/app/server-script) | Python rules on save, submit, API or schedule | `tabServer Script` |
| Custom DocType | A completely new screen, created in [DocType](/app/doctype) with **Custom?** ticked | `tabDocType` |
| Custom app | Code installed on the site, versioned in Git | App folder on the server |

**Custom screens in this system:** **Hostel**, **Hostel Room**, **Hostel Room Type**, **Hostel Registration** and **Hostel Allocation**.

**How to find what is customized:**
1. Open the [Custom Field](/app/custom-field) and [Property Setter](/app/property-setter) lists and group by **DocType**.
2. Check the [Client Script](/app/client-script) and [Server Script](/app/server-script) lists.
3. Filter the [DocType](/app/doctype) list by **Custom?** ticked.

**Tip:** Prefer Customize Form over editing standard DocTypes, so upgrades do not overwrite your changes.""",
	},
	{
		"id": "report-types",
		"title": "Report Types: Report Builder, Query Report and Script Report",
		"tags": "report builder query report script report custom report save report group by filter export excel naya report kaise banaye report types",
		"doctypes": ["Report"],
		"body": """ERPNext has three report types, all listed in [Report](/app/report):

**1. Report Builder**
- Built from any list view: choose columns, filters, sort and **Group By**, then save with **Save As**.
- Reads one DocType and its child table. No code needed.
- Example: open [Purchase Order](/app/purchase-order/view/report), add **Supplier** and **Grand Total** columns, filter **Status = To Receive and Bill**.

**2. Query Report**
- Defined by a SQL query in the Report record. Only users with the **Script Manager** role can create or edit one.
- Example: [Item Balance (Simple)](/app/query-report/Item Balance %28Simple%29).

**3. Script Report**
- Python code (plus optional JavaScript filters) in an app. Most standard reports are this type, for example [General Ledger](/app/query-report/General Ledger), [Stock Balance](/app/query-report/Stock Balance) and [Accounts Receivable](/app/query-report/Accounts Receivable).

**Common features:** filters, export to Excel or CSV, print, charts, and **Prepared Report** mode for heavy reports, which runs in the background.

**Access:** Each report has a **Roles** table. Users need one of those roles and read access to the reference DocType.""",
	},
	{
		"id": "workspaces-sidebar",
		"title": "Workspaces and the Sidebar",
		"tags": "workspace sidebar desk module home page shortcut number card link menu customize workspace screen kahan milega navigation",
		"doctypes": ["Workspace", "Workspace Sidebar", "Number Card", "Dashboard Chart"],
		"body": """**Workspace:** A page in the desk such as *Accounting*, *Stock* or *HR*. It holds shortcuts, link cards, number cards, charts and quick lists. Stored in [Workspace](/app/workspace) with child tables such as **Workspace Shortcut** and **Workspace Link**.

**Sidebar (v16):** The left sidebar lists workspaces and their links. In v16 it is defined by [Workspace Sidebar](/app/workspace-sidebar) records with **Workspace Sidebar Item** rows.

**How to customize:**
1. Open a workspace and click **Edit**.
2. Add or remove shortcuts, cards and charts, then **Save**.
3. A public workspace is visible to everyone with the related roles. A private workspace is visible only to you.

**Visibility:** Links and shortcuts appear only when the user has permission on the target DocType, report or page. Roles can also be set on the workspace.

**Tip:** Use the search bar (Ctrl + G) to open any screen by name if it is not in the sidebar.""",
	},
	{
		"id": "background-jobs-scheduler",
		"title": "Background Jobs and the Scheduler",
		"tags": "background job scheduler queue worker rq scheduled job type cron job failed job email queue auto run daily hourly job nahi chal raha",
		"doctypes": ["Scheduled Job Type", "Scheduled Job Log", "RQ Job", "Error Log"],
		"body": """Long or periodic tasks run outside the user's request.

**Background jobs (queues):**
- Heavy tasks such as reposting, bulk submit, data import and prepared reports are put in a queue (*short*, *default* or *long*).
- Worker processes pick them up. Check them in the [RQ Job](/app/rq-job) list.

**Scheduler:**
- [Scheduled Job Type](/app/scheduled-job-type) lists periodic jobs with a **Frequency**, for example All, Hourly, Daily, Weekly, Monthly or Cron.
- Each run is logged in [Scheduled Job Log](/app/scheduled-job-log).
- Examples: earned leave allocation, auto repeat documents, email sending, Repost Item Valuation, daily reminders.

**Troubleshooting:**
1. If scheduled tasks do not run, check whether the scheduler is enabled: **Enable Scheduled Jobs** in [System Settings](/app/system-settings), or the server command `bench enable-scheduler`.
2. Look for failures in [Error Log](/app/error-log) and failed rows in Scheduled Job Log.
3. Make sure the worker and scheduler containers are running.""",
	},
	{
		"id": "leave-model",
		"title": "Leave Management Data Model",
		"tags": "leave type leave policy leave policy assignment leave allocation leave ledger entry earned leave accrual carry forward encashment leave balance chutti kaise milti hai leave period hr-pol-01",
		"doctypes": ["Leave Type", "Leave Policy", "Leave Policy Assignment", "Leave Allocation", "Leave Ledger Entry", "Leave Application", "Leave Encashment"],
		"body": """HRMS manages leave through linked records:

1. **[Leave Type](/app/leave-type):** rules per type, for example **Is Earned Leave**, **Earned Leave Frequency** (Monthly, Quarterly, Half-Yearly, Yearly), **Allocate on Day**, **Rounding**, **Carry Forward**, **Maximum Carry Forwarded Leaves**, **Allow Encashment**, **Maximum Leave Allocation Allowed per Leave Period** and **Allow Leave Application After (Calendar Days)**.
2. **[Leave Policy](/app/leave-policy):** a set of leave types with annual allocations. This system has the policy **CGF Leave Policy (HR-POL-01)** (ID `HR-LPOL-2026-00001`).
3. **[Leave Policy Assignment](/app/leave-policy-assignment):** applies a policy to an employee. **Assignment based on** can be **Leave Period** or **Joining Date**, or you can enter the dates directly. On submit it creates Leave Allocations.
4. **[Leave Allocation](/app/leave-allocation):** the leaves granted to one employee for one leave type and period.
5. **[Leave Ledger Entry](/app/leave-ledger-entry):** every change to the balance (allocation, application, expiry, carry forward, encashment) is a row in `tabLeave Ledger Entry`. The balance is the sum of these rows.
6. **[Leave Application](/app/leave-application):** the employee's request. On approval and submit, it posts a negative ledger entry.

**Earned leave:** A scheduled job adds leaves to the allocation each period, based on the frequency.

**Carry forward:** When a new allocation is made with **Add unused leaves from previous allocations**, unused leaves move forward up to the maximum.

**Encashment:** [Leave Encashment](/app/leave-encashment) pays unused leaves and reduces the balance.

**Reports:** [Employee Leave Balance](/app/query-report/Employee Leave Balance), [Leave Ledger](/app/query-report/Leave Ledger).""",
	},
	{
		"id": "bom-work-order",
		"title": "Bill of Materials and Work Order",
		"tags": "bom bill of materials work order manufacturing production raw material finished goods operations routing job card manufacture stock entry banana production kaise kare",
		"doctypes": ["BOM", "Work Order", "Job Card", "Stock Entry", "Production Plan"],
		"body": """**[BOM](/app/bom) (Bill of Materials):** the recipe for a finished item. It lists raw materials with quantities, optional **Operations** with workstations and times, and scrap items. A BOM must be submitted and marked **Is Default** to be used automatically.

**[Work Order](/app/work-order):** an order to produce a quantity of an item from a BOM.

**Flow:**
1. Create a Work Order from the BOM, Sales Order or [Production Plan](/app/production-plan).
2. **Start** creates a [Stock Entry](/app/stock-entry) of type **Material Transfer for Manufacture** from stores to the work-in-progress warehouse.
3. If operations exist, [Job Card](/app/job-card) records track time per operation.
4. **Finish** creates a Stock Entry of type **Manufacture**: raw materials are consumed and the finished item is added to the target warehouse.

**Costing:** The finished item's valuation = raw material cost + operating cost + additional costs, minus scrap value.

**Reports:** [BOM Stock Analysis](/app/query-report/BOM Stock Analysis), [Work Order Summary](/app/query-report/Work Order Summary).""",
	},
	{
		"id": "assets-depreciation-schedule",
		"title": "Assets and Depreciation Schedules",
		"tags": "asset fixed asset depreciation schedule straight line written down value wdv asset category asset movement asset value adjustment scrap sell asset ghisawat",
		"doctypes": ["Asset", "Asset Category", "Asset Depreciation Schedule", "Asset Movement"],
		"body": """**[Asset Category](/app/asset-category):** the **Finance Books** table sets the default **Depreciation Method**, **Total Number of Depreciations** and **Frequency of Depreciation (Months)**. The **Accounts** table sets the Fixed Asset, Accumulated Depreciation and Depreciation Expense accounts per company.

**[Asset](/app/asset):** one record per asset (or per group of identical assets). It is usually created from a Purchase Receipt or Purchase Invoice for an item marked **Is Fixed Asset**.

**[Asset Depreciation Schedule](/app/asset-depreciation-schedule):** In v15 and v16 the schedule is a separate document per asset and finance book. It lists each depreciation date and amount.

**Methods:** Straight Line, Double Declining Balance, Written Down Value, and Manual.

**How depreciation posts:** A scheduled job creates a Journal Entry on each due date: Debit *Depreciation Expense*, Credit *Accumulated Depreciation*.

**Other actions:** [Asset Movement](/app/asset-movement) (location or custodian change), **Asset Value Adjustment**, **Asset Repair**, scrap or sale from the Asset form.

**Reports:** [Asset Depreciation Ledger](/app/query-report/Asset Depreciation Ledger), [Asset Depreciations and Balances](/app/query-report/Asset Depreciations and Balances).""",
	},
	{
		"id": "projects-timesheets-costing",
		"title": "Projects, Tasks and Timesheet Costing",
		"tags": "project task timesheet activity type activity cost billing hours costing project profitability project cost billable hours kitna kharcha hua",
		"doctypes": ["Project", "Task", "Timesheet", "Activity Type", "Activity Cost"],
		"body": """**[Project](/app/project):** groups tasks, time, purchases and sales for a job. It shows totals such as **Total Costing Amount (via Timesheet)**, **Total Billable Amount (via Timesheet)**, **Total Purchase Cost (via Purchase Invoice)** and **Gross Margin**.

**[Task](/app/task):** a piece of work in a project, with dependencies and progress.

**[Timesheet](/app/timesheet):** records hours per employee, activity type, project and task.

**Costing:**
1. [Activity Type](/app/activity-type) sets a **Default Billing Rate** and **Default Costing Rate** per hour.
2. [Activity Cost](/app/activity-cost) overrides these rates per employee.
3. Each timesheet row calculates **Costing Amount** and **Billing Amount** from hours and rates.
4. Billable timesheets can be added to a **Sales Invoice**.

**Other costs:** Purchase Invoices, Expense Claims and Stock Entries with a **Project** field add to project cost.

**Reports:** [Project Summary](/app/query-report/Project Summary), [Daily Timesheet Summary](/app/query-report/Daily Timesheet Summary), and the **Project** accounting dimension in the General Ledger.""",
	},
	{
		"id": "document-links-create-mappings",
		"title": "Document Flow and the Create Button (Mappings)",
		"tags": "create button make mapping get items from linked document document flow purchase order to purchase receipt sales order to delivery note make_ function connections kaise banaye next document",
		"doctypes": ["Purchase Order", "Purchase Receipt", "Purchase Invoice", "Sales Order", "Delivery Note", "Sales Invoice"],
		"body": """ERPNext connects documents in a chain. The **Create** button on a submitted document copies its data into the next document type.

**How it works internally:** each **Create** option calls a Python mapping function, usually named `make_<target>`, for example `make_purchase_receipt` or `make_sales_invoice`. It uses `get_mapped_doc` to copy fields and pending quantities, and it stores back-references in the item rows (for example `purchase_order` and `purchase_order_item` on Purchase Receipt Item).

**Standard flows:**
- Buying: Material Request, then Purchase Order, then Purchase Receipt, then Purchase Invoice, then Payment Entry.
- Selling: Quotation, then Sales Order, then Delivery Note, then Sales Invoice, then Payment Entry.

**Benefits of linking:**
1. Only pending quantities are copied, which prevents over-receipt or over-billing.
2. The source document updates **% Received**, **% Billed** and **Status**.
3. The **Connections** tab shows the full chain.

**Get Items From:** On a new document, the **Get Items From** button pulls items from one or more source documents.

**Tip:** If you create documents without linking, statuses stay "To Receive" or "To Bill" and reports such as [Purchase Order Analysis](/app/query-report/Purchase Order Analysis) show them as pending.""",
	},
	{
		"id": "versions-audit-trail",
		"title": "Versions and Audit Trail",
		"tags": "version audit trail track changes who changed history change log edit history kisne badla activity log deleted document",
		"doctypes": ["Version", "Activity Log", "Deleted Document", "Access Log"],
		"body": """ERPNext keeps a history of changes for audit purposes.

**Version:**
- When a DocType has **Track Changes** ticked (on by default for most transactions), every save creates a [Version](/app/version) record in `tabVersion`.
- It stores the changed fields with old and new values, added or removed child rows, and the user and time.
- The changes appear in the **Activity** timeline at the bottom of the form.

**Turn on tracking:** [Customize Form](/app/customize-form), select the DocType, tick **Track Changes**, then save.

**Other logs:**
- [Activity Log](/app/activity-log): logins, logouts and some actions.
- [Deleted Document](/app/deleted-document): a copy of every deleted record. You can restore it from there.
- [Access Log](/app/access-log): exports and report downloads.
- **Track Views** on a DocType records who opened a document.

**Audit Trail:** The [Audit Trail](/app/audit-trail) screen compares versions of a submitted or amended document.""",
	},
	{
		"id": "files-attachments",
		"title": "Files and Attachments",
		"tags": "file attachment attach upload image pdf private public file manager attachment limit file kahan save hota hai document upload",
		"doctypes": ["File"],
		"body": """Every uploaded file is a [File](/app/file) record (table `tabFile`).

**Key fields:**
- **File Name**, **File URL**, **File Size**
- **Is Private:** private files are served only to logged-in users with access to the linked document. Public files can be opened by anyone with the URL.
- **Attached To DocType**, **Attached To Name**, **Attached To Field:** link the file to a document or an Attach field.
- **Folder:** files are arranged in folders such as *Home* and *Home/Attachments*.

**Where files are stored on disk:** in the site folder, under `public/files` for public files and `private/files` for private files.

**How to attach:**
1. Open the document.
2. Use the **Attachments** section in the sidebar, or an **Attach** field on the form.
3. Upload from your computer, a link, or the camera.

**Limits:** A DocType can set **Max Attachments**. The maximum file size is set in [System Settings](/app/system-settings) > **Max File Size (MB)**.

**Browse all files:** the [File](/app/file) list.""",
	},
]
