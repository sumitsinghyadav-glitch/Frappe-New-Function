"""Built-in help content: step-by-step process guides and plain-language notes for common fields.
Used by Help mode (no AI, instant). Guides link to screens with /app/... URLs."""

GUIDES = [
	{
		"id": "purchase-cycle",
		"title": "Purchase Cycle: Material Request, Purchase Order, Purchase Receipt, Purchase Invoice and Payment",
		"tags": "purchase buy buying po order procure procurement vendor supplier grn receipt bill kharid kharidi purchase cycle flow process "
		"purchase process buying process p2p procure to pay goods receipt supplier bill maal mangana kharidari kaise kare saman kharidna "
		"purchase flow steps order to payment",
		"doctypes": ["Material Request", "Purchase Order", "Purchase Receipt", "Purchase Invoice", "Payment Entry"],
		"body": """**When to use:** You are buying goods or services from a supplier.

1. *(Optional)* Create a **Material Request** ([new](/app/material-request/new)) when a department needs items. Set **Purpose** to *Purchase* and submit it.
2. Create a **Purchase Order** ([new](/app/purchase-order/new)). Select the **Supplier**, set the **Required By** date, and add the **Items** with quantity and rate. Set **Set Target Warehouse** to the warehouse where the goods will arrive. Select a **Purchase Taxes and Charges Template** for GST. Click **Save**, then **Submit**.
   - To start from a Material Request, open it and click **Create > Purchase Order**.
3. When the goods arrive, open the Purchase Order and click **Create > Purchase Receipt** (GRN). Check the received quantity and the warehouse, then click **Submit**. Stock increases.
4. When the supplier's bill arrives, open the Purchase Receipt (or the Purchase Order) and click **Create > Purchase Invoice**. Enter the **Supplier Invoice No** and **Supplier Invoice Date**, then click **Submit**. The amount payable to the supplier increases.
5. To pay the supplier, open the Purchase Invoice and click **Create > Payment**. Select the bank or cash account and click **Submit**. The invoice status changes to *Paid*.

**Tip:** Always use **Create** from the previous document. Items, rates and links are copied automatically.

**Check:** The Purchase Order shows **% Received** and **% Billed**. For all orders, use the [Purchase Order Analysis](/app/query-report/Purchase Order Analysis) report.""",
	},
	{
		"id": "sales-cycle",
		"title": "Sales Cycle: Quotation, Sales Order, Delivery Note, Sales Invoice and Payment",
		"tags": "sale sales sell selling so order customer delivery challan dispatch invoice bill receipt becho bikri sales cycle flow process quotation "
		"order to cash o2c sales process selling process maal bechna bikri kaise kare customer ko bill dispatch kaise kare sales flow steps",
		"doctypes": ["Quotation", "Sales Order", "Delivery Note", "Sales Invoice", "Payment Entry"],
		"body": """**When to use:** You are selling goods or services to a customer.

1. *(Optional)* Create a **Quotation** ([new](/app/quotation/new)) to offer prices to a customer, and submit it. When the customer accepts, click **Create > Sales Order**.
2. Create a **Sales Order** ([new](/app/sales-order/new)). Select the **Customer**, set the **Delivery Date**, and add the **Items** with quantity and rate. Set **Set Source Warehouse** and select the **Sales Taxes and Charges Template** (in-state sales use CGST and SGST; out-of-state sales use IGST). Click **Save**, then **Submit**.
3. To dispatch the goods, open the Sales Order and click **Create > Delivery Note** (challan). Check the quantity and the warehouse, then click **Submit**. Stock decreases.
4. Open the Delivery Note (or the Sales Order) and click **Create > Sales Invoice**, then click **Submit**. The amount receivable from the customer increases.
   - For a small counter sale, create the Sales Invoice directly and tick **Update Stock**. No Delivery Note is needed.
5. When the customer pays, open the Sales Invoice and click **Create > Payment**. Select the bank or cash account and click **Submit**.

**Check:** The Sales Order shows **% Delivered** and **% Amount Billed**. Use the [Sales Order Analysis](/app/query-report/Sales Order Analysis) and [Accounts Receivable](/app/query-report/Accounts Receivable) reports.""",
	},
	{
		"id": "item",
		"title": "Create an Item (Product, Material or Service)",
		"tags": "item product material service sku create new item master hsn uom saman "
		"add item new product item kaise banaye item code maal product banana item setup stock item service item",
		"doctypes": ["Item"],
		"body": """**When to use:** You need a new product, raw material or service in the system.

1. Go to **Stock > Setup > Item** and click **+ Add Item** ([new](/app/item/new)).
2. Enter a short, unique **Item Code** (for example, STEEL-PIPE-2IN) and a readable **Item Name**.
3. Select the **Item Group** (for example, Products or Raw Material) and the **Default Unit of Measure** (for example, Nos, Kg or Ltr).
4. Tick **Maintain Stock** for physical goods. Untick it for services.
5. Enter the **HSN/SAC** code (6 to 8 digits). On the **Tax** tab, add the GST template (5%, 12%, 18% or 28%) for your company in the **Taxes** table.
6. *(Optional)* Tick **Has Batch No** or **Has Serial No**, enter a starting **Valuation Rate**, and set the default warehouse in the **Item Defaults** table.
7. Click **Save**.

**Next:** Add selling and buying prices in [Item Price](/app/item-price), using the *Standard Selling* and *Standard Buying* price lists.""",
	},
	{
		"id": "customer",
		"title": "Create a Customer",
		"tags": "customer client buyer party create new customer master gstin address grahak "
		"add customer naya customer customer kaise banaye party banana buyer setup customer address gst number",
		"doctypes": ["Customer"],
		"body": """**When to use:** You are selling to a new party.

1. Go to **Selling > Setup > Customer** and click **+ Add Customer** ([new](/app/customer/new)).
2. Enter the **Customer Name** and select the **Customer Type** (Company, Individual or Partnership), **Customer Group** and **Territory**.
3. Select the **GST Category** (for example, Registered Regular, Unregistered or Overseas) and enter the **GSTIN / UIN**. If the GST API is enabled, the address is filled in automatically.
4. Click **Save**. Then add an **Address** (with the state and GSTIN) and a **Contact** on the **Address & Contact** tab.
5. *(Optional)* Set the default **Price List**, the **Payment Terms Template**, and a credit limit in the **Credit & Overdue Limits** table.

**Note:** The state in the customer address decides the tax type. A customer in your state is charged CGST and SGST; a customer in another state is charged IGST.""",
	},
	{
		"id": "supplier",
		"title": "Create a Supplier",
		"tags": "supplier vendor party create new supplier master gstin address "
		"add supplier naya supplier vendor kaise banaye vikreta party banana supplier setup reverse charge rcm",
		"doctypes": ["Supplier"],
		"body": """**When to use:** You are buying from a new party.

1. Go to **Buying > Setup > Supplier** and click **+ Add Supplier** ([new](/app/supplier/new)).
2. Enter the **Supplier Name** and select the **Supplier Group** and **Supplier Type**.
3. Select the **GST Category** and enter the **GSTIN / UIN**. Tick **Reverse Charge Applicable** if reverse charge (RCM) applies.
4. Click **Save**. Then add an **Address** (with the state and GSTIN) and a **Contact**.
5. *(Optional)* Set the default **Price List**, the **Payment Terms Template** and the **Billing Currency**.""",
	},
	{
		"id": "opening-stock",
		"title": "Enter Opening Stock (Starting Quantities)",
		"tags": "opening stock initial balance starting quantity stock reconciliation adjust physical count shuruati "
		"go live opening balance stock reco stock adjustment physical stock correction stock sahi karna stock milan opening maal",
		"doctypes": ["Stock Reconciliation"],
		"body": """**When to use:** You are starting to use the system and need to enter existing stock, or a physical count shows a different quantity.

1. Go to **Stock > Tools > Stock Reconciliation** and click **+ Add** ([new](/app/stock-reconciliation/new)).
2. Set **Purpose** to *Opening Stock* for go-live, or to *Stock Reconciliation* to correct quantities after a physical count.
3. Set the **Posting Date**. To use a past date, tick **Edit Posting Date and Time** first.
4. In the **Items** table, enter the item, warehouse, quantity and valuation rate (cost per unit).
5. For opening stock, set **Difference Account** to *Temporary Opening*.
6. Click **Submit**.

**Check:** Open the [Stock Balance](/app/query-report/Stock Balance) report.""",
	},
	{
		"id": "stock-transfer",
		"title": "Move Stock Between Warehouses (Same Company)",
		"tags": "stock transfer move shift warehouse godown material transfer stock entry inter warehouse "
		"godown badalna maal shift karna stock bhejna warehouse to warehouse material receipt material issue",
		"doctypes": ["Stock Entry"],
		"body": """**When to use:** You are moving stock from one warehouse to another within the same company and the same GSTIN.

1. Go to **Stock > Stock Entry** and click **+ Add** ([new](/app/stock-entry/new)).
2. Set **Stock Entry Type** to *Material Transfer*.
3. Set the **Default Source Warehouse** and the **Default Target Warehouse**.
4. Add each item and its quantity. The rate is taken from the valuation rate automatically.
5. Click **Save**, then **Submit**. Stock moves at cost. There is no accounting effect if both warehouses use the same stock account.

**Other entry types:** *Material Receipt* (stock in without a purchase), *Material Issue* (consumption or write-off) and *Manufacture*.

**Note:** For transfers between branches with a different GSTIN, use the internal Sales Invoice flow. See *Inter-State Branch Transfer*.

**Check:** Open the [Stock Ledger](/app/query-report/Stock Ledger) report.""",
	},
	{
		"id": "internal-same-gstin",
		"title": "Branch Transfer in the Same State (Same GSTIN): Delivery Note and Purchase Receipt",
		"tags": "internal transfer branch same state same gstin delivery note purchase receipt internal customer internal supplier intra state "
		"branch transfer goods in transit internal purchase receipt branch ko maal bhejna same gst",
		"doctypes": ["Delivery Note", "Purchase Receipt"],
		"body": """**When to use:** You are sending stock between two of your own branches that share the same GSTIN.

**One-time setup:** Create an internal **Customer** with **Is Internal Customer** ticked and an internal **Supplier** with **Is Internal Supplier** ticked. Set **Represents Company** to your company on both, and link the branch addresses to both.

1. Create a **Delivery Note** ([new](/app/delivery-note/new)). Select the internal customer. Set the company address to the sending branch and the customer address to the receiving branch.
2. Set **Set Source Warehouse** to the sending warehouse and **Set Target Warehouse** to *Goods In Transit*. Click **Submit**. No GST is charged because the GSTIN is the same.
3. Open the Delivery Note and click **Create > Internal Purchase Receipt**. Set **Accepted Warehouse** to the receiving warehouse and click **Submit**.

**Result:** Stock moves at cost through the transit warehouse. No invoice is needed. You may **Close** the Delivery Note and Purchase Receipt if they show the status *To Bill*.""",
	},
	{
		"id": "internal-inter-state",
		"title": "Inter-State Branch Transfer (Different GSTIN): Sales Invoice and Purchase Invoice",
		"tags": "internal transfer branch inter state interstate different gstin igst internal sales invoice purchase invoice stock transfer gst "
		"dusre state me maal bhejna branch transfer igst internal purchase invoice goods in transit e-way bill",
		"doctypes": ["Sales Invoice", "Purchase Invoice"],
		"body": """**When to use:** You are sending stock between your own branches in different states. This is a taxable supply and IGST applies.

1. Create a **Sales Invoice** ([new](/app/sales-invoice/new)) for the internal customer and tick **Update Stock**. Set the company address to the sending branch (its GSTIN) and the customer address to the receiving branch (the other GSTIN).
2. Set **Set Target Warehouse** to *Goods In Transit* and select the **Output GST Out-state** tax template. Click **Submit**. The status changes to *Internal Transfer*.
3. Open the Sales Invoice and click **Create > Internal Purchase Invoice**. Tick **Update Stock**, set **Set Accepted Warehouse** to the receiving branch's warehouse, select the **Input GST Out-state** template, and click **Submit**.

**Result:** The output IGST at the sending branch equals the input IGST at the receiving branch. Unrealized profit or loss nets to zero. An e-way bill is required when the value exceeds ₹50,000.""",
	},
	{
		"id": "sales-return",
		"title": "Sales Return and Credit Note",
		"tags": "sales return credit note customer return goods back wapas return against invoice "
		"maal wapas aaya customer return credit memo sales return kaise kare return entry",
		"doctypes": ["Delivery Note", "Sales Invoice"],
		"body": """**When to use:** A customer returns goods, or you need to reduce an invoice amount.

1. Open the submitted **Sales Invoice** and click **Create > Return / Credit Note**. From a submitted **Delivery Note**, click **Create > Sales Return**.
2. The quantities appear as negative values. Change them to the quantities actually returned.
3. On a return invoice, tick **Update Stock** if the goods come back into the warehouse.
4. Click **Submit**. The customer's outstanding amount decreases. If a refund is due, record it with a Payment Entry.""",
	},
	{
		"id": "purchase-return",
		"title": "Purchase Return and Debit Note",
		"tags": "purchase return debit note return to supplier rejected goods wapas "
		"supplier ko maal wapas debit memo purchase return kaise kare rejected maal",
		"doctypes": ["Purchase Receipt", "Purchase Invoice"],
		"body": """**When to use:** You are sending goods back to a supplier, or the supplier's bill must be reduced.

1. Open the submitted **Purchase Receipt** and click **Create > Purchase Return**, or open the submitted **Purchase Invoice** and click **Create > Return / Debit Note**.
2. Keep only the quantities you are sending back. They are shown as negative values.
3. Click **Submit**. Stock and the amount payable to the supplier decrease.""",
	},
	{
		"id": "payment",
		"title": "Record a Payment (Received from a Customer or Paid to a Supplier)",
		"tags": "payment receive pay paid money bank cash payment entry advance receipt bhugtan bhuktan "
		"paisa aaya paisa diya payment kaise kare payment receive kaise kare upi cheque neft rtgs advance payment",
		"doctypes": ["Payment Entry"],
		"body": """**When to use:** Money is received from a customer, paid to a supplier, or moved between your bank and cash accounts.

**Fastest method:** Open the invoice and click **Create > Payment**. All details are filled in.

**Manual method:** Go to **Invoicing > Payments > Payment Entry** and click **+ Add** ([new](/app/payment-entry/new)).
1. Set **Payment Type** to *Receive* (from a customer), *Pay* (to a supplier) or *Internal Transfer* (between bank and cash).
2. Select the **Party Type** and **Party**, the **Account Paid From** and **Account Paid To** (bank or cash), and enter the **Paid Amount**.
3. For bank payments, enter the **Cheque/Reference No** (cheque number or UTR) and the **Cheque/Reference Date**.
4. Click **Get Outstanding Invoices** to allocate the payment against bills. Any unallocated amount is kept as an advance.
5. Click **Submit**.""",
	},
	{
		"id": "petty-cash",
		"title": "Petty Cash and Small Expenses",
		"tags": "petty cash expense expenses small kharcha office expense cash payment conveyance tea travel reimbursement imprest "
		"chhota kharcha cash kharcha chai nashta courier daily expense cash book petty cash ka process expense claim",
		"doctypes": ["Journal Entry", "Expense Claim"],
		"body": """**When to use:** The company pays small expenses in cash, or an employee needs to be reimbursed.

**The company pays an expense in cash** (for example, tea, courier or a small local purchase):
1. Go to **Invoicing > Payments > Journal Entry** and click **+ Add** ([new](/app/journal-entry/new)). Set **Entry Type** to *Cash Entry*.
2. In the first row, select the expense account (for example, *Miscellaneous Expenses*, *Office Maintenance Expenses* or *Travel Expenses*), enter the amount as a **Debit**, and set the **Cost Center**.
3. In the second row, select the **Cash** account and enter the same amount as a **Credit**. Add the bill number in **User Remark**, then click **Submit**.

**Top up petty cash from the bank:** Create a [Payment Entry](/app/payment-entry/new) with **Payment Type** set to *Internal Transfer*, **Account Paid From** set to the bank, and **Account Paid To** set to cash.

**An employee spent their own money:** Create an [Expense Claim](/app/expense-claim/new). After the approver approves it, click **Create > Payment** to reimburse the employee.

**Check:** The [General Ledger](/app/query-report/General Ledger) report, filtered on the Cash account, shows the petty cash book.""",
	},
	{
		"id": "journal-entry",
		"title": "Journal Entry (Adjustments, Expenses and Opening Balances)",
		"tags": "journal entry jv voucher adjustment expense opening balance accounting entry debit credit "
		"jv kaise banaye adjustment entry contra entry provision entry rectification entry bank entry cash entry",
		"doctypes": ["Journal Entry"],
		"body": """**When to use:** You need an accounting adjustment, an expense booking or an opening balance entry.

1. Go to **Invoicing > Payments > Journal Entry** and click **+ Add** ([new](/app/journal-entry/new)).
2. Select the **Entry Type** (for example, Journal Entry, Bank Entry, Cash Entry, Opening Entry or Depreciation Entry).
3. In the **Accounting Entries** table, add one row per account with a debit or a credit amount. The total debit must equal the total credit.
4. For customer or supplier accounts (Debtors or Creditors), set the **Party Type** and **Party** in the row.
5. Click **Submit**.

**Note:** For normal customer and supplier payments, use a Payment Entry instead.""",
	},
	{
		"id": "stock-reports",
		"title": "Check Stock: Balance, Ledger and Item-Wise Reports",
		"tags": "stock check balance kitna stock quantity report ledger inventory warehouse wise maal "
		"stock kitna hai available qty stock report godown me kitna maal hai current stock inventory report stock value",
		"doctypes": ["Bin"],
		"body": """**When to use:** You need to know how much stock you have, where it is, or how it moved.

- [Stock Balance](/app/query-report/Stock Balance): quantity and value of each item in each warehouse for a period.
- [Stock Ledger](/app/query-report/Stock Ledger): every stock movement in and out, with the document that caused it.
- [Stock Projected Qty](/app/query-report/Stock Projected Qty): actual quantity plus ordered quantity minus reserved quantity.
- [Warehouse Wise Stock Balance](/app/query-report/Warehouse Wise Stock Balance): total stock value of each warehouse.
- [Warehouse wise Item Balance Age and Value](/app/query-report/Warehouse wise Item Balance Age and Value): stock age and value by warehouse.

**Quick answer:** Type **stock of <item name>** here.""",
	},
	{
		"id": "accounts-reports",
		"title": "Accounts Reports: Ledger, Trial Balance, Profit and Loss, Receivables and Payables",
		"tags": "report ledger general ledger trial balance profit loss balance sheet receivable payable outstanding party balance account statement hisab "
		"p&l pnl party ledger customer statement supplier statement kitna lena hai kitna dena hai baki gst report sales register",
		"doctypes": ["GL Entry"],
		"body": """**When to use:** You need account balances, party statements or financial statements.

- [General Ledger](/app/query-report/General Ledger): all entries of an account or a party (account statement).
- [Accounts Receivable](/app/query-report/Accounts Receivable): amounts customers owe you.
- [Accounts Payable](/app/query-report/Accounts Payable): amounts you owe suppliers.
- [Trial Balance](/app/query-report/Trial Balance), [Profit and Loss Statement](/app/query-report/Profit and Loss Statement) and [Balance Sheet](/app/query-report/Balance Sheet): financial statements.
- GST: [GSTR-1](/app/gstr-1), [GST Sales Register](/app/query-report/GST Sales Register) and [GST Purchase Register](/app/query-report/GST Purchase Register).""",
	},
	{
		"id": "leave-apply",
		"title": "Apply for Leave and Approve It",
		"tags": "leave apply chutti chhutti holiday off leave application approve approval sick casual privilege "
		"leave kaise lagaye chutti kaise le leave approve kaise kare leave reject leave request cl sl pl leave approval workflow",
		"doctypes": ["Leave Application"],
		"body": """**When to use:** An employee needs time off, or an approver must approve or reject a leave request.

1. Go to **Leaves > Leave Application** and click **+ Add** ([new](/app/leave-application/new)).
2. Select the **Employee** and **Leave Type** (for example, Casual, Sick or Privilege), and set the **From Date** and **To Date**. Tick **Half Day** if needed. The available balance is shown on the form.
3. The **Leave Approver** is filled in from the employee record. Click **Save**. The approver is notified.
4. The approver opens the application, sets **Status** to *Approved* or *Rejected*, and clicks **Submit**.

**Policy rules in this system (HR-POL-01):** Casual leave is limited to 3 days at a time. Holidays within a leave period are not counted, except for Maternity Leave and Compensatory Off. You cannot approve your own leave. Only an HR Manager can enter backdated leave.

**Check:** Open the [Employee Leave Balance](/app/query-report/Employee Leave Balance) report.""",
	},
	{
		"id": "leave-setup",
		"title": "Give Leave to a New Employee (Policy Assignment and Allocation)",
		"tags": "leave allocation policy assignment new employee leave balance allocate leave control panel maternity paternity bereavement "
		"leave dena leave assign leave policy lagana carry forward leave balance nahi hai no leave allocated",
		"doctypes": ["Leave Policy Assignment", "Leave Allocation"],
		"body": """**When to use:** A new employee has joined, a new leave year starts, or an event-based leave is needed.

1. Make sure the employee record has a **Date of Joining** and a **Leave Approver**.
2. Go to **Leaves > Leave Policy Assignment** and click **+ Add** ([new](/app/leave-policy-assignment/new)). Select the **Employee**, set **Leave Policy** to *CGF Leave Policy (HR-POL-01)*, set **Assignment based on** to *Leave Period*, select the **Leave Period**, and click **Submit**. Casual and sick leave are prorated. Privilege leave accrues at 1.25 days per month.
   - To assign many employees at once, use the [Leave Control Panel](/app/leave-control-panel).
3. For event-based leave (Maternity 182 days, Paternity 5 days, Bereavement 3 days), create a **Leave Allocation** ([new](/app/leave-allocation/new)) for the employee and leave type.
4. For a new leave year, create the new period's assignment and tick **Add unused leaves from previous allocations** to carry forward privilege leave.""",
	},
	{
		"id": "employee",
		"title": "Add an Employee",
		"tags": "employee add new staff joining hire worker karmchari "
		"naya employee employee kaise banaye staff add karna new joining employee master karmachari",
		"doctypes": ["Employee"],
		"body": """**When to use:** A new person joins the company.

1. Go to **HR Setup > Employee** and click **+ Add Employee** ([new](/app/employee/new)).
2. Enter the **First Name**, **Gender**, **Date of Birth** and **Date of Joining**, and set **Status** to *Active*.
3. On the **Attendance & Leaves** tab, set the **Leave Approver** and **Holiday List**.
4. *(Optional)* Set the **User ID** (to give ERP login access), **Department**, **Designation** and **Reports to**.
5. Click **Save**. Then assign the leave policy (see *Give Leave to a New Employee*).""",
	},
	{
		"id": "cancel-amend",
		"title": "Correct a Submitted Document (Cancel and Amend)",
		"tags": "cancel amend correct mistake galti edit submitted change wrong entry delete "
		"galat entry sudharna cancel kaise kare edit nahi ho raha submitted document change cannot edit amend kaise kare",
		"doctypes": [],
		"body": """**When to use:** A submitted document has a mistake. Submitted documents cannot be edited directly, except for fields marked *Allow on Submit*.

1. Cancel the later documents first (for example, the Payment, then the Invoice, then the Receipt).
2. Open the document and click **Cancel**. If the system lists linked documents, cancel them first or use **Cancel All**.
3. Click **Amend**. A copy opens with a name ending in -1. Correct it and click **Submit**.

**Note:** Draft documents can be edited or deleted freely.""",
	},
	{
		"id": "gst-setup",
		"title": "GST Basics: Tax Templates, HSN Codes, In-State and Out-of-State Tax",
		"tags": "gst tax cgst sgst igst hsn sac template in state out state tax category gstin e-way bill einvoice "
		"gst kaise lagaye tax template galat tax wrong gst igst kyun aa raha place of supply e-invoice gst settings",
		"doctypes": ["Sales Taxes and Charges Template", "Item Tax Template"],
		"body": """**When to use:** You need to understand or correct how GST is applied.

- **Item:** Set the **HSN/SAC** code and add the item tax template (GST 5%, 12%, 18% or 28%) for each company in the **Taxes** table.
- **Transactions:** Select **Output GST In-state** (CGST and SGST) when the customer's state is the same as your company's state. Otherwise, select **Output GST Out-state** (IGST). Purchases use the matching *Input GST* templates.
- **Place of Supply** is set from the state in the customer or shipping address.
- The party's **GSTIN** comes from its address. When both sides have the same GSTIN, no GST applies (internal transfer).
- **Settings:** [GST Settings](/app/gst-settings) controls e-Waybill, e-Invoice and the GST API.""",
	},
	{
		"id": "price-list",
		"title": "Set Item Prices (Price List)",
		"tags": "price rate price list item price selling price buying price mrp dam "
		"rate kaise set kare item ka rate price change bhav keemat price update standard selling standard buying",
		"doctypes": ["Item Price", "Price List"],
		"body": """**When to use:** You want rates to fill in automatically on transactions.

1. Go to **Selling > Items & Pricing > Item Price** and click **+ Add** ([new](/app/item-price/new)).
2. Select the **Item Code** and the **Price List** (*Standard Selling* or *Standard Buying*), and enter the **Rate**.
3. Click **Save**. Transactions take the rate from the price list set on the document, customer or supplier.

**Bulk update:** Use [Data Import](/app/data-import) for the Item Price document.""",
	},
	{
		"id": "material-request",
		"title": "Material Request (Request Items to Buy or Transfer)",
		"tags": "material request indent requisition demand purchase request mr "
		"maal ki demand indent kaise banaye requirement store request item mangwana",
		"doctypes": ["Material Request"],
		"body": """**When to use:** A department needs items to be purchased, transferred or issued.

1. Go to **Stock > Material Request** and click **+ Add** ([new](/app/material-request/new)).
2. Set **Purpose** to *Purchase*, *Material Transfer*, *Material Issue* or *Manufacture*.
3. Add the items and quantities, set **Required By**, and set **Set Target Warehouse**. Click **Submit**.
4. The purchase team opens the request and clicks **Create > Purchase Order** (or **Request for Quotation**).""",
	},
	{
		"id": "holiday-list",
		"title": "Holiday List (Weekly Offs and Holidays)",
		"tags": "holiday list weekly off sunday festival holidays calendar chutti "
		"chhutti ki list tyohar weekly off kaise set kare holiday calendar holiday list assignment",
		"doctypes": ["Holiday List"],
		"body": """**When to use:** You need to define weekly offs and festival holidays for leave and attendance.

1. Go to **Leaves > Setup > Holiday List** ([open](/app/holiday-list)).
2. Set the **From Date** and **To Date**. Select the **Weekly Off** day (for example, Sunday) and click **Add to Holidays**. Then add festival dates in the holidays table.
3. Click **Save**. Assign the list to the company with a [Holiday List Assignment](/app/holiday-list-assignment), or set it on each employee.

**Note:** Holidays within a leave period are not counted as leave days, unless the leave type has **Include holidays within leaves as leaves** ticked (in this system, Maternity Leave and Compensatory Off).""",
	},
	{
		"id": "navigation",
		"title": "How to Find Anything in ERPNext (Search Bar and Shortcuts)",
		"tags": "find search navigate where open shortcut keyboard menu kahan dhundhe awesome bar list report "
		"kahan hai kaise khole screen nahi mil raha search kaise kare keyboard shortcut sidebar module",
		"doctypes": [],
		"body": """**When to use:** You cannot find a screen, document or report.

- **Search bar** (at the top, or press **Ctrl+K**): type a screen name (for example, "purchase order"), a document number, or "new purchase order".
- **Sidebar** (on the left): lists the modules (for example, Buying, Selling, Stock, Invoicing and Leaves) and their documents.
- **Lists:** Use the filters at the top, **Report View** to choose columns, and the menu to **Export** data.
- **Shortcuts:** **Ctrl+S** saves the document. **Ctrl+B** in a list creates a new document of that type. **Ctrl+K** opens the search bar. **Ctrl+G** opens global search.
- **Ask here:** Type "where is <screen name>" to get the menu path and a link.""",
	},
	{
		"id": "naming",
		"title": "Document Numbers (Naming Series)",
		"tags": "naming series number prefix document number format series numbering "
		"number kaise badle series change prefix change invoice number format document number setting",
		"doctypes": [],
		"body": """**When to use:** You want to understand or change how documents are numbered.

- Each document type has a **Series** field (for example, PUR-ORD-.YYYY.-). The next number is assigned when you save.
- To change prefixes, open [Document Naming Settings](/app/document-naming-settings).
- When a cancelled document is amended, the new copy gets a -1, -2 (and so on) suffix.""",
	},
]

FIELD_NOTES = {
	"naming_series": "The numbering format for this document (for example, PUR-ORD-.YYYY.-). The system assigns the next number automatically.",
	"company": "The company this document belongs to. Accounts, warehouses and taxes must belong to the same company.",
	"posting_date": "The accounting and stock date of the entry. Reports and ledgers use this date.",
	"set_posting_time": "Tick this to change the posting date and time (for example, to backdate an entry). Otherwise, the current date and time are used.",
	"transaction_date": "The date of the order or quotation.",
	"schedule_date": "The date by which you need the goods (Required By).",
	"delivery_date": "The date by which you promise to deliver to the customer.",
	"due_date": "The date by which payment is due. It is calculated from the payment terms.",
	"cost_center": "The department or branch used to split income and expenses in reports.",
	"project": "Links the entry to a project so that its cost and revenue can be tracked.",
	"currency": "The currency of this transaction. A currency other than the company currency requires an exchange rate.",
	"conversion_rate": "The exchange rate from the transaction currency to the company currency.",
	"selling_price_list": "The price list used to fill in selling rates automatically.",
	"buying_price_list": "The price list used to fill in buying rates automatically.",
	"price_list_rate": "The rate from the price list, before any discount.",
	"rate": "The price per unit actually charged, after discount.",
	"amount": "Quantity multiplied by rate.",
	"discount_percentage": "The discount percentage applied to the price list rate.",
	"qty": "The quantity in the selected unit of measure.",
	"uom": "The unit of measure used in this row (for example, Nos or Kg).",
	"stock_uom": "The item's base unit of measure used for stock.",
	"conversion_factor": "The number of stock units in one unit of this row's UOM (for example, 1 Box = 12 Nos).",
	"set_warehouse": "The default warehouse for all item rows. It is the source warehouse on sales and the target warehouse on purchases.",
	"set_target_warehouse": "The warehouse the goods go to. On internal transfers, this is usually Goods In Transit.",
	"set_from_warehouse": "The warehouse the goods are taken from (used on internal and subcontracting receipts).",
	"warehouse": "The warehouse this row's stock goes out of or comes into.",
	"target_warehouse": "The destination warehouse for this row (used on internal transfers).",
	"from_warehouse": "The source warehouse for this row (used on internal transfers).",
	"s_warehouse": "The source warehouse. Stock goes out of this warehouse.",
	"t_warehouse": "The target warehouse. Stock comes into this warehouse.",
	"rejected_warehouse": "The warehouse where rejected quantity is kept on a purchase receipt.",
	"update_stock": "Tick this to move stock from the invoice itself, without a separate Delivery Note or Purchase Receipt.",
	"is_return": "Marks this document as a return (credit note or debit note). Quantities are negative.",
	"return_against": "The original document this return is made against.",
	"taxes_and_charges": "The tax template (for example, Output GST In-state). It fills in the taxes table.",
	"tax_category": "Decides which tax template applies (for example, In-State, Out-State or Reverse Charge).",
	"place_of_supply": "The GST state of supply. It decides whether CGST and SGST or IGST applies.",
	"gst_category": "The party's GST status: Registered Regular, Registered Composition, Unregistered, SEZ, Overseas and others.",
	"company_gstin": "Your GSTIN used on this document. It comes from the company address.",
	"billing_address_gstin": "The customer's GSTIN. It comes from the customer address.",
	"supplier_gstin": "The supplier's GSTIN. It comes from the supplier address.",
	"is_reverse_charge": "Under reverse charge (RCM), you as the buyer pay the tax instead of the supplier.",
	"payment_terms_template": "The rule that splits payment into due dates (for example, 30 days, or 50% in advance).",
	"tc_name": "The terms and conditions template printed on the document.",
	"apply_discount_on": "Decides whether the additional discount applies to the net total or the grand total.",
	"additional_discount_percentage": "An extra discount percentage on the whole document.",
	"grand_total": "The final total, including taxes.",
	"rounded_total": "The grand total rounded to the nearest rupee.",
	"outstanding_amount": "The amount still to be paid or received on this invoice.",
	"allocate_advances_automatically": "Applies the party's advance payments to this invoice automatically.",
	"is_pos": "Marks this as a point-of-sale invoice. Payment is taken on the invoice itself.",
	"bill_no": "The supplier's invoice number, as printed on their bill (Supplier Invoice No).",
	"bill_date": "The date printed on the supplier's bill (Supplier Invoice Date).",
	"customer_address": "The customer's billing address. It decides the customer's GSTIN and state.",
	"supplier_address": "The supplier's address. It decides the supplier's GSTIN and state.",
	"company_address": "Your address and GSTIN used on this document. For a company with several GSTINs, select the correct branch.",
	"shipping_address_name": "The address where the goods are delivered.",
	"is_internal_customer": "Marks this customer as your own company or branch. It is used for stock transfers.",
	"is_internal_supplier": "Marks this supplier as your own company or branch. It is used for stock transfers.",
	"represents_company": "The company that this internal party represents.",
	"payment_type": "Receive (from a customer), Pay (to a supplier) or Internal Transfer (between your own accounts).",
	"party_type": "The type of party whose account this entry affects (for example, Customer, Supplier or Employee).",
	"party": "The customer, supplier or employee for this entry.",
	"paid_from": "The account the money goes out of (Account Paid From).",
	"paid_to": "The account the money comes into (Account Paid To).",
	"paid_amount": "The amount of the payment.",
	"reference_no": "The cheque number, UTR or bank transaction number.",
	"reference_date": "The date of the cheque or bank transaction.",
	"mode_of_payment": "The payment method (for example, Cash, Bank Transfer, UPI or Cheque). It sets the default account.",
	"stock_entry_type": "The purpose of the stock entry: Material Transfer, Material Receipt, Material Issue, Manufacture and others.",
	"purpose": "What this entry or request is for (for example, Transfer, Issue, Receipt or Purchase).",
	"basic_rate": "The cost per unit of the item in this stock entry.",
	"valuation_rate": "The cost per unit used to value stock.",
	"material_request_type": "The purpose of the request: Purchase, Material Transfer, Material Issue or Manufacture.",
	"item_code": "The code of the item (product or material).",
	"item_name": "The readable name of the item.",
	"item_group": "The category of the item. It is used for reports and defaults.",
	"is_stock_item": "Maintain Stock: tick this for physical goods tracked in warehouses. Untick it for services.",
	"has_batch_no": "Tracks this item by batch (lot) number, for example to manage expiry dates.",
	"has_serial_no": "Tracks each unit of this item by its own serial number.",
	"gst_hsn_code": "The HSN code (for goods) or SAC code (for services) used for GST.",
	"item_tax_template": "The GST rate template for this item (5%, 12%, 18% or 28%).",
	"batch_no": "The batch (lot) of the item being moved.",
	"serial_no": "The serial numbers of the units being moved.",
	"customer_group": "The category of the customer. It is used for pricing and reports.",
	"territory": "The sales region of the customer.",
	"supplier_group": "The category of the supplier.",
	"credit_limit": "The maximum unpaid amount allowed for this customer before new transactions are blocked.",
	"tax_id": "The PAN or tax ID of the party.",
	"gstin": "The 15-character GST identification number.",
	"pan": "The PAN of the party or company.",
	"leave_type": "The type of leave (for example, Casual, Sick, Privilege or Leave Without Pay).",
	"leave_approver": "The user who approves this employee's leave. It is required; without it, leave cannot be approved.",
	"from_date": "The start date.",
	"to_date": "The end date.",
	"half_day": "Tick this if the leave is for half a day. It counts as 0.5 days.",
	"total_leave_days": "The number of days counted for this leave. Holidays are excluded unless the leave type includes them.",
	"holiday_list": "The calendar of weekly offs and holidays used for leave and attendance.",
	"date_of_joining": "The employee's start date. It is used to prorate leave allocations.",
	"status": "The current stage of the document. It is set by the system or by the approver.",
	"docstatus": "The document state: 0 = Draft, 1 = Submitted, 2 = Cancelled.",
}
