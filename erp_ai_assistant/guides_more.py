"""More process guides (names verified against this ERPNext v16 system)."""

GUIDES_MORE = [
	{
		"id": "item-variants",
		"title": "Create item variants (size, colour…): Item Attribute → template → variants",
		"tags": "item variant variants size colour color attribute template has variants make variants create variants variant of sku t-shirt",
		"doctypes": ["Item", "Item Attribute", "Item Variant Settings"],
		"body": """**When to use:** one product sold in several sizes, colours or other options.

1. Create the attributes in [Item Attribute](/app/item-attribute) (for example *Size* with S, M, L and *Colour* with Red, Blue), each value with an **Abbreviation** used in the variant code.
2. Open the template item (for example **SKU001 T-shirt**), tick **Has Variants**, set **Variant Based On** = *Item Attribute* and add the attributes in **Variant Attributes**. Save. The template itself is not used in transactions.
3. Use **Create → Single Variant** (one combination) or **Multiple Variants** (all combinations you tick). Each variant is a normal item, linked by **Variant Of**.
4. Control which template changes copy to variants in [Item Variant Settings](/app/item-variant-settings).

**Check:** the template's **Variants** tab lists the new items (for example *SKU001-RED-M*), and they can be used in orders.""",
	},
	{
		"id": "auto-email-report",
		"title": "Email a report automatically every day or week (Auto Email Report)",
		"tags": "auto email report schedule send report email every monday weekly daily automatic report mail",
		"doctypes": ["Auto Email Report", "Report"],
		"body": """**When to use:** to receive a report (for example Stock Ageing or Accounts Receivable) by email on a schedule.

1. Open [Auto Email Report](/app/auto-email-report) → **+ Add**.
2. Choose the **Report**, tick **Enabled**, and set the report filters (for example **Warehouse** = *Indore Depot - Ssy*).
3. Set **Frequency** (*Daily*, *Weekdays*, *Weekly* or *Monthly*), and for weekly reports the **Day of Week** (for example *Monday*).
4. Enter **Email To** (one address per line), choose the **Format** (*HTML*, *XLSX*, *CSV* or *PDF*) and optionally tick **Send only if there is any data**. Save.
5. Use **Send Now** to test it.

**Check:** the email arrives at the next scheduled time; outgoing email must be set up in [Email Account](/app/email-account).""",
	},
	{
		"id": "export-customizations",
		"title": "Export customizations to move them to another site",
		"tags": "export customizations custom fields property setters fixtures move to another site migrate customization custom doctype export",
		"doctypes": ["Customize Form", "Custom Field", "Property Setter"],
		"body": """**When to use:** to copy custom fields and form changes from this site to another (for example from test to live).

1. See what exists: [Custom Field](/app/custom-field) (fields added by your company have *Is System Generated* unticked), [Property Setter](/app/property-setter) (changed properties) and custom screens in [DocType](/app/doctype?custom=1).
2. Open [Customize Form](/app/customize-form), pick the screen, then **⋯ → Export Customizations**, choose the **Module to Export** into, and confirm. This writes the custom fields and property setters into that module of a custom app (developer mode).
3. Commit the custom app and install/migrate it on the other site; the customizations are applied on migrate. Custom DocTypes with *Custom?* ticked can be exported the same way as fixtures in the app's `hooks.py`.
4. Without a custom app, use [Data Export](/app/data-export) / [Data Import](/app/data-import) on the Custom Field and Property Setter lists.

**Check:** on the other site, the screen shows the same extra fields after migrate.""",
	},
	{
		"id": "asset-movement",
		"title": "Move an asset to another location or employee (Asset Movement)",
		"tags": "asset movement transfer asset location move asset shift asset issue asset to employee receive asset custodian source location target location which screen",
		"doctypes": ["Asset Movement", "Asset", "Location"],
		"body": """**When to use:** an asset (laptop, machine, vehicle) moves to another location, or is handed to or returned by an employee.

1. Create the locations first in [Location](/app/location) if they do not exist.
2. Open [Asset Movement](/app/asset-movement) → **+ Add** (or, on the asset, **Create → Transfer Asset**).
3. Set **Purpose**: *Transfer* (location to location), *Issue* (to an employee), *Receipt* (back from an employee) or *Transfer and Issue*.
4. In the **Assets** table pick each **Asset**; **Source Location** fills from the asset. Set **Target Location**, and **To Employee** / **From Employee** when an employee is involved.
5. Set the **Transaction Date** and **Submit**. India Compliance also lets you add e-Waybill details on the **E-Waybill Info** tab when the asset travels between places.

**Check:** the asset's **Location** (and **Custodian**) now shows the new value, and its **Connections** list the Asset Movement. Moving an asset does not post accounting entries.""",
	},
]