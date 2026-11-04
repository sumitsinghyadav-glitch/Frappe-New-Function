"""Additional troubleshooting entries (accounts and stock setup errors)."""

PROBLEMS = [
	{
		"id": "default-inventory-account-missing",
		"title": "Default inventory account is not set for the warehouse or company",
		"errors": ["please set default inventory account", "default inventory account", "set account in warehouse", "inventory account not set", "please set account in warehouse"],
		"tags": "default inventory account warehouse account perpetual inventory stock account company purchase receipt delivery note stock entry not submitting set",
		"doctypes": ["Company", "Warehouse", "Purchase Receipt", "Stock Entry"],
		"cause": "With perpetual inventory, every stock movement also posts to a stock (inventory) account. ERPNext looks for the account on the **Warehouse** first, then on the **Item Default** row, then on the **Company**. If none is set, the stock document cannot be submitted.",
		"solution": """1. Open [Company](/app/company) → your company → **Accounts** tab and set **Default Inventory Account** (for example *Stock In Hand - <abbr>*). Save.
2. To use a different account for one warehouse, open [Warehouse](/app/warehouse) → the warehouse and set its **Account** field.
3. Make sure the account is a ledger account (not a group) of type *Stock* and belongs to the same company.
4. Submit the Purchase Receipt, Delivery Note or Stock Entry again.

**Check:** the document submits and its accounting ledger shows a debit or credit to the inventory account.""",
	},
	{
		"id": "unrealized-exchange-gain-loss-account",
		"title": "Unrealized Exchange Gain/Loss Account is not set in Company",
		"errors": ["unrealized exchange gain/loss account", "please set unrealized exchange gain/loss account", "exchange gain / loss account", "please set exchange gain/loss account"],
		"tags": "unrealized exchange gain loss account foreign currency revaluation exchange rate revaluation multi currency company account missing",
		"doctypes": ["Company", "Exchange Rate Revaluation", "Payment Entry"],
		"cause": "Foreign-currency invoices and payments, and the **Exchange Rate Revaluation** tool, post currency differences to the company's exchange gain/loss accounts. If those accounts are blank, the document stops with this message.",
		"solution": """1. Open [Company](/app/company) → your company → **Accounts** tab → **Exchange Gain / Loss** section.
2. Set **Exchange Gain / Loss Account** (realized differences on payments) and **Unrealized Exchange Gain/Loss Account** (used by Exchange Rate Revaluation). Use income/expense ledger accounts, for example *Exchange Gain/Loss - <abbr>*. Save.
3. Retry the payment or the [Exchange Rate Revaluation](/app/exchange-rate-revaluation).

**Check:** the document submits and its accounting ledger shows the difference posted to the exchange gain/loss account.""",
	},
	{
		"id": "rate-must-be-same-as-order",
		"title": "Rate must be the same as in the Purchase Order or Sales Order",
		"errors": ["rate must be same as", "rate cannot be greater than the rate in purchase order", "rate different from purchase order", "rate is not same as", "same rate is not maintained"],
		"tags": "rate must be same maintain same rate purchase cycle sales cycle purchase order rate higher receipt invoice rate changed stop warn buying settings selling settings",
		"doctypes": ["Buying Settings", "Selling Settings", "Purchase Receipt", "Purchase Invoice", "Delivery Note", "Sales Invoice"],
		"cause": "**Maintain same rate throughout the purchase cycle** (Buying Settings) or **Maintain same rate throughout sales cycle** (Selling Settings) is ticked. A receipt or invoice made from an order must then use the order's rate. When **Action if same rate is not maintained** is *Stop*, a different rate blocks the document; when it is *Warn*, you only see a message.",
		"solution": """1. If the order rate is correct, change the row **Rate** back to the order's rate and save again.
2. If the supplier or customer has genuinely changed the price, update the order first (cancel and amend it, or use **Update Items** on a submitted order if allowed), then make the receipt or invoice from it again.
3. To allow different rates, open [Buying Settings](/app/buying-settings) or [Selling Settings](/app/selling-settings) and either untick **Maintain same rate…** or set **Action if same rate is not maintained** to *Warn*. A user with the **Role Allowed to Override Stop Action** can also pass the check.

**Check:** the receipt or invoice saves, and its rows show the intended rate.""",
	},
	{
		"id": "return-rate-greater-than-original",
		"title": "Return rate cannot be greater than the original document's rate",
		"errors": ["rate cannot be greater than the rate used in", "cannot be greater than the rate used"],
		"tags": "return rate greater than original credit note debit note return against rate higher sales return purchase return",
		"doctypes": ["Sales Invoice", "Purchase Invoice", "Delivery Note", "Purchase Receipt"],
		"cause": "A return (credit note or debit note) refunds what was originally charged. ERPNext stops a return row whose rate is higher than the rate on the original document it is made against (**Return Against**).",
		"solution": """1. Open the return and check **Return Against** points to the right original document.
2. Set each row's **Rate** to the original rate or lower (lower is allowed, for example for a partial refund).
3. To give the customer an extra amount, return at the original rate and record the extra as a separate credit note or a Journal Entry.

**Check:** the return saves and its **Grand Total** is not more than the original document's value for the returned quantity.""",
	},
	{
		"id": "wip-warehouse-not-set",
		"title": "Work In Progress Warehouse is not set on the Work Order",
		"errors": ["please set work in progress warehouse", "work in progress warehouse is mandatory", "set wip warehouse", "wip warehouse not set", "work-in-progress warehouse"],
		"tags": "work in progress warehouse wip warehouse work order manufacture default company set every time manually target warehouse mandatory",
		"doctypes": ["Work Order", "Company", "Manufacturing Settings"],
		"cause": "A Work Order needs a **Work-in-Progress Warehouse** where raw materials wait during production, unless **Skip Material Transfer to WIP Warehouse** is ticked. The value is filled from the Company default; if that is blank, you must type it every time.",
		"solution": """1. Open [Company](/app/company) → your company and set **Default Work In Progress Warehouse** (for example *Work In Progress - <abbr>*). Also check **Default Finished Goods Warehouse**. Save.
2. New Work Orders now fill the WIP warehouse automatically. For the current one, set **Work-in-Progress Warehouse** on the Work Order and submit again.
3. If you transfer materials straight from the store without a WIP stage, tick **Skip Material Transfer to WIP Warehouse** on the Work Order instead.

**Check:** a new Work Order shows the WIP warehouse filled in and submits without the message.""",
	},
	{
		"id": "depreciation-not-posted-automatically",
		"title": "Asset depreciation is not posted automatically",
		"errors": ["depreciation not booking", "depreciation not posted", "journal entry not created for depreciation", "depreciation entries not created", "schedule rows have no journal entry"],
		"tags": "asset depreciation not booking automatically schedule past dates journal entry missing book asset depreciation entry automatically accounts settings scheduler depreciation entry",
		"doctypes": ["Asset", "Asset Depreciation Schedule", "Accounts Settings", "Journal Entry"],
		"cause": "Depreciation rows are turned into Journal Entries by a daily scheduled job, but only when **Book Asset Depreciation entry automatically** is ticked in Accounts Settings and the scheduler is running. Otherwise the rows stay unposted.",
		"solution": """1. Open [Accounts Settings](/app/accounts-settings) and tick **Book Asset Depreciation entry automatically**. Save.
2. Make sure background jobs run: [System Settings](/app/system-settings) must not have the scheduler disabled (a System Manager can check **Scheduler** status in [System Health Report](/app/system-health-report)).
3. To post the overdue rows now, open the asset's depreciation schedule and use the **Depreciation Entry** action on each due row, or wait for the next daily run.

**Check:** the schedule rows show a **Journal Entry** link and the [Asset Depreciation Ledger](/app/query-report/Asset Depreciation Ledger) lists the postings.""",
	},
	{
		"id": "customize-label-not-updating",
		"title": "A change made in Customize Form does not show to users",
		"errors": ["still see the old label", "old label", "label not changing", "customize form change not visible", "changes not reflecting"],
		"tags": "customize form label renamed still old label not reflecting not visible property setter clear cache hard refresh translation reload",
		"doctypes": ["Customize Form", "Property Setter", "Translation"],
		"cause": "Form layouts are cached in the browser and on the server. If a **Translation** exists for the old label, it also overrides your new label.",
		"solution": """1. In [Customize Form](/app/customize-form), confirm the change was saved: it is stored as a [Property Setter](/app/property-setter) for that field.
2. Ask users to reload the page without cache (**Ctrl+Shift+R**). A System Manager can also run **⋯ → Reload** / clear cache.
3. If the label is still old, open [Translation](/app/translation) and look for a translation of the old text in the user's language; edit or delete it.

**Check:** after a hard refresh the form shows the new label for every user.""",
	},
	{
		"id": "group-account-in-transaction",
		"title": "Cannot post accounting entries against a group account",
		"errors": ["cannot create accounting entries against group accounts", "against group accounts", "is a group account", "group account cannot be used", "account is a group"],
		"tags": "group account is group ledger account chart of accounts parent account child account leaf posting not allowed",
		"doctypes": ["Account", "Journal Entry", "Payment Entry", "Company"],
		"cause": "In the Chart of Accounts, accounts with **Is Group** ticked are headings that only total their child accounts. Transactions can only post to ledger (non-group) accounts.",
		"solution": """1. Open the [Chart of Accounts](/app/account/view/tree) and find the account named in the message.
2. Pick one of its child ledger accounts instead (or add one with **Add Child**, leaving **Is Group** unticked).
3. Update the document, or the default that filled it (Company defaults, Item Default, Customer/Supplier **Default Accounts**, Mode of Payment account), to use the ledger account.
4. Submit again.

**Check:** the account selected in the document shows **Is Group = No**.""",
	},
]
