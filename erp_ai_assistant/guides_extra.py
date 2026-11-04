"""Extra process guides for the offline Help Guide.

Each entry describes one end-to-end business process in ERPNext v16
(with HRMS and India Compliance). Screen, field and report names were
checked against the live system. The Help Guide matches questions to
these entries by words in the title, tags and body; no AI is used.
"""

GUIDES_EXTRA = [
	{
		"id": "bom",
		"title": "Create a Bill of Materials (BOM) for a manufactured item",
		"tags": "bom bill of materials recipe formula raw material components finished goods manufacture banana kaise banaye kachcha maal secondary items scrap process loss multi level sub assembly",
		"doctypes": ["BOM", "Item"],
		"body": """**When to use:** before you manufacture or subcontract an item, so the system knows which raw materials (components) and how much of each are needed.

1. Make sure the finished item and all raw-material items exist in [Item](/app/item). Each must have **Maintain Stock** ticked.
2. Open [new BOM](/app/bom/new).
3. Set **Item to Manufacture** and **Quantity (Output Qty)** (for example, 1 unit or 100 kg).
4. In the **Components** table, add each raw material with its **Qty** for that output quantity.
5. Set **Rate Of Materials Based On** (Valuation Rate, Price List or Last Purchase Rate) so the BOM shows a cost.
6. Optional: tick **With Operations** to add operations and workstations, or select a **Routing**.
7. Optional: add **Secondary Items** (scrap or by-products) and **% Process Loss** if some material is lost in production.
8. Save and **Submit**. A submitted BOM marked **Is Active** and **Is Default** is picked automatically on Work Orders.

**Notes:**
- A submitted BOM cannot be edited. To change it, use **Copy** (or Cancel and Amend), edit, submit the new one and mark it **Is Default**.
- For a sub-assembly, create its own BOM first. The parent BOM picks it up and **Use Multi-Level BOM** on the Work Order explodes it.

**Check:** [BOM Explorer](/app/query-report/BOM Explorer) shows the full tree, and [BOM Stock Analysis](/app/query-report/BOM Stock Analysis) shows whether you have enough stock to build it.""",
	},
	{
		"id": "work-order-manufacture",
		"title": "Manufacture an item: BOM → Work Order → Material Transfer → Manufacture",
		"tags": "work order production manufacture manufacturing finish goods produce banana production order material transfer for manufacture wip work in progress backflush stock entry manufacture kaise kare utpadan",
		"doctypes": ["Work Order", "BOM", "Stock Entry", "Manufacturing Settings"],
		"body": """**When to use:** to produce finished goods from raw materials using a submitted BOM.

1. One-time setup: open [Manufacturing Settings](/app/manufacturing-settings) and set **Backflush Raw Materials Based On** (BOM or Material Transferred for Manufacture) and any **Overproduction Percentage For Work Order**.
2. Open [new Work Order](/app/work-order/new). Select **Item To Manufacture**; the default **BOM No** fills in.
3. Enter **Qty To Manufacture**, **Work-in-Progress Warehouse**, **Target Warehouse** and the **Default source Warehouse** for raw materials.
4. Optional: tick **Skip Material Transfer to WIP Warehouse** if you consume raw materials directly from the store.
5. Save and **Submit**.
6. Click **Start**. This creates a [Stock Entry](/app/stock-entry) of type **Material Transfer for Manufacture** (store → WIP). Check the quantities and submit it.
7. When production is done, click **Finish** on the Work Order. This creates a Stock Entry of type **Manufacture**, which consumes raw materials and adds the finished item to the **Target Warehouse**. Submit it.
8. The Work Order status becomes **Completed** when the full quantity is manufactured.

**Common problems:**
- "Insufficient stock" on Start: the raw material is not in the source warehouse. Do a stock transfer or purchase first.
- Wrong cost: the finished item's rate is the total raw-material and operating cost divided by the quantity produced.

**Check:** [Work Order Summary](/app/query-report/Work Order Summary) and [Stock Ledger](/app/query-report/Stock Ledger) for the finished item.""",
	},
	{
		"id": "job-card-routing",
		"title": "Track production operations with Routing, Workstation and Job Card",
		"tags": "job card routing workstation operation shop floor machine time log operator production step process capacity planning job card kaise banaye",
		"doctypes": ["Job Card", "Routing", "Workstation", "Operation"],
		"body": """**When to use:** when production has several steps (cutting, welding, painting) and you want to record time and quantity per step.

1. Create each machine or work area in [Workstation](/app/workstation) with its hourly operating cost.
2. Create each step in [Operation](/app/operation) and set its **Default Workstation**.
3. Optional: group the steps in order in [Routing](/app/routing).
4. In the [BOM](/app/bom), tick **With Operations** and select the **Routing** (or add operations manually). Submit the BOM.
5. Submit a [Work Order](/app/work-order) for this BOM. One [Job Card](/app/job-card) is created for each operation.
6. On each Job Card, add **Time Logs** (from time, to time, completed quantity, employee) and submit it when the step is done.
7. After the last Job Card is complete, finish the Work Order to create the **Manufacture** stock entry.

**Check:** [Job Card Summary](/app/query-report/Job Card Summary) and [BOM Operations Time](/app/query-report/BOM Operations Time).""",
	},
	{
		"id": "subcontracting",
		"title": "Subcontracting (job work): Purchase Order → Subcontracting Order → send materials → Subcontracting Receipt",
		"tags": "subcontract subcontracting job work job worker third party processing outsource send raw material to supplier supplied items subcontracting order subcontracting receipt bahar se banwana maal bhejna",
		"doctypes": ["Subcontracting Order", "Purchase Order", "Subcontracting Receipt", "Subcontracting BOM", "Stock Entry"],
		"body": """**When to use:** when a job worker (supplier) makes a finished item for you using raw materials that you supply.

1. Set up items: the finished item must have **Is Subcontracted Item** ticked and a submitted [BOM](/app/bom). Also create a non-stock **service item** for the job-work charge.
2. Optional: create a [Subcontracting BOM](/app/subcontracting-bom) to link the service item to the finished item and BOM.
3. Create a [Purchase Order](/app/purchase-order/new) to the job worker. Tick **Is Subcontracted** and add the service item with the rate per unit. Submit it.
4. From the Purchase Order, click **Create → Subcontracting Order** (or enable **Auto create Subcontracting Order** in [Buying Settings](/app/buying-settings)). Check the **Job Worker Warehouse** and the **Supplied Items** table. Submit it.
5. From the Subcontracting Order, click **Transfer → Material to Supplier**. This makes a [Stock Entry](/app/stock-entry) that moves raw materials to the job worker's warehouse. Submit it.
6. When finished goods come back, click **Create → Subcontracting Receipt**. Enter the received and rejected quantities and submit. Raw materials are consumed based on **Backflush raw materials of subcontract based on** in Buying Settings.
7. Create the [Purchase Invoice](/app/purchase-invoice) for the job-work charge from the Purchase Order or the Subcontracting Receipt.

**Check:** [Subcontract Order Summary](/app/query-report/Subcontract Order Summary) and [Stock Balance](/app/query-report/Stock Balance) filtered on the job worker's warehouse. [GST Job Work Stock Movement](/app/query-report/GST Job Work Stock Movement) helps with ITC-04.""",
	},
	{
		"id": "quality-inspection",
		"title": "Inspect quality on purchase, delivery or manufacture (Quality Inspection)",
		"tags": "quality inspection qc qa check incoming inspection outgoing inspection rejected accepted sample readings parameter template quality check kaise kare jaanch",
		"doctypes": ["Quality Inspection", "Quality Inspection Template", "Item", "Stock Settings"],
		"body": """**When to use:** when goods must pass a quality check before you accept a receipt, deliver to a customer or finish production.

1. Create a [Quality Inspection Template](/app/quality-inspection-template) with the parameters to check (for example, diameter, thickness) and their acceptable values.
2. On the [Item](/app/item), tick **Inspection Required before Purchase** and/or **Inspection Required before Delivery**, and set the **Quality Inspection Template**.
3. In [Stock Settings](/app/stock-settings), set **Action if Quality Inspection is not submitted** and **Action if Quality Inspection is rejected** (Stop or Warn).
4. Create the Purchase Receipt, Delivery Note or Stock Entry as usual and save it (do not submit yet).
5. On the item row, click **Quality Inspection** (or create one from [new Quality Inspection](/app/quality-inspection/new)) with **Inspection Type**, **Reference Type** and **Reference Name**.
6. Fill the **Readings** and the **Sample Size**. Set **Status** to Accepted or Rejected. Submit it.
7. Submit the original document. If the inspection is missing or rejected, the action from step 3 applies.

**Check:** the [Quality Inspection list](/app/quality-inspection) filtered by status, or the **Quality Inspection** column on the receipt's item rows.""",
	},
	{
		"id": "batch-tracking",
		"title": "Track items by batch (lot number, manufacturing and expiry date)",
		"tags": "batch batch number lot lot number expiry expiry date shelf life batch wise stock batch tracking fifo fefo serial and batch bundle batch kaise banaye",
		"doctypes": ["Batch", "Item", "Serial and Batch Bundle", "Stock Settings"],
		"body": """**When to use:** for items bought or produced in lots, such as medicines, food, chemicals or steel heats.

1. On the [Item](/app/item), tick **Has Batch No**. Optional: tick **Automatically Create New Batch** and set the **Batch Number Series** (for example, `PIPE-.#####`).
2. If the item expires, tick **Has Expiry Date** and set **Shelf Life In Days**.
3. Note: batch tracking must be set before the item has any stock transactions.
4. On a Purchase Receipt or Stock Entry, enter the batch on each row. In v16 the batch is stored in a [Serial and Batch Bundle](/app/serial-and-batch-bundle); click **Add Serial / Batch No** on the row to enter it. If auto-creation is on, a batch is made on submit.
5. On a Delivery Note or Sales Invoice with **Update Stock**, pick the batch on the row. [Stock Settings](/app/stock-settings) has **Pick Serial / Batch Based On** (FIFO, LIFO or Expiry) and **Auto create Serial and Batch Bundle for outward**.
6. View or edit batch details in [Batch](/app/batch).

**Check:** [Batch-Wise Balance History](/app/query-report/Batch-Wise Balance History) shows stock per batch and warehouse.""",
	},
	{
		"id": "serial-number-tracking",
		"title": "Track items by serial number (one number per unit)",
		"tags": "serial no serial number imei unique number warranty track each unit serialized item serial and batch bundle serial number kaise daale",
		"doctypes": ["Serial No", "Item", "Serial and Batch Bundle"],
		"body": """**When to use:** for items where each unit must be tracked individually, such as machines, laptops or motors.

1. On the [Item](/app/item), tick **Has Serial No**. Optional: set **Serial Number Series** (for example, `MTR-.#####`) to generate numbers automatically.
2. Set this before the item has any stock transactions.
3. On a Purchase Receipt or Stock Entry, click **Add Serial / Batch No** on the row and enter or generate one serial number per unit. They are saved in a [Serial and Batch Bundle](/app/serial-and-batch-bundle).
4. On a Delivery Note (or Sales Invoice with **Update Stock**), select the serial numbers being sold. The quantity must match the number of serials.
5. Each [Serial No](/app/serial-no) record shows its current warehouse, status and history.

**Common problem:** "Serial No is mandatory" means the row has no bundle. Open the row and add the serial numbers.

**Check:** [Serial No Ledger](/app/query-report/Serial No Ledger) shows every movement of a serial number.""",
	},
	{
		"id": "landed-cost",
		"title": "Add freight, customs and other charges to stock value (Landed Cost Voucher)",
		"tags": "landed cost voucher freight transport customs duty cartage loading clearing charges add to item cost valuation rate import cost bhada bhaada kiraya maal ki keemat",
		"doctypes": ["Landed Cost Voucher", "Purchase Receipt", "Purchase Invoice"],
		"body": """**When to use:** when costs such as freight, customs duty or loading are paid separately and must be added to the value of received stock.

1. Submit the [Purchase Receipt](/app/purchase-receipt) (or a Purchase Invoice with **Update Stock**) first.
2. Open [new Landed Cost Voucher](/app/landed-cost-voucher/new).
3. In **Vouchers**, add the receipt(s). Click **Get Items** to fill **Receipt Items**.
4. In the **Landed Cost** table, add each charge with its **Expense Account** (for example, Freight and Forwarding Charges), **Description** and **Amount**.
5. Set **Distribute Charges Based On** (Qty, Amount or Distribute Manually).
6. Submit. The valuation rate of the items is increased and the stock ledger is reposted.
7. Book the transporter's bill as a separate [Purchase Invoice](/app/purchase-invoice) against the same expense account (or link it in the voucher's vendor invoice table).

**Check:** [Stock Ledger](/app/query-report/Stock Ledger) shows the new valuation rate for the received items.""",
	},
	{
		"id": "reorder-auto-material-request",
		"title": "Set reorder levels and raise Material Requests automatically",
		"tags": "reorder level re-order level minimum stock safety stock auto material request automatic indent low stock alert reorder qty stock kam hone par",
		"doctypes": ["Item", "Item Reorder", "Stock Settings", "Material Request"],
		"body": """**When to use:** to have the system raise a Material Request when stock falls below a minimum level.

1. Open the [Item](/app/item), go to the **Auto re-order** section and add a row in the reorder table:
   - **Request for**: the warehouse to refill.
   - **Check Availability in Warehouse**: optional parent warehouse to check.
   - **Re-order Level**: the minimum quantity.
   - **Re-order Qty**: how much to request.
   - **Material Request Type**: Purchase, Transfer, Manufacture and so on.
2. In [Stock Settings](/app/stock-settings), tick **Raise Material Request when stock reaches re-order level**. Optional: tick **Notify by email on creation of automatic Material Request**.
3. A scheduled job checks the projected quantity daily and creates draft [Material Requests](/app/material-request) for items below the level.
4. Review the Material Requests and convert them to Purchase Orders or Stock Entries.

**Check:** [Stock Projected Qty](/app/query-report/Stock Projected Qty) shows the reorder level beside the projected quantity, and [Itemwise Recommended Reorder Level](/app/query-report/Itemwise Recommended Reorder Level) suggests levels.""",
	},
	{
		"id": "rfq-supplier-quotation",
		"title": "Compare suppliers: Request for Quotation → Supplier Quotation → Purchase Order",
		"tags": "rfq request for quotation supplier quotation compare rates vendor comparison quotation from supplier best price tender bid rate mangwana compare karna",
		"doctypes": ["Request for Quotation", "Supplier Quotation", "Purchase Order"],
		"body": """**When to use:** when you want prices from several suppliers before placing an order.

1. Open [new Request for Quotation](/app/request-for-quotation/new) (or create it from a Material Request with **Create → Request for Quotation**).
2. Add the **Suppliers** (each needs an email contact) and the **Items** with quantity and **Required Date**.
3. Optional: choose an **Email Template**, then save and **Submit**. Emails are sent to suppliers with a portal link.
4. When a supplier replies, open the RFQ and click **Create → Supplier Quotation**, or open [new Supplier Quotation](/app/supplier-quotation/new). Enter the supplier's rates and **Valid Till**, then submit.
5. Repeat for each supplier.
6. Compare the quotations in [Supplier Quotation Comparison](/app/query-report/Supplier Quotation Comparison).
7. Open the chosen Supplier Quotation and click **Create → Purchase Order**.

**Check:** the RFQ shows the quote status for each supplier, and the comparison report shows the lowest rate per item.""",
	},
	{
		"id": "crm-lead-opportunity-quotation",
		"title": "Sales pipeline (CRM): Lead → Opportunity → Quotation → Sales Order",
		"tags": "crm lead opportunity enquiry inquiry prospect quotation sales pipeline follow up potential customer sales stage lost reason lead convert customer naya grahak inquiry kaise darj kare",
		"doctypes": ["Lead", "Opportunity", "Quotation", "Customer"],
		"body": """**When to use:** to track a potential customer from first contact to order.

1. Create a [Lead](/app/lead/new) with name, **Organization Name**, **Email**, **Mobile No**, **Source** and **Lead Owner**.
2. When there is real interest, open the Lead and click **Create → Opportunity**. Set **Opportunity Type**, **Sales Stage**, **Probability (%)**, **Expected Closing Date** and add **Items**.
3. From the Opportunity, click **Create → Quotation**. Check the items, rates and taxes, set **Valid Till** and submit it. Use **Print** or **Email** to send it.
4. When the customer accepts, open the Quotation and click **Create → Sales Order**. The Lead is converted to a [Customer](/app/customer) if it is not one already.
5. If the deal is lost, use **Set as Lost** on the Opportunity or Quotation and select **Lost Reasons**.

**Check:** [Sales Pipeline Analytics](/app/query-report/Sales Pipeline Analytics), [Opportunity Summary by Sales Stage](/app/query-report/Opportunity Summary by Sales Stage), [Lost Opportunity](/app/query-report/Lost Opportunity) and [Lead Details](/app/query-report/Lead Details).""",
	},
	{
		"id": "pos",
		"title": "Retail counter billing: POS Profile → Opening Entry → Point of Sale → Closing Entry",
		"tags": "pos point of sale retail counter billing cash counter shop billing pos invoice pos profile opening closing shift cashier cash drawer counter sale dukan billing",
		"doctypes": ["POS Profile", "POS Opening Entry", "POS Invoice", "POS Closing Entry", "POS Settings"],
		"body": """**When to use:** for fast counter sales with immediate payment.

1. Create a [POS Profile](/app/pos-profile/new): set **Company**, **Warehouse**, default **Customer** (for walk-in sales), **Price List**, **Payment Methods** (Cash, UPI, Card with accounts), **Write Off Account**, **Write Off Cost Center** and **Applicable for Users**.
2. Optional: in the profile, tick **Allow User to Edit Rate** or **Allow User to Edit Discount** if cashiers may change prices.
3. In [POS Settings](/app/pos-settings), choose **Invoice Type Created via POS Screen** (Sales Invoice or POS Invoice).
4. Open [Point of Sale](/app/point-of-sale). At the start of a shift, a [POS Opening Entry](/app/pos-opening-entry) asks for the opening cash.
5. Scan or search items, choose the customer, click **Checkout**, select the payment mode and **Complete Order**. Print the receipt.
6. At the end of the shift, open the POS menu and click **Close the POS**. This creates a [POS Closing Entry](/app/pos-closing-entry). Enter the actual closing amount per payment mode and submit.
7. If POS Invoices are used, submitting the closing entry consolidates them into Sales Invoices.

**Check:** the POS Closing Entry totals, and [Sales Register](/app/query-report/Sales Register) for the day.""",
	},
	{
		"id": "pricing-rule",
		"title": "Give automatic discounts with Pricing Rule and Promotional Scheme",
		"tags": "pricing rule discount scheme offer promotional scheme buy one get one free item quantity discount slab special rate for customer festival offer chhoot discount kaise lagaye",
		"doctypes": ["Pricing Rule", "Promotional Scheme"],
		"body": """**When to use:** to apply a discount, special rate or free item automatically when conditions match.

**Single rule (Pricing Rule):**
1. Open [new Pricing Rule](/app/pricing-rule/new).
2. Set **Apply On** (Item Code, Item Group, Brand or Transaction) and add the items or groups.
3. Tick **Selling** and/or **Buying**. Set **Applicable For** (for example, Customer or Customer Group) and choose the value.
4. Set **Min Qty (As Per Stock UOM)** and **Max Qty (As Per Stock UOM)** if the rule depends on quantity.
5. Choose **Price or Product Discount**:
   - Price: set **Rate or Discount** to Rate, Discount Percentage or Discount Amount.
   - Product: set the **Free Item** and **Qty**.
6. Set **Valid From**, **Valid Up To** and the **Company**. Use **Priority** when several rules can match. Save.

**Slabs (Promotional Scheme):** use [Promotional Scheme](/app/promotional-scheme/new) to define several quantity or amount slabs in one place. Add rows in **Price Discount Slabs** or **Product Discount Slabs**. Saving the scheme creates the Pricing Rules for you.

**Check:** create a draft Sales Order for a matching customer and item. The row shows the applied **Pricing Rules** and the discounted rate.""",
	},
	{
		"id": "credit-limit",
		"title": "Set a customer credit limit and control overdue billing",
		"tags": "credit limit customer credit outstanding limit exceeded overdue limit block sales order bypass credit limit udhaar limit credit limit cross error",
		"doctypes": ["Customer", "Accounts Settings"],
		"body": """**When to use:** to stop sales when a customer's outstanding amount crosses an agreed limit.

1. Open the [Customer](/app/customer) and find the **Credit & Overdue Limits** table.
2. Add a row with the **Company** and the **Credit Limit** amount.
3. Optional: tick **Bypass credit limit check at sales order** to check the limit only at invoicing instead of at the Sales Order.
4. In [Accounts Settings](/app/accounts-settings), on the **Credit Limits** tab, set **Role allowed to bypass credit limit** for managers who may approve exceptions.
5. When a Sales Order or Sales Invoice would take the outstanding amount above the limit, the system blocks it. Users with the bypass role see a warning instead.

**Fix for "Credit limit has been crossed":** collect payment, raise the limit on the Customer, or ask a user with the bypass role to submit.

**Check:** [Accounts Receivable](/app/query-report/Accounts Receivable) and [Customer Credit Balance](/app/query-report/Customer Credit Balance).""",
	},
	{
		"id": "multi-currency",
		"title": "Invoice and pay in a foreign currency (multi-currency, exchange gain or loss)",
		"tags": "multi currency foreign currency usd dollar euro export import invoice exchange rate exchange gain loss revaluation forex videshi mudra currency change",
		"doctypes": ["Sales Invoice", "Purchase Invoice", "Currency Exchange", "Exchange Rate Revaluation", "Account"],
		"body": """**When to use:** when you bill a customer or are billed by a supplier in a currency other than INR.

1. Create a receivable (or payable) [Account](/app/account) in the foreign currency, for example "Debtors USD", with **Currency** set to USD.
2. On the [Customer](/app/customer) (or Supplier), set **Billing Currency** and add this account in the **Default Accounts** table for your company.
3. Optional: add rates in [Currency Exchange](/app/currency-exchange), or let the system fetch them.
4. Create the [Sales Invoice](/app/sales-invoice/new). **Currency** comes from the customer. Check the **Exchange Rate** and submit. The ledger is posted in INR and the foreign currency.
5. Receive payment with a [Payment Entry](/app/payment-entry/new). Enter the rate on the payment date. The difference is booked to the **Exchange Gain / Loss Account** set on the [Company](/app/company).
6. At month or year end, run [Exchange Rate Revaluation](/app/exchange-rate-revaluation/new) to revalue open foreign-currency balances.

**Note:** an account's currency cannot be changed after it has entries, and a party can have only one billing currency per company.

**Check:** [General Ledger](/app/query-report/General Ledger) with the **Currency** filter set to the foreign currency, and [Accounts Receivable](/app/query-report/Accounts Receivable).""",
	},
	{
		"id": "bank-reconciliation",
		"title": "Reconcile the bank account with the bank statement",
		"tags": "bank reconciliation brs bank statement match clearance date cheque cleared bank transaction statement import reconcile bank balance mismatch bank milan",
		"doctypes": ["Bank Reconciliation Tool", "Bank Transaction", "Bank Statement Import", "Bank Account"],
		"body": """**When to use:** to match ERPNext payments with the entries on your bank statement.

1. Create a [Bank Account](/app/bank-account) with **Is Company Account** ticked and link it to the ledger in **Company Account**.
2. Import the statement with [Bank Statement Import](/app/bank-statement-import/new): select **Company**, **Bank Account**, upload the file and map the columns. This creates [Bank Transactions](/app/bank-transaction).
3. Open [Bank Reconciliation Tool](/app/bank-reconciliation-tool). Select the **Company**, **Bank Account**, **From Date** and **To Date**, and enter the **Closing Balance** from the statement.
4. For each unmatched bank transaction, click **Actions**:
   - **Match Against Voucher** to link an existing Payment Entry or Journal Entry.
   - **Create Voucher** to make a new Payment Entry or Journal Entry (for example, bank charges).
5. When everything is matched, the difference shown by the tool should be zero.

**Without a statement file:** use [Bank Clearance](/app/bank-clearance) to enter the **Clearance Date** for each payment.

**Check:** [Bank Reconciliation Statement](/app/query-report/Bank Reconciliation Statement) lists entries not yet cleared by the bank.""",
	},
	{
		"id": "period-closing",
		"title": "Close the financial year (Period Closing Voucher)",
		"tags": "year end closing period closing voucher fiscal year close books profit transfer retained earnings closing entry financial year end march closing saal khatam",
		"doctypes": ["Period Closing Voucher", "Fiscal Year", "Accounts Settings"],
		"body": """**When to use:** at the end of a financial year, to move the year's profit or loss into a balance-sheet account.

1. Make sure all invoices, payments, depreciation and adjustments for the year are posted.
2. Create the next [Fiscal Year](/app/fiscal-year/new) (for example, 2027-2028) if it does not exist.
3. Create a liability or equity account for retained earnings (for example, "Reserves and Surplus") if needed.
4. Open [new Period Closing Voucher](/app/period-closing-voucher/new). Set **Company**, **Fiscal Year**, **Period Start Date**, **Period End Date**, **Transaction Date** and **Closing Account Head** (the retained earnings account).
5. Submit. Income and expense accounts are closed and the net profit or loss is posted to the closing account.
6. Optional: to stop back-dated changes, set **Accounts Frozen Till Date** on the [Company](/app/company).

**Note:** you can still post entries in the closed year. The closing entries are recalculated if needed, but avoid doing this after audit.

**Check:** [Balance Sheet](/app/query-report/Balance Sheet) and [Trial Balance](/app/query-report/Trial Balance) for the closed year.""",
	},
	{
		"id": "budget",
		"title": "Set a budget by Cost Center or Project and control spending",
		"tags": "budget budget control expense limit cost center project budget variance stop warn exceed budget monthly quarterly distribution kharcha seema",
		"doctypes": ["Budget", "Cost Center", "Project"],
		"body": """**When to use:** to limit spending on an expense account for a cost center or project.

1. Open [new Budget](/app/budget/new).
2. Set **Budget Against** (Cost Center or Project) and choose the **Cost Center** or **Project**.
3. Select the **Company**, the expense **Account**, **From Fiscal Year** and **To Fiscal Year**.
4. Enter the **Budget Amount** and choose the **Distribution Frequency** (Monthly, Quarterly, Half-Yearly or Yearly). Tick **Distribute Equally** or edit the **Budget Distribution** table.
5. Under **Control Action**, choose where to check the budget and what to do (Stop, Warn or Ignore):
   - **Applicable on Material Request**
   - **Applicable on Purchase Order**
   - **Applicable on booking actual expenses**
6. Submit the budget.

**Check:** [Budget Variance Report](/app/query-report/Budget Variance Report) compares budget and actual amounts.""",
	},
	{
		"id": "accounting-dimension",
		"title": "Add an accounting dimension (for example, Branch or Department) to all transactions",
		"tags": "accounting dimension branch wise department wise segment profit by branch dimension filter cost center alternative analytics branch ka profit",
		"doctypes": ["Accounting Dimension", "Cost Center"],
		"body": """**When to use:** to report profit and expenses by a category other than Cost Center, such as Branch, Department or Region.

1. Open [new Accounting Dimension](/app/accounting-dimension/new).
2. Set **Reference Document Type** (for example, Branch). The **Dimension Name** fills in.
3. Optional: in the company table, set a default value and tick mandatory for Balance Sheet or Profit and Loss accounts.
4. Save. A new field is added to invoices, payments, journal entries and stock documents.
5. Fill the field on transactions. It can also be set by default per company.

**Check:** [General Ledger](/app/query-report/General Ledger), [Profit and Loss Statement](/app/query-report/Profit and Loss Statement) and [Trial Balance](/app/query-report/Trial Balance) can be filtered by the new dimension.""",
	},
	{
		"id": "opening-invoices",
		"title": "Enter opening outstanding invoices for customers and suppliers (Opening Invoice Creation Tool)",
		"tags": "opening balance opening invoice outstanding old dues previous balance migration party opening debtors creditors opening temporary opening purana baaki",
		"doctypes": ["Opening Invoice Creation Tool", "Journal Entry"],
		"body": """**When to use:** when you start using ERPNext and customers or suppliers already owe money from before.

1. Open [Opening Invoice Creation Tool](/app/opening-invoice-creation-tool).
2. Select the **Company** and **Invoice Type** (Sales for customers, Purchase for suppliers).
3. Optional: tick **Create Missing Party** to create customers or suppliers that do not exist.
4. In **Invoices**, add one row per old bill: **Party ID**, **Posting Date**, **Due Date**, **Outstanding Amount** and optionally **Invoice Number**. The **Temporary Opening Account** is used as the balancing account.
5. Click **Create Invoices**. Opening Sales or Purchase Invoices are created and submitted.
6. Enter the opening balances of other ledgers (bank, cash, capital, fixed assets) with a [Journal Entry](/app/journal-entry/new) marked **Is Opening** = Yes, using the same Temporary Opening account.
7. At the end, the Temporary Opening account balance should be zero.

**Check:** [Accounts Receivable](/app/query-report/Accounts Receivable), [Accounts Payable](/app/query-report/Accounts Payable) and [Trial Balance](/app/query-report/Trial Balance).""",
	},
	{
		"id": "tds",
		"title": "Deduct TDS on supplier bills (Tax Withholding Category)",
		"tags": "tds tax deducted at source tax withholding 194c 194j 194q section threshold deduct tds supplier lower deduction certificate tds kaise kate",
		"doctypes": ["Tax Withholding Category", "Supplier", "Purchase Invoice", "Lower Deduction Certificate"],
		"body": """**When to use:** when you must deduct TDS from payments to suppliers (for example, contractors or professionals).

1. Open [Tax Withholding Category](/app/tax-withholding-category) and create or check a category per section (for example, "194C - Contractor").
2. In **Rates**, add a row with **From Date**, **To Date**, **Tax Withholding Rate**, **Cumulative Threshold** and **Transaction Threshold**.
3. In **Accounts**, set the TDS payable account for your company.
4. On the [Supplier](/app/supplier), set **Tax Withholding Category**.
5. Create the [Purchase Invoice](/app/purchase-invoice/new). Keep **Consider for Tax Withholding** ticked. TDS is calculated when the threshold is crossed and shown in the tax withholding entries.
6. If the supplier has a certificate for a lower rate, create a [Lower Deduction Certificate](/app/lower-deduction-certificate/new).
7. Pay the deducted TDS to the government with a Payment Entry or Journal Entry from the TDS payable account.

**Check:** [Tax Withholding Details](/app/query-report/Tax Withholding Details) and [TDS Computation Summary](/app/query-report/TDS Computation Summary).""",
	},
	{
		"id": "e-waybill",
		"title": "Generate an e-Waybill for a Sales Invoice or Delivery Note",
		"tags": "e-waybill eway bill e way bill ewb transport vehicle number distance transporter id part b generate e waybill update vehicle cancel e waybill eway bill kaise banaye",
		"doctypes": ["Sales Invoice", "Delivery Note", "GST Settings", "e-Waybill Log"],
		"body": """**When to use:** when goods worth more than the threshold (usually ₹50,000) are moved and an e-Waybill is required.

1. One-time setup: in [GST Settings](/app/gst-settings), tick **Enable API Features** and **Enable e-Waybill Features**. Optional: **Automatically Generate e-Waybill on Invoice Submission**, **Enable e-Waybill Generation from Delivery Note**, and the **Default Threshold Value for e-Waybill Generation**.
2. Make sure the company address, customer address (with PIN code) and item HSN codes are correct.
3. On the [Sales Invoice](/app/sales-invoice), fill **Transporter Info**: **Transporter** or **GST Transporter ID**, **Mode of Transport**, **Vehicle No**, **Distance (in km)** (0 lets the portal calculate it) and **GST Vehicle Type**.
4. Submit the invoice. If auto-generation is off, click **e-Waybill → Generate**.
5. The **e-Waybill No.** and status are saved on the invoice. Use **e-Waybill → Print** to print it.
6. To change the vehicle, use **e-Waybill → Update Vehicle Info**. To cancel (within 24 hours), use **e-Waybill → Cancel**.

**Check:** [e-Waybill Log](/app/e-waybill-log) lists every e-Waybill with its status.""",
	},
	{
		"id": "e-invoice",
		"title": "Generate an e-Invoice (IRN and QR code) for a Sales Invoice",
		"tags": "e-invoice einvoice irn qr code invoice registration number irp generate e invoice cancel e invoice b2b invoice e invoice kaise banaye",
		"doctypes": ["Sales Invoice", "GST Settings", "e-Invoice Log"],
		"body": """**When to use:** for B2B, export and SEZ invoices when your company's turnover requires e-invoicing.

1. One-time setup: in [GST Settings](/app/gst-settings), tick **Enable API Features** and **Enable e-Invoicing**. Set **e-Invoice Applicable From**. Optional: **Automatically Generate e-Invoice on Invoice Submission** and **Generate e-Waybill with e-Invoice**.
2. Make sure the customer has a valid GSTIN and address, and every item has an HSN code.
3. Create and submit the [Sales Invoice](/app/sales-invoice/new).
4. If auto-generation is off, click **e-Invoice → Generate**.
5. The **IRN** and **e-Invoice Status** are saved, and the signed QR code appears on the e-Invoice print format.
6. To cancel within 24 hours, use **e-Invoice → Cancel** before cancelling the Sales Invoice. After 24 hours, issue a Credit Note instead.

**Check:** [e-Invoice Summary](/app/query-report/e-Invoice Summary) and [e-Invoice Log](/app/e-invoice-log).""",
	},
	{
		"id": "gst-returns",
		"title": "Prepare GSTR-1 and GSTR-3B returns",
		"tags": "gstr1 gstr-1 gstr3b gstr-3b gst return filing monthly return outward supplies itc input tax credit hsn summary purchase reconciliation 2b gst return kaise bhare",
		"doctypes": ["GSTR-1", "GSTR 3B Report", "Purchase Reconciliation Tool"],
		"body": """**When to use:** every month or quarter, to prepare GST return data for each GSTIN.

**GSTR-1 (outward supplies):**
1. Open [GSTR-1](/app/gstr-1).
2. Select **Company**, **Company GSTIN**, **Year** and **Month/Quarter**.
3. Review the data in the tabs (B2B, B2C, exports, credit notes, HSN summary and document issued). Fix any invoice errors in the source documents.
4. Download the JSON and upload it to the GST portal, or file through the API if enabled.

**GSTR-3B (summary return):**
1. Reconcile purchases first in [Purchase Reconciliation Tool](/app/purchase-reconciliation-tool) by downloading GSTR-2B and matching it with your Purchase Invoices.
2. Open [new GSTR 3B Report](/app/gstr-3b-report/new). Select **Company**, **Company GSTIN**, **Year** and **Month or Quarter**, then save.
3. Review the tax liability and ITC figures, then download the JSON for the portal.

**Check:** [GST Sales Register](/app/query-report/GST Sales Register), [GST Purchase Register](/app/query-report/GST Purchase Register), [HSN-wise-summary of outward supplies](/app/query-report/HSN-wise-summary of outward supplies) and [GSTR-3B Details](/app/query-report/GSTR-3B Details).""",
	},
	{
		"id": "asset-lifecycle",
		"title": "Fixed assets: purchase → depreciation → sale or scrap",
		"tags": "asset fixed asset depreciation machine vehicle computer furniture capitalise asset category sell asset scrap asset dispose write off wdv slm straight line written down value sampatti",
		"doctypes": ["Asset", "Asset Category", "Asset Depreciation Schedule", "Purchase Invoice", "Accounts Settings"],
		"body": """**When to use:** to record machines, vehicles or other fixed assets, depreciate them and later sell or scrap them.

1. Create an [Asset Category](/app/asset-category/new). In **Accounts**, set the Fixed Asset, Accumulated Depreciation and Depreciation Expense accounts. In **Finance Books**, set **Depreciation Method**, **Total Number of Depreciations** and **Frequency of Depreciation (Months)**.
2. Create the [Item](/app/item) with **Is Fixed Asset** ticked and the **Asset Category** set. It must not maintain stock.
3. Buy the asset with a [Purchase Receipt](/app/purchase-receipt) or [Purchase Invoice](/app/purchase-invoice). If **Auto create assets on purchase** is ticked on the item, a draft [Asset](/app/asset) is created; otherwise create it and link the receipt or invoice.
4. On the Asset, check **Location**, **Purchase Date**, **Available for Use Date** and tick **Calculate Depreciation**. Submit it. An [Asset Depreciation Schedule](/app/asset-depreciation-schedule) is created.
5. Depreciation entries are posted automatically on schedule when **Book Asset Depreciation entry automatically** is ticked in [Accounts Settings](/app/accounts-settings).
6. To sell: open the Asset and use **Manage → Sell Asset**. This creates a Sales Invoice; gain or loss goes to the **Gain/Loss Account on Asset Disposal** on the Company.
7. To scrap: use **Manage → Scrap Asset**. A journal entry writes off the remaining value.

**Check:** [Fixed Asset Register](/app/query-report/Fixed Asset Register), [Asset Depreciation Ledger](/app/query-report/Asset Depreciation Ledger) and [Asset Depreciations and Balances](/app/query-report/Asset Depreciations and Balances).""",
	},
	{
		"id": "projects-timesheets",
		"title": "Projects: Project → Tasks → Timesheets → billing",
		"tags": "project task timesheet time tracking hours billable billing project costing project profitability activity type milestone gantt project kaise banaye",
		"doctypes": ["Project", "Task", "Timesheet", "Activity Type", "Sales Invoice"],
		"body": """**When to use:** to plan work, record time spent and bill customers for hours or track project cost.

1. Create a [Project](/app/project/new) with **Project Name**, **Expected Start Date**, **Expected End Date**, **Customer** and **Estimated Cost**. Optional: link a **Sales Order** and set **Default Cost Center**.
2. Add [Tasks](/app/task/new) with subject, project, dates and assigned users. Tasks can have parent tasks and dependencies.
3. Create [Activity Types](/app/activity-type) (for example, Installation, Consulting) with default billing and costing rates.
4. Employees record time in a [Timesheet](/app/timesheet/new): for each row, set **Activity Type**, **From Time**, **Hrs**, **Project**, **Task** and tick **Is Billable**. Submit the timesheet.
5. To bill the customer, open the timesheet and click **Create Sales Invoice**, or fetch timesheets on a Sales Invoice.
6. Purchase Invoices and Stock Entries linked to the project add to its cost.

**Check:** [Project Summary](/app/query-report/Project Summary), [Timesheet Billing Summary](/app/query-report/Timesheet Billing Summary), [Daily Timesheet Summary](/app/query-report/Daily Timesheet Summary) and [Project Profitability](/app/query-report/Project Profitability).""",
	},
	{
		"id": "expense-claim",
		"title": "Employee expense claim: submit → approve → reimburse",
		"tags": "expense claim reimbursement travel expense conveyance food bill employee claim approve expense approver kharcha wapas reimburse",
		"doctypes": ["Expense Claim", "Expense Claim Type", "Employee", "Payment Entry"],
		"body": """**When to use:** when an employee spends their own money for company work and must be repaid.

1. One-time setup: create [Expense Claim Types](/app/expense-claim-type) (for example, Travel, Food) with the expense account for your company. Set **Expense Approver** on each [Employee](/app/employee) and the **Default Expense Claim Payable Account** on the [Company](/app/company).
2. The employee opens [new Expense Claim](/app/expense-claim/new), selects **From Employee** and the **Expense Approver**.
3. In **Expenses**, add rows with **Expense Date**, **Expense Claim Type**, description and **Amount**. Attach bills. Save.
4. The approver reviews the claim, sets **Sanctioned Amount** per row and sets **Approval Status** to Approved, then submits.
5. If the employee had taken an advance, fetch it in the **Advances** table to adjust it.
6. Pay the employee with **Create → Payment** on the claim, which makes a [Payment Entry](/app/payment-entry).

**Check:** [Unpaid Expense Claim](/app/query-report/Unpaid Expense Claim) and the claim's status (Unpaid or Paid).""",
	},
	{
		"id": "employee-advance",
		"title": "Give an employee advance and settle it against expenses or salary",
		"tags": "employee advance salary advance travel advance imprest advance return advance adjustment repay from salary advance dena",
		"doctypes": ["Employee Advance", "Expense Claim", "Payment Entry", "Salary Slip"],
		"body": """**When to use:** when an employee is paid money in advance for travel or other expenses.

1. Set the **Default Employee Advance Account** on the [Company](/app/company).
2. Open [new Employee Advance](/app/employee-advance/new). Select the **Employee**, enter the **Purpose**, **Advance Amount** and **Advance Account**. Optional: tick **Repay Unclaimed Amount from Salary**.
3. Submit it, then click **Create → Payment** to pay the employee.
4. Later, when the employee files an [Expense Claim](/app/expense-claim), fetch the advance in the **Advances** table. The claim amount is adjusted against the advance.
5. If money is left over, use **Return** on the Employee Advance to record the refund, or let it be deducted from salary if that option was ticked.

**Check:** [Employee Advance Summary](/app/query-report/Employee Advance Summary).""",
	},
	{
		"id": "attendance-checkin",
		"title": "Record attendance: manual attendance, biometric check-in and shifts",
		"tags": "attendance check in check out checkin biometric punch shift late entry early exit half day absent present mark attendance auto attendance hajri haziri",
		"doctypes": ["Attendance", "Employee Checkin", "Shift Type", "Employee Attendance Tool"],
		"body": """**When to use:** to record whether employees were present, absent or on half day, for leave and payroll.

**Manual attendance:**
1. Mark one employee in [new Attendance](/app/attendance/new) with **Status** and date, then submit.
2. Mark many employees at once in [Employee Attendance Tool](/app/employee-attendance-tool).

**Automatic attendance from check-ins:**
1. Create a [Shift Type](/app/shift-type/new) with **Start Time**, **End Time**, **Holiday List**, **Late Entry Grace Period**, **Working Hours Threshold for Half Day** and **Working Hours Threshold for Absent**. Tick **Enable Auto Attendance** and set **Process Attendance After**.
2. Assign the shift to employees (**Default Shift** on [Employee](/app/employee) or a Shift Assignment).
3. Set **Attendance Device ID (Biometric/RF tag ID)** on each employee.
4. Punches arrive as [Employee Checkin](/app/employee-checkin) records (from the device integration or the mobile app), with **Log Type** IN or OUT.
5. The scheduler creates Attendance from check-ins up to **Last Sync of Checkin**.

**Check:** [Monthly Attendance Sheet](/app/query-report/Monthly Attendance Sheet) and [Shift Attendance](/app/query-report/Shift Attendance).""",
	},
	{
		"id": "payroll",
		"title": "Run payroll: Salary Component → Salary Structure → Assignment → Payroll Entry → Salary Slip",
		"tags": "payroll salary salary slip salary structure salary component basic hra pf esi professional tax payroll entry process salary pay salary monthly salary tankhwah vetan salary kaise banaye",
		"doctypes": ["Payroll Entry", "Salary Component", "Salary Structure", "Salary Structure Assignment", "Salary Slip", "Payroll Settings"],
		"body": """**When to use:** to calculate and pay monthly salaries.

1. Check [Payroll Settings](/app/payroll-settings), especially **Calculate Payroll Working Days Based On** (Leave or Attendance).
2. Create [Salary Components](/app/salary-component) such as Basic, HRA, PF and Professional Tax. Set **Type** (Earning or Deduction), **Abbr**, the account in **Accounts**, and a **Formula** if needed (for example, `base * .5` for Basic).
3. Create a [Salary Structure](/app/salary-structure/new) with **Payroll Frequency** (usually Monthly) and the **Earnings** and **Deductions** rows. Submit it.
4. Assign it to each employee with a [Salary Structure Assignment](/app/salary-structure-assignment/new): **Employee**, **Salary Structure**, **From Date**, **Base** (monthly gross or CTC base) and optionally **Income Tax Slab**. Submit it.
5. Each month, open [new Payroll Entry](/app/payroll-entry/new). Set **Posting Date**, **Company**, **Payroll Frequency**, **Start Date**, **End Date**, **Payroll Payable Account**, **Cost Center** and **Payment Account**.
6. Click **Get Employees**, then **Create Salary Slips**. Review the draft [Salary Slips](/app/salary-slip).
7. Click **Submit Salary Slip** to post the accrual entry, then **Make Bank Entry** to record the payment.

**Common problem:** "No salary structure assigned" means step 4 is missing or its **From Date** is after the payroll period.

**Check:** [Salary Register](/app/query-report/Salary Register) and [Bank Remittance](/app/query-report/Bank Remittance).""",
	},
	{
		"id": "user-roles-permissions",
		"title": "Create a user, assign roles and restrict access with User Permissions",
		"tags": "user create user login new user role role profile permission access rights restrict user permission branch wise access only see own warehouse permission manager password reset user kaise banaye",
		"doctypes": ["User", "Role Profile", "User Permission", "Role"],
		"body": """**When to use:** to give a person a login and control what they can see and do.

1. Open [new User](/app/user/new). Enter **Email** and **First Name**. Keep **Send Welcome Email** ticked so they can set a password, or set it later under **Set New Password**.
2. In **Roles**, tick the roles needed (for example, Sales User, Stock User, Accounts User). To reuse a set of roles, create a [Role Profile](/app/role-profile/new) and select it in **Role Profile**.
3. Optional: use **Module Profile** or **Block Modules** to hide modules.
4. Save.
5. To limit records, create a [User Permission](/app/user-permission/new): set **User**, **Allow** (for example, Company, Warehouse or Branch) and **For Value**. Untick **Apply To All Document Types** to limit it to selected document types.
6. To change what a role can do, use [Role Permissions Manager](/app/permission-manager).
7. For employees, link the user in **User ID** on the [Employee](/app/employee).

**Check:** log in as the user (or use **Settings → Permitted Documents for User**) to confirm what they can see.""",
	},
	{
		"id": "data-import",
		"title": "Bulk upload data from Excel or CSV (Data Import)",
		"tags": "data import bulk upload excel csv import items import customers import stock upload template update existing records mass upload migration excel se data daalna",
		"doctypes": ["Data Import"],
		"body": """**When to use:** to create or update many records at once, such as items, customers, suppliers or opening stock.

1. Open [new Data Import](/app/data-import/new).
2. Select the **Document Type** (for example, Item) and **Import Type** (**Insert New Records** or **Update Existing Records**). Save.
3. Click **Download Template**. Choose the fields you need and download as Excel or CSV. For updates, export the existing records with their ID column.
4. Fill the template. Keep the header row unchanged. Use exact names for linked values (for example, Item Group, UOM, Warehouse).
5. Upload it in **Import File** (or use **Import from Google Sheets**). Optional: tick **Submit After Import** for submittable documents and **Don't Send Emails**.
6. Review the preview and warnings, then click **Start Import**.
7. If some rows fail, read the **Import Log**, fix those rows, and click **Export Errored Rows** to re-import only them.

**Check:** open the list of that document type and confirm the count and values.""",
	},
	{
		"id": "print-format-letterhead",
		"title": "Customize print formats and add a company Letter Head",
		"tags": "print format letter head letterhead logo invoice format print design pdf layout header footer company logo on invoice custom print print setting print format kaise badle",
		"doctypes": ["Print Format", "Letter Head", "Print Settings"],
		"body": """**When to use:** to change how invoices and other documents look when printed or emailed as PDF.

**Letter Head:**
1. Open [new Letter Head](/app/letter-head/new). Enter **Letter Head Name**.
2. Set **Letter Head Based On** to Image (upload the logo or header image) or HTML. Set **Footer Based On** for a footer.
3. Tick **Default Letter Head** to use it on all prints. Save.

**Print Format:**
1. Open a document (for example, a Sales Invoice) and click **Print**.
2. Use the format selector to try existing formats, including the GST formats from India Compliance.
3. To make your own, click **Edit Format** or open [Print Format Builder](/app/print-format-builder). Start from a standard format, drag fields, add or remove columns and save with a new name.
4. For full control, create a [Print Format](/app/print-format/new) with **Custom Format** ticked and write HTML (Jinja).
5. To make it the default, go to **Customize Form** for that document type and set **Default Print Format**.

**Check:** print a sample document with the new format and letter head. Page size and margins are in [Print Settings](/app/print-settings).""",
	},
	{
		"id": "email-account",
		"title": "Set up an email account to send and receive emails",
		"tags": "email account smtp imap gmail outlook send email from erp email not sending outgoing incoming email setup app password email setting email nahi ja raha",
		"doctypes": ["Email Account"],
		"body": """**When to use:** so ERPNext can email invoices, purchase orders, salary slips and notifications.

1. Open [new Email Account](/app/email-account/new).
2. Enter **Email Address** and **Email Account Name**. Choose **Service** (for example, GMail or Outlook.com) to fill server settings automatically.
3. Under **Authentication**, choose the **Method**. For Gmail with basic authentication, use an app password (not the normal password) in **Password**. OAuth is also available.
4. For sending, tick **Enable Outgoing** and **Default Outgoing**. Check **Outgoing Server** and **Port** (587 with TLS or 465 with SSL).
5. For receiving, tick **Enable Incoming** and check **Incoming Server**. Optional: set **Append To** (for example, Lead or Issue) to create records from incoming mail.
6. Save. ERPNext tests the connection and shows an error if login fails.

**Common problems:** "Authentication failed" usually means a wrong or expired app password. If emails stay in the queue, check the [Email Queue](/app/email-queue) for the error.

**Check:** send a test document by email and confirm its status in [Email Queue](/app/email-queue).""",
	},
	{
		"id": "workflow-approval",
		"title": "Set up an approval workflow (for example, Purchase Order approval)",
		"tags": "workflow approval approve reject maker checker multi level approval purchase order approval sales order approval workflow state transition manager approval approval kaise lagaye",
		"doctypes": ["Workflow", "Workflow State", "Workflow Action Master", "Role"],
		"body": """**When to use:** when a document must be approved by a specific role before it is submitted.

1. Decide the states (for example, Draft, Pending Approval, Approved, Rejected) and the roles involved.
2. Open [new Workflow](/app/workflow/new). Enter **Workflow Name** and **Document Type** (for example, Purchase Order). Tick **Is Active**.
3. In **States**, add each **State** with its **Doc Status** (0 = Draft, 1 = Submitted, 2 = Cancelled) and the role in **Only Allow Edit For**. "Approved" should have Doc Status 1.
4. In **Transitions**, add each move: current **State**, **Action** (for example, Approve), **Next State** and the role **Allowed** to do it. Optional: add a **Condition** (for example, `doc.grand_total > 100000`) and untick **Allow Self Approval**.
5. Optional: tick **Send Email Alert** to notify approvers. Save.
6. On the document, the **Submit** button is replaced by an **Actions** menu showing the allowed actions for the user's role.

**Note:** states and actions must exist in [Workflow State](/app/workflow-state) and [Workflow Action Master](/app/workflow-action-master); new ones are created when you type them. You can also design it visually in [Workflow Builder](/app/workflow-builder).

**Check:** create a test document as a normal user and confirm it waits for the approver.""",
	},
	{
		"id": "customize-form",
		"title": "Add a custom field or change a form (Customize Form)",
		"tags": "customize form custom field add field new field hide field mandatory field change label form customization extra column field add kaise kare",
		"doctypes": ["Customize Form", "Custom Field"],
		"body": """**When to use:** to add your own fields, hide unused fields, rename labels or make fields mandatory, without coding.

1. Open [Customize Form](/app/customize-form) and select the document type in **Enter Form Type** (for example, Sales Invoice). You can also open it from a form's **⋯ → Customize** menu.
2. To add a field, add a row in **Fields** at the right position with **Label**, **Type** and **Options** (for a Link field, the linked document type). Tick **Mandatory** or **In List View** if needed.
3. To change an existing field, open its row and change the label, tick **Hidden**, or set **Mandatory**, **Read Only** or **Default**.
4. Click **Update**. Reload the form to see the change.
5. To add a field with more options (for example, **Fetch From** or **Depends On**), you can also create a [Custom Field](/app/custom-field/new) directly with **DocType**, **Label**, **Field Type** and **Insert After**.

**Note:** standard fields cannot be deleted, only hidden. Customizations survive upgrades.

**Check:** open a new document of that type and confirm the field appears where expected.""",
	},
	{
		"id": "naming-series-change",
		"title": "Change a naming series prefix or its current number",
		"tags": "naming series change prefix invoice number series series counter reset numbering start from document number format current value invoice number badalna",
		"doctypes": ["Document Naming Settings"],
		"body": """**When to use:** to change the number format of invoices or orders (for example, `SINV-26-` to `GST/26-27/`) or to set the next number.

1. Open [Document Naming Settings](/app/document-naming-settings).
2. **Change the format:** in **Setup Series for transactions**, choose the document type in **Select Transaction**. Edit **Series List for this Transaction**, one series per line. The first line is the default. Use `.YY.`, `.MM.`, `.FY.` and `.####` for year, month, fiscal year and the running number. Use **Try a Naming Series** to see a preview, then click **Update**.
3. **Change the next number:** in **Update Series Counter**, select the **Prefix**, enter the new **Current Value** (the last number used), and click **Update Series Number**.
4. To use a new series on documents, select it in the **Series** field when creating them.

**Warning:** setting the current value lower than an existing number causes "Duplicate name" errors. GST rules require a unique, continuous series per financial year (maximum 16 characters).

**Check:** create a draft document and confirm the new name after saving.""",
	},
	{
		"id": "auto-repeat",
		"title": "Create recurring invoices or orders automatically (Auto Repeat)",
		"tags": "auto repeat recurring invoice monthly invoice repeat subscription rent invoice amc recurring order automatic invoice every month har mahine invoice",
		"doctypes": ["Auto Repeat", "Sales Invoice"],
		"body": """**When to use:** to create the same invoice or order automatically every month, quarter or year (for example, rent or AMC billing).

1. Create and submit the first document (for example, a [Sales Invoice](/app/sales-invoice)). It acts as the template.
2. On that document, use **⋯ → Repeat** (or open [new Auto Repeat](/app/auto-repeat/new) and set **Reference Document Type** and **Reference Document**).
3. Set **Frequency** (Daily, Weekly, Fortnightly, Monthly, Quarterly, Half-yearly or Yearly), **Start Date** and optional **End Date**. For monthly, set **Repeat on Day** or tick **Repeat on Last Day of the Month**.
4. Optional: tick **Submit on Creation** to submit new documents automatically, and **Notify by Email** with **Recipients** to email them.
5. Save. The **Next Schedule Date** shows when the next document will be made.
6. To stop, tick **Disabled** on the Auto Repeat.

**Note:** if the document type is not available, enable **Allow Auto Repeat** for it in [Customize Form](/app/customize-form).

**Check:** the [Auto Repeat list](/app/auto-repeat) and the documents it created, shown on its dashboard.""",
	},
]
