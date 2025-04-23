# Client Background

> Disclaimer: The company and brand name referenced in this use case are entirely fictional and have been created solely to provide context and narrative for the purpose of this project.

AutoNest is a leading **belgian** digital marketplace designed to simplify the buying, selling, and ownership experience for vehicles. Founded with the vision to create a frictionless automotive ecosystem for **belgians**. AutoNest connects millions of buyers, sellers, and dealers across the country (**Belgium**), enabling smarter vehicle decisions through data, technology, and trust.

## 🔧 Core Services Offered by AutoNest

1. Vehicle Listings Marketplace 🛍️  
A seamless platform for individuals and dealers to list, browse, and purchase new or used vehicles.  
Advanced filters, pricing insights, and real-time availability.

## Business Metrics & Questions for AutoNest
Below are the key performance indicators (KPIs), metrics, and business questions the AutoNest team can answer using the current data model and tables.

### 🚗 Listings & Inventory Metrics
|Metric|Business Question|Data Source|
|---|---|---|
|**Total Active Listings**|How many cars are currently listed?|`listings.status = 'active'`|
|**New vs Used Split**|What percentage of listings are new vs used?|`listings.condition_type`|
|**Listings by Make/Model**|What are the most listed brands/models?|`listings.make`, `listings.model`|
|**Average Days on Market**|How long does a listing typically stay active?|`listings.listing_date`, `transactions.transaction_date` or status|
|**Inventory Turnover Rate**|Are listings being sold quickly?|Compare volume in `listings` vs `transactions` over time|

### 🛍️ Buyer & Seller Engagement
| Metric                       | Business Question                                    | Data Source                                               |
| ---------------------------- | ---------------------------------------------------- | --------------------------------------------------------- |
| **DAU / MAU**                | How many users are actively engaging?                | `search_activity`, `listing_engagements`                  |
| **Top Search Queries**       | What are buyers searching for the most?              | `search_activity.search_query`                            |
| **Engagements per Listing**  | Which listings generate the most clicks or contacts? | `listing_engagements.action_type` grouped by `listing_id` |
| **Seller Type Distribution** | Are more listings from dealers or individuals?       | `listings.seller_type`                                    |
| **Verified Users %**         | What % of users verified their email?                | `users.email_verified`                                    |

### 💰 Sales & Revenue Insights
|Metric|Business Question|Data Source|
|---|---|---|
|**Vehicles Sold**|How many vehicles were sold?|Count of `transactions`|
|**Average Sale Price**|What's the average sale value?|`transactions.sale_price`|
|**Payment Method Breakdown**|Which payment types are most used?|`transactions.payment_method`|
|**Top Performing Dealers**|Which dealers are selling the most?|Join `transactions.seller_id` with `dealers`|
|**Feature Promotion Revenue**|How much revenue from promoted listings?|`feature_usage.payment_id` (if monetized)|

### 📈 Pricing & Market Trends
|Metric|Business Question|Data Source|
|---|---|---|
|**Average Price by Make/Model/Year**|What are typical prices for specific cars?|`listings`, `vehicle_specs`|
|**Price Change Frequency**|How often do sellers change prices?|`pricing_history`|
|**Price Drop vs Engagement**|Does engagement increase after price drops?|Correlate `pricing_history` and `listing_engagements`|

### 🚚 Logistics & Premium Features
|Metric|Business Question|Data Source|
|---|---|---|
|**Delivery Request Rate**|How many buyers request delivery?|`transactions.delivery_requested`|
|**Feature Promotion Usage**|How often are paid listing features used?|`feature_usage`|
|_(Future)_ Service Center Bookings|Are users booking services?|(Future `service_appointments` table)|

### 🌍 Geographic Insights
| Metric                     | Business Question                     | Data Source                                  |
| -------------------------- | ------------------------------------- | -------------------------------------------- |
| **Listings by City/State** | Where are listings most concentrated? | `listings.location`                          |
| **User Geography Heatmap** | Where are our most active users from? | `users.location`, `search_activity.location` |

### 🧠 AI Recommendations & Personalization
|Metric|Business Question|Data Source|
|---|---|---|
|**Recommendation Click Rate**|Are users engaging with recommended cars?|`listing_engagements` (from "recommended")|
|**Recommendation Conversion**|Do recommendations lead to purchases?|Match `recommended listings` with `transactions`|




## Mission:
- To redefine how people buy and own cars by making the entire experience digital, data-driven, and delightful.

## Vision:
- To be the most trusted automotive platform that empowers every vehicle decision.
