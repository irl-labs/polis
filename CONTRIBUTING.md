
# Contributing

There are many ways to contribute to the polis.

#### Bug fixes   

Bug fixes, especialy for existing data sets can be most helpful.  All cells in all tables are editable; all changes are recorded separately and incorporated optionally by the end user.  Track records for editors are based on adoption of changes by users. Bug fixes will be rewarded with bounties and other incentives over time.
   
#### Code development
   
Code development is always welcomed.  See the [issues]() secton of the gitlab repository for known problems and enhancement requests, all waiting for anyone to figure out solutions.  In addition, the front end code - [dash](), [plotly]() on top of [flask]() is pathetic.  Read the ongoing discussion and development efforts on the [discord dev channel]().  Our back-end is a postgresql database for its [postgis]() package for spatial data storage and manipulation as well as the uint256 support for certain interfaces.  Postgresql also fits nicely with our open source commitment.  The volume and low latency of updates don't seem to require more advanced databases, but porting of the schemas to other platforms is a natural avenue. ETL replaced with ELT plays out in the backend endlessly.

New views into existing datasets are valuable contributions requiring less technical skills.  Many of the table, chart and map views are available as stand-alone [notebooks]() for data exploration and experimentation.  The current implementation of charts and maps barely scratch the surface of plotly capabilities.  Data visualizations, animations and presentations are the reason this project exists.  Data science contributions would be awesome.

#### Data

New sources of data, conforming to the data standards of privacy, reproducibility, coverage and applicability can be an important contribution to polis.  Read our [data standard]() for some guidelines and practices.  Contribute by making our data standards more coherent and self-consistent.  Mechanisms for automatically adding new data sources is an ongoing code devlopement project.

Another contribution would be adding a new city, town, state, country as a new polis.  Hosting the raw data, creating an open data set, new docker is the goal of the polis project.

#### Analysis/Opinion

Blogs ([medium](), other) are an easy way to contribute.  Every chart, map and table has a placeholder for links to long format explanations, analysis and opinions about the data presented in polis.  The [submission guidelines]() suggest a few principles; all data used in the blog post must be hosted on polis.  All results should be reproducible through gists, notebooks and other documented recipes.  

New charts, maps and tables are also welcomed contributions and likely to be developed through contributed blog posts.  Adding new views in existing data is as easy as creating a new [parameter]() entry.

#### Support 

Donations in the form of [BTC](), [ETH]() or [USDC]() are used to offset hosting costs of the generic polis front end, bug bounties, dev incentives and certain storage costs.  These are minimal costs at this time and all donations and expenditures are open for inspection.  Donations are not tax deductible.
