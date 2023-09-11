# MA [DOR Databank](https://www.mass.gov/municipal-databank-data-analytics)

The [Division of Local Services’ Data Analytics and Resources Bureau - DLS](https://www.mass.gov/orgs/division-of-local-services) analyzes and distributes data related to local government. All analytics use the data submitted to DLS by individual cities, towns, special purpose districts, regional school districts, and state and federal agencies.

The DOR Databank is organized into five groups:

1. Revenue and Expenditures
2. Municipal Debt
3. Property Taxes
4. Socioeconomic
5. Local Aid and Taxes

   
Each Databank group has 3-22 different spreadsheets for a total of 45 different types of time series generally for all (351) Massacusetts cities and towns for a given fiscal year (6/30) with upwards of 30 years of history.  Each spreadsheet column is a timeseries.  There are 524 different time series generally indexed by ```<municipality> <year>```.  These time series range form Police, Fire and Education expenditures to annual changes in the CPI.

## Extract, Transform and Load.

Selenium extract using URLs and webpage options IDs from database table ``` common.dor_databank_definitions```, copied below.  The url is prefixed by

```python

    url_prefix = "https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport="
    
    url_suffix = "&rdSubReport=True"
    
```

#### Dor Databank Selenium Extract Definitions:

|group|series_type|url|year|dropdown|button|tab|transpose|tableau|pagination|
|--------|-----------|---|----|--------|------|---|---------|-------|----------|
|RevenueExpenses|GeneralFunds|ScheduleA.GeneralFund|islYear|islAmountType|btnSubmit||||xtGenFund-NextPageCaption|
|RevenueExpenses|FedGrants|ScheduleA.Special_Rev_Funds.SpecialRevFunds|islYear|islAmountType|btnSubmit|FedGrants|||xtFedGrants-NextPageCaption|
|RevenueExpenses|StateGrants|ScheduleA.Special_Rev_Funds.SpecialRevFunds|islYear|islAmountType|btnSubmit|StateGrants|||xtStateGrants-NextPageCaption|
|RevenueExpenses|RRA|ScheduleA.Special_Rev_Funds.SpecialRevFunds|islYear|islAmountType|btnSubmit|RRA|||xtRecResApp-NextPageCaption|
|RevenueExpenses|RevFunds|ScheduleA.Special_Rev_Funds.SpecialRevFunds|islYear|islAmountType|btnSubmit|RevFunds|||xtRevFunds-NextPageCaption|
|RevenueExpenses|OtherSpecRev|ScheduleA.Special_Rev_Funds.SpecialRevFunds|islYear|islAmountType|btnSubmit|OtherSpecRev|||xtOtherSpRev-NextPageCaption|
|RevenueExpenses|CapitalFunds|ScheduleA.CapitalProjects.CapitalProjects|islYear|islAmountType|btnSubmit||||xtCapProjects-NextPageCaption|
|RevenueExpenses|TrustFunds|ScheduleA.TrustFunds.TrustFunds|islYear|islAmountType|btnSubmit||||xtTrustFunds-NextPageCaption|
|RevenueExpenses|EnterpriseFunds|ScheduleA.EnterpriseFunds.EnterpriseFunds|islYear|islAmountType|btnSubmit||||xtEntFunds-NextPageCaption|
|RevenueExpenses|HealthInsurance|ScheduleA.HealthInsurance.HealthInsExpenditures|checkbox||||yes||ctHealthExp-NextPageCaption|
|RevenueExpenses|StabFunds|Dashboard.TrendAnalysisReports.StabFund|checkbox||btnAdvisorSubmit||||tblStabilization-NextPageCaption|
|RevenueExpenses|EmployeeWages|ScheduleA.PesonnelExpenditures.PersonnelExpenditures|islYear||btnSubmit|||mixed|ctPerExp-NextPageCaption|
|RevenueExpenses|SnowIce|BalanceSheet.SnowIce|checkbox||btnSubmit||||tblSnowIce-NextPageCaption|
|RevenueExpenses|TaxRecap|TaxRateRecap.PAGE3.LocalReceiptsAct_vs_Est|checkbox|||||||
|Debt|MunicipalDebt|https://www.mass.gov/doc/fy2020-fy2022-debt-analysis/download||||||||
|Debt|BondRatings|DLS_bond_ratings|checkbox|islCompany|btnSubmit||yes||xtblBondRatings-NextPageCaption|
|Debt|CertifiedFreeCash|Dashboard.Cat_1_Reports.CertifiedFreeCashBudget351|checkbox||btnSubmit||||TblCFC_PerBudg-NextPageCaption|
|Debt|RetainedEarnings|BalanceSheet.EntFundRetainedEarnings|checkbox||btnSubmit||yes||CrsTblEntFund-NextPageCaption|
|Debt|FreeCashProof|BalanceSheet.FreecashProofComp||islMuniCCP|btnSubmit|||||
|Debt|StabFunds351|Dashboard.Cat_1_Reports.StablPerBudget351|checkbox||btnSubmit||||TblStabl_PerBudg-NextPageCaption|
|PropertyTax|TaxRates|PropertyTaxInformation.taxratesbyclass.taxratesbyclass|checkbox||btnSubmit||||tbl_taxratesbyclass-NextPageCaption|
|PropertyTax|TaxRatesSpecial|Districts.Tax_Rates_by_Class|checkbox||btnSubmit||||tblDistTaxRateClass-NextPageCaption|
|PropertyTax|TaxLevy|Districts.Levy_By_Class_Data|checkbox||btnSubmit||||tbltaxlevybyclassdis-NextPageCaption|
|PropertyTax|NewGrowth|NewGrowth.NewGrowth_dash_v2_test|checkbox||btnSubmit|||mixed|tblNewGrowth-NextPageCaption|
|PropertyTax|OverlayReserve|Dashboard.Cat_1_Reports.OL1PerLevy351|checkbox||btnSubmit||||TblOverlayPerLevy-NextPageCaption|
|PropertyTax|PropertyTax|PropertyTaxInformation.TaxLevies.LeviesByClass|checkbox||btnSubmit||||tblTaxlevybyclass-NextPageCaption|
|PropertyTax|TaxLeviesSpecial|Districts.Levy_By_Class_Data|checkbox||btnSubmit||||tbltaxlevybyclassdis-NextPageCaption|
|PropertyTax|AverageSingleFamilyTaxBill|AverageSingleTaxBill.SingleFamTaxBill_wRange|checkbox||btnSubmit|yes|||tblSinglefamtaxbill-NextPageCaption|
|PropertyTax|AssessedValues|PropertyTaxInformation.AssessedValuesbyClass.assessedvaluesbyclass|checkbox||btnSubmit|yes|||tblassessedvalues-NextPageCaption|
|PropertyTax|AssessedValuesSpecial|Districts.Assessed_Value_By_Class|checkbox||btnSubmit||||tblassessedvalclassdis-NextPageCaption|
|PropertyTax|ExemptValues|LA4.Totals|checkbox|islMuni|btnSubmit|||mixed||
|PropertyTax|EqualizedValuations|PropertyTaxInformation.EQV.EQV|checkbox||btnSubmit|yes|yes|||
|PropertyTax|MotorVehicleExciseTax|TaxRateRecap.PAGE3.Subreports.MV_Act_Est|checkbox||btnSubmit||yes||CxtblMV_Est-NextPageCaption|
|PropertyTax|EstActReceipts|TaxRateRecap.PAGE3.LocalReceiptsAct_vs_Est|checkbox||btnSubmit|||||
|PropertyTax|ParcelCounts|PropertyTaxInformation.LA4.Parcel_counts_vals|islYear||btnSubmit|parcel_counts|||xtParcels-NextPageCaption|
|PropertyTax|ParcelValues|PropertyTaxInformation.LA4.Parcel_counts_vals|islYear||btnSubmit|parcel_valuations|||xtVals-NextPageCaption|
|PropertyTax|RevenueSources|RevenueBySource.RBS.RevbySource2|checkbox||btnSubmit||||dtCurrent-NextPageCaption|
|PropertyTax|CIPTaxShift|TaxRate.CIP_TaxShift|checkbox||btnSubmit||||tblCIP_TaxShift-NextPageCaption|
|PropertyTax|Overrides|Votes.Prop2_5.OverrideUnderride|||btnSubmit||||tblProp2_5Votes-NextPageCaption|
|PropertyTax|CapitalExclusion|Votes.Prop2_5.Capital|||btnSubmit||||tblProp2_5Votes-NextPageCaption|
|PropertyTax|DebtExclusion|Votes.Prop2_5.DebtExclusionLevyAmt|||btnSubmit||||TblDebtExcLevyAmt-NextPageCaption|
|PropertyTax|AllDebtExclusion|Votes.Prop2_5.DebtExclusionVotes|||btnSubmit||||tblProp2_5Votes-NextPageCaption|
|PropertyTax|SpecialPurposeStabFund|Votes.Prop2_5.Stabilization|||btnSubmit||||tblProp2_5Votes-NextPageCaption|
|Socioeconomic|DORIncome|DOR_Income_EQV_Per_Capita|islYear||btnAdvisorSubmit||||xtblDOR_Income_EQV_Per_Capita-NextPageCaption|
|Socioeconomic|HousingDensity|Socioeconomic.HousingSqMIle|1999,2009||btnSubmit||||tblHousingSqMile-NextPageCaption|
|Socioeconomic|HouseholdIncome|Socioeconomic.MedHouseholdFamInc|1999||btnSubmit|||||
|Socioeconomic|Population|Socioeconomic.Population.Population|checkbox||btnSubmit||yes||xtblPopulation-NextPageCaption|
|Socioeconomic|CPI|Socioeconomic.consumer.consumerpriceindex|||||yes|||
|Socioeconomic|LaborForce|Dashboard.TrendAnalysisReports.LaborForce|checkbox||btnAdvisorSubmit||||tblLaborForce-NextPageCaption|
|Socioeconomic|MotorVehicles|Socioeconomic.MotorVehicles|checkbox||btnSubmit||||tblMotorVehicle-NextPageCaption|
|Socioeconomic|RegisteredVoters|Socioeconomic.RegisteredVoters|checkbox||btnSubmit||||tblRegVoter-NextPageCaption|
|Socioeconomic|RoadMiles|Socioeconomic.RoadMIles|checkbox||btnSubmit||||tblRoadMiles-NextPageCaption|
|Socioeconomic|ResidentBirths|Number_of_Resident_Births|checkbox||btnSubmit||yes||xt_BirthNumbs-NextPageCaption|
|LocalAidTaxes|CherrySheetsAssessments|CherrySheets.CherrySheet_detail&amp;rdLinkDataLayers=CherrySheets.cherrysheetdetail_main|islYear|islRecChrg|btnBudgetType|||islBudgetType|xtCherrySheet-NextPageCaption|
|LocalAidTaxes|CherrySheetsReceipts|CherrySheets.CherrySheet_detail&amp;rdLinkDataLayers=CherrySheets.cherrysheetdetail_main|islYear|islRecChrg|btnBudgetType|||islBudgetType|xtCherrySheet-NextPageCaption|
|LocalAidTaxes|CherrySheetsDORIncomeEQV|DOR_Income_EQV_Per_Capita|islYear||btnSubmit||||xtblDOR_Income_EQV_Per_Capita-NextPageCaption|
|LocalAidTaxes|LocalMealsTax|Local_Option_Meals_Rooms|checkbox2||btnSubmit||||xt_meals-NextPageCaption|
|LocalAidTaxes|LocalRoomsTax|Local_Option_Meals_Rooms|checkbox2||btnSubmit||||xt_rooms-NextPageCaption|
|LocalAidTaxes|LocalWeedTax|Local_Option_Meals_Rooms|checkbox2||btnSubmit||||xt_ImpactFee-NextPageCaption|


## Database schema

Database tables created:

1. governance.dor_databank
    * ```<dor><year><series><value>```   
2. common.int_value_pairs
    * ```<key><item><value>```
    * ```where int_value_pairs.key = dor_databank_series with item='series'```
    
There are more than 2 million oberservations of financial statement data; almost entirely integer type.  A zscore is computed for each timeseries within a given year across all municipalities.

A single key-value table is used to store all the data with schema:

```sql
        -- Table: governance.dor_databank

        -- DROP TABLE IF EXISTS governance.dor_databank;

        CREATE TABLE IF NOT EXISTS governance.dor_databank
        (
            dor smallint NOT NULL,
            year smallint NOT NULL,
            dor_databank_series smallint NOT NULL,
            value bigint,
            zscore real,
            CONSTRAINT dor_databank_pkey PRIMARY KEY (dor, year, dor_databank_series)
        )

        TABLESPACE pg_default;

        ALTER TABLE IF EXISTS governance.dor_databank
            OWNER to polis     

```

## Databank detail

Below is a brief description of the DOR databank and links to the source data.



## [Schedule A - Revenues and Expenditures](https://www.mass.gov/lists/schedule-a-reports-revenues-expenditures-and-more)

The Schedule A is a statement of revenues, expenditures, and other year-end financial information prepared annually by the local accountant or auditor.

### Revenues

* [General Funds](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=ScheduleA.GenFund_MAIN)

The general fund is used to account for most financial resources and activities governed by the normal town meeting or city council appropriation process.

* [Special Funds](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=ScheduleA.Special_Rev_Funds.SpecialRevFunds)

Funds established by statute only, containing revenues that are earmarked for and restricted expenditures for specific purposes.

* [Capital Funds](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=ScheduleA.CapitalProjects.CapitalProjects)

Capital projects funds and bonding during fiscal year.

* [Trust Funds](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=ScheduleA.TrustFunds.TrustFunds)

Funds for money donated or transferred to a municipality with specific instructions on its use.

* [Enterprise Funds](https://dlsgateway.dor.state.ma.us/reportsrdPage.aspx?rdReport=ScheduleA.EnterpriseFunds.EnterpriseFunds)

An enterprise fund is a separate accounting and financial reporting mechanism for municipal services for which a fee is charged in exchange for goods or services.


### Expenditures

* [Health Insurance](https://dlsgateway.dor.state.ma.us/reportsrdPage.aspx?rdReport=ScheduleA.HealthInsurance.HealthInsExpenditures)

Schedule A, Parts 1 and 6, Health Insurance Expenditures


* [Stabilization funds](https://dlsgateway.dor.state.ma.us/reportsrdPage.aspx?rdReport=Dashboard.TrendAnalysisReports.StabFund)

Total Full Time Equivalent (FTE) Municipal Employees and Wages - Not by Department 

* [Wages](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=ScheduleA.PesonnelExpenditures.PersonnelExpenditures)

Snow and Ice expenditures are allowed to overspend its budget by statute.

* [Snow&Ice](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=BalanceSheet.SnowIce)

### Tax Receipts

Estimated and actual local receipts are reported to DLS annually on the Tax Rate Recapitulation form. The report below compares a community's estimated and actual local receipts for various revenue types. Please note that only estimated (budgeted) receipt data is available for the current fiscal year.

* [Tax Rate Recap Receipts](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=TaxRateRecap.PAGE3.LocalReceiptsAct_vs_Est)


## Debt

Key financial indicators and trends related to bond ratings, borrowing and the management of municipal debt.

* [Bond Ratings](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=DLS_bond_ratings)

Bond ratings issued by [Moody's](https://www.mass.gov/media/1676896/download) and [Standard & Poor's](https://www.mass.gov/media/1676891/download).

* [Certified Free Cash](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Dashboard.Cat_1_Reports.CertifiedFreeCashBudget351)

Free cash is a revenue source which results from the calculation, as of July 1, of a community's remaining, unrestricted funds from operations of the previous fiscal year based on the balance sheet as of June 30. Free cash is offset by property tax receivables and certain deficits and can be a negative number.

* [Retained Earnings](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=BalanceSheet.EntFundRetainedEarnings)

Free Cash certified from an enterprise fund is referred to as Retained Earnings. This can be used for purposes including capital improvements, reimbursing the general fund for prior year subsidies or reducing user fees.

* [Free Cash Proof](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=BalanceSheet.FreecashProofComp)

The Free Cash Calculation Report shows the data used to determine the amount of free cash certified as of June 30th of a specific fiscal year.

* [StabFunds](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Dashboard.Cat_1_Reports.StablPerBudget351)

Stabilization is a reserve fund - sometimes referred to as a "rainy day fund" - designed to accumulate funds that can later be appropriated for any lawful purpose.

* [Municipal Debt Analysis](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=https://www.mass.gov/doc/fy2020-fy2022-debt-analysis/download)

Report detailing municipal debt.  Useful terms:


    1. Long term debt consists of Bonds, USDA Rural Development Loans, Serial Notes and Refunding Notes. 

    2. Short term debt consists of [Bond Anticipation Notes](https://www.investopedia.com/terms/b/bondanticipationnote.asp)  (BAN), Federal Aid Anticipation Notes (FAAN), [Revenue Anticipation Notes](https://www.investopedia.com/terms/r/ran.asp) and [State Anticipation Notes (SAAN)](https://www.lawinsider.com/dictionary/state-bond-anticipation-note).

    3. Most long term debt issues range between 5 - 20 years, while short term issues are typically for one year or less. 

    4. A community's debt limit equals 5 percent of the most recent EQV. Prior to FY05, the municipal debt limit was 2.5 percent for cities and 5 percent for towns. The [Municipal Relief Act (Chapter 46, Section 32 of the Acts of 2003))(https://malegislature.gov/Laws/SessionLaws/Acts/2003/Chapter46) changed the debt limit to 5 percent for all cities and towns.

    5. The long term retired column refers to bond issues that have either matured or been "called in." The long term interest, short term interest and other interest columns refer to interest payments made this year on bond issues.

    6. Total Outstanding Debt refers to the remaining principal payments that have not been paid off as of July 1 of the current fiscal year. 


## Property Tax

Tax rates, assessed values, levies, Proposition 2 1/2 referendum votes and other data related to property taxes

* [TaxRatesMuni](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=PropertyTaxInformation.taxratesbyclass.taxratesbyclass_main)

City and town tax rates from FY 2003 to the present. Depending on the options chosen each year by the select board or city council, property classes can be taxed using a single rate or different rates. 


* [TaxRatesSpecial](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Districts.Tax_Rates_by_Class)

* [TaxLevy](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Districts.Levy_By_Class)

* [NewGrowth](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=NewGrowth.NewGrowth_dash_v2_test)

* [OverlayReserve](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Dashboard.Cat_1_Reports.OL1PerLevy351)

* [ExcessOverrideCapacity1](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Prop2.5.ExcessLevyCapandOverride_MAIN)

* [ExcessOverrideCapacity2](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Prop2.5.ExcessLevyCapandOverride_03_09)

### Property Tax Levies and Average Single Family Tax Bills 

* [PropertyTax](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Dashboard.TrendAnalysisReports.TaxLevyByClass)

Property tax levies by the five major property classes (residential, open space, commercial, industrial and personal property) as reported on page 1 of the annual tax rate recapitulation sheet for municipalities.


* [TaxLeviesSpecial](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Districts.Levy_By_Class)

* [AverageSingleFamilyTaxBill](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=AverageSingleTaxBill.SingleFamTaxBill_wRange)

Average single family tax bill for all communities and ranks those bills by fiscal year from the highest to lowest in the Commonwealth.

### Assessed Property Values

* [AssessesValues](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=PropertyTaxInformation.AssessedValuesbyClass.assessedvaluesbyclass)

Assessed total property values by residential, open space, commercial, industrial and personal property types for cities and town as reported by the local board of assessors through the DLS Gateway application on the LA-4 form.


* [AssessedValuesSpecial](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Districts.Assessed_Value_By_Class)

Assessed total property values by residential, open space, commercial, industrial and personal property types for cities and town as reported by the **special purpose taxing districts** assessors through the DLS Gateway application on the LA-4 form.

* [ExemptValues](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=LA4.Totals)

### Other Property Tax Related Reports

* [EqualizedValuations](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=PropertyTaxInformation.EQV.EQV)
* [MotorVehicleExciseTax](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=TaxRateRecap.PAGE3.Subreports.MV_Act_Est)
* [EstActReceipts](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=TaxRateRecap.PAGE3.LocalReceiptsAct_vs_Est)
* [ParcelCountsValues](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=PropertyTaxInformation.LA4.Parcel_counts_vals)
* [ParcelCountsValuesSpecial](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Districts.parcel_count_by_type)
* [RevenueSources](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=RevenueBySource.RBS.RevbySourceMAIN)
* [CIPTaxShift](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=TaxRate.CIP_TaxShift)

### Proposition 2 1/2 Referendum Data

* [Overrides](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Votes.Prop2_5.OverrideUnderride)
* [CapitalExclusion](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Votes.Prop2_5.Capital)
* [DebtExclusion](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Votes.Prop2_5.DebtExclusionLevyAmt)
* [AllDebtExclusion](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Votes.Prop2_5.DebtExclusionVotes)
* [SpecialPurposeStabFund](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Votes.Prop2_5.Stabilization)


## Socioeconomic Data - Income, Population and Housing Data

Select socioeconomic data from the department of revenue (DOR), Mass department of transportation (Mass DOT), secretary of state's office, department of public health (DPH), department of work force and labor (DWFL) and the US census bureau. Key economic condition indicators for cities, towns and counties.

Data relative to income, population and housing from both the DOR and the US Census Bureau.  Income is presented in the Income, EQV and Population report which is used in the formula allocation of certain cherry sheet programs and the calculation of school building assistance rates.  Other income, population and housing data relates to the US Census surveys.

* [DORIncome](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=DOR_Income_EQV_Per_Capita)
* [HousingDensity](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Socioeconomic.HousingSqMIle)
* [MedHouseholdIncome](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Socioeconomic.MedHouseholdFamInc)
* [Population](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Socioeconomic.Population.population_main)
* [CPI](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Socioeconomic.consumer.consumerpriceindex_main)
* [LaborForce](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Dashboard.TrendAnalysisReports.LaborForce)
* [MotorVehicles](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Socioeconomic.MotorVehicles)
* [RegisteredVoters](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Socioeconomic.RegisteredVoters)
* [RoadMiles](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Socioeconomic.RoadMIles)
* [ResidentBirths](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Number_of_Resident_Births)


## Local Aid/Cherry Sheets

Cherry sheet estimates, monthly local aid and other payments managed by DLS and Municipal Revenue Growth Factors (MRGF) data

    * Annually the Commissioner of Revenue must provide cherry sheet estimates, which are the best estimate of the amount of state aid and assessments.  Boards of assessors are required to use these estimates in determining their local budgets.

    * Monthly local aid payments, CPA state match, smart growth school cost reimbursement and property tax exemption reimbursements.

    * Municipal revenue growth factors (MRGFs) are a component used by the Department of Elementary and Secondary Education in determining the annual allocation of the Chapter 70 aid cherry sheet program.


* [CherrySheets](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=CherrySheets.cherrysheetdetail_main)

Estimated state aid to be received and assessments due by community, or by year and program.

* [CherrySheetsDORIncomeEQV](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=DOR_Income_EQV_Per_Capita)

* [LocalTaxes](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Local_Option_Meals_Rooms)

Monthly local aid and other payments managed by the Division of Local Services

* [CPAAdopt](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Local_Option_CPA)
* [CPA](https://www.mass.gov/doc/fy2024-community-preservation-act-state-match/download)


## Local Taxes
* [LocalOptions](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=LocalOptions.localoptions)

Municipalities may adopt certain local option statutes that will impact the assessment of local property taxes and appear in the Local Options report. 

* [MarijuanaTaxAdoption](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=LocalOptions.Local_Options_Tax)
* [LocalTaxes](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=Local_Option_Meals_Rooms)
* [RoomTaxAdoption](https://dlsgateway.dor.state.ma.us/reports/rdPage.aspx?rdReport=LocalOptions.Room_Tax_Impact_Fee)

