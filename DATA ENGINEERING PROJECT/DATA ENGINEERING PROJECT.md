DATA ENGINEERING PROJECT

\---------------------------



This project builds a complete, production-style data platform for an e-commerce company on AWS. It ingests data from three different source types (a relational database, CSV files, and a REST API), lands it in a raw zone in Amazon S3, cleans and transforms it using AWS Glue, catalogs it for SQL querying, and analyzes it using Amazon Athena. Optionally, the modeled data is also loaded into a Redshift star-schema warehouse for high-performance analytics.



Pipeline stages: Ingest → Store → Transform → Catalog → Analyze → (optional) Warehouse



STEPS 

\---------



1.CREATE KMS Encryption Key



&#x20; Customer managed keys → Create key → Key type: Symmetric. → Usage: Encrypt and decrypt  → Alias: ecom-datalake-key 



2\. CREATE IAM ROLE 

&#x20;

&#x20;  -- ecom-dms-role : TE = DMS 

&#x20;                     INLINE POLICY :{

&#x20; "Version": "2012-10-17",

&#x20; "Statement": \[

&#x20;   {

&#x20;     "Effect": "Allow",

&#x20;     "Action": \["s3:PutObject","s3:DeleteObject","s3:PutObjectTagging","s3:GetObject"],

&#x20;     "Resource": "arn:aws:s3:::ecom-raw-<ACCOUNT\_ID>/\*"

&#x20;   },

&#x20;   {

&#x20;     "Effect": "Allow",

&#x20;     "Action": \["s3:ListBucket","s3:GetBucketLocation"],

&#x20;     "Resource": "arn:aws:s3:::ecom-raw-<ACCOUNT\_ID>"

&#x20;   },

&#x20;   {

&#x20;     "Effect": "Allow",

&#x20;     "Action": \["kms:GenerateDataKey","kms:Encrypt","kms:Decrypt"],

&#x20;     "Resource": "\*"

&#x20;   }

&#x20; ]

}



&#x20;   --ecom-lambda-role :     TE      = LAMBDA

&#x20;                        PERMISSIONS =  AWSLambdaBasicExecutionRole, AmazonS3FullAccess, SecretsManagerReadWrite



&#x20;   

&#x20;   --ecom-glue-role : TE           = GLUE

&#x20;                      PERMISSIONS  = AWSGlueServiceRole, AmazonS3FullAccess



&#x20;    --ecom-redshift-role : TE          = REDSHIFT

&#x20;                           PERMISSIONN = AmazonS3ReadOnlyAccess, AWSGlueConsoleFullAccess

&#x20;

&#x20;   -- dms-vpc-role       : TE          = DMS 

&#x20;                           PERMISSIONN = AmazonDMSVPCManagementRoe

&#x20;   

&#x20;  -- dms-cloudwatch-logs-role : TE             = DMS 

&#x20;                                PERMISSION    =  AmazonDMSCloudWatchLogsRole.





3.Give the roles access to the KMS key

&#x20;

&#x20; Go back to KMS → Customer managed keys → click ecom-datalake-key  → Scroll to Key users → Add.  → Tick all five roles → Add.



4.CREATE YOUR OWN VPC 



&#x20; VPC endpoints: S3 Gateway



5\. Create three security groups



&#x20;  VPC → Security groups

&#x20;   

&#x20;  - DMS-SG : INBOUND RULE → NONE

&#x20;  -EC2-SG  : INBOUND RULE → SSH, port 22, source My IP

&#x20;  -RDS-SG  : INBOUND RULE → MySQL/Aurora (3306) with source sg-dms \&\&\& MySQL/Aurora (3306) with source sg-ec2





6\. CREATE S3 BUCKETS 



&#x20;-- CREATE BUCKETS WITH ENABLED VERSIONING AND PRIVATE BUCKETS ALSO USE Default encryption: SSE-KMS → Choose from your AWS KMS keys → ecom-datalake-key



BUCKET NAME : YOU CAN MENTIONANY NAME BUT CREATE 5 BUCKETS    

&#x20;-- ecom-raw-tejes

&#x20;  -- ecom-processed-tejes

&#x20;  -- ecom-curated-tejes

&#x20;  -- ecom-athena-results-tejes

&#x20;  -- ecom-scripts-tejes  



&#x20; 

7\. CREATE PREFIXES INSIDE THE S3 BUCKET 



&#x20;  raw →	mysql, csv, api

raw/csv →	product\_catalog, sales\_data, reviews

processed →	cleaned

curated	→       sales, customers, products



8.Create the database password secret



&#x20;Secrets Manager → Secrets Manager → Store a new secret → Secret type: Other type of secret.



&#x20; Add these key/value row :: 

username = admin

password = root123456

host = pending

port = 3306

dbname = ecommerce 



Encryption key: choose ecom-datalake-key



8\. Create the MySQL database



&#x20;DB instance identifier: ecom-mysql

Master username        : admin

Credentials management : Self managed → type the same password as in your secret

VPC : CREATED VPC 

Initial database name  : ecommerce



9\. Go to Secrets Manager → ecom/rds-mysql → Retrieve secret value → Edit → change host = RDS END POINT→ Save.



10.LAUNCH EC2 INSTANCE AND USE CREATED VPC AND SSH INTO IT AND CONNECT TO RD DATABASE 



11 . NOW CREATE TABLES 

\------------------------------------

&#x20; 

&#x20;  USE ecommerce;



CREATE TABLE customers (

&#x20; customer\_id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(150),

&#x20; state VARCHAR(50), city VARCHAR(50), created\_at DATETIME);



CREATE TABLE products (

&#x20; product\_id INT PRIMARY KEY, name VARCHAR(150), category VARCHAR(50),

&#x20; price DECIMAL(10,2));



CREATE TABLE orders (

&#x20; order\_id INT PRIMARY KEY, customer\_id INT, order\_date DATETIME,

&#x20; status VARCHAR(20), total\_amount DECIMAL(12,2), updated\_at DATETIME);



CREATE TABLE order\_items (

&#x20; item\_id INT PRIMARY KEY, order\_id INT, product\_id INT,

&#x20; quantity INT, unit\_price DECIMAL(10,2));



CREATE TABLE payments (

&#x20; payment\_id INT PRIMARY KEY, order\_id INT, method VARCHAR(30),

&#x20; status VARCHAR(20), amount DECIMAL(12,2), paid\_at DATETIME);



CREATE TABLE inventory (

&#x20; product\_id INT PRIMARY KEY, stock\_qty INT, updated\_at DATETIME);



CALL mysql.rds\_set\_configuration('binlog retention hours', 24);

\-----------------------------------------------------------------------------



12.Insert sample data

\------------------------------

INSERT INTO customers VALUES

(1,'Asha Rao','asha@mail.com','Telangana','Hyderabad','2026-01-05 10:00:00'),

(2,'Ravi Kumar','RAVI@mail.com ','Karnataka','Bengaluru','2026-01-07 11:30:00'),

(3,'Meena Iyer',NULL,'Tamil Nadu','Chennai','2026-02-01 09:15:00'),

(4,'Asha Rao','asha@mail.com','Telangana','Hyderabad','2026-02-10 14:00:00'),

(5,'John Dsouza','john@mail.com',NULL,NULL,'2026-03-02 16:45:00');



INSERT INTO products VALUES

(101,'Wireless Mouse','Electronics',799.00),

(102,'Running Shoes','Footwear',2499.00),

(103,'Water Bottle',NULL,349.00),

(104,'Laptop Bag','Accessories',1299.00);



INSERT INTO orders VALUES

(1001,1,'2026-03-01 10:10:00','DELIVERED',3298.00,'2026-03-03 10:00:00'),

(1002,2,'2026-03-05 12:00:00','SHIPPED',799.00,'2026-03-06 09:00:00'),

(1003,3,'2026-03-10 15:30:00',NULL,349.00,'2026-03-10 15:30:00'),

(1004,1,'2026-04-02 09:00:00','CANCELLED',1299.00,'2026-04-02 12:00:00'),

(1005,5,'2026-04-15 18:20:00','DELIVERED',NULL,'2026-04-17 10:00:00');



INSERT INTO order\_items VALUES

(1,1001,101,1,799.00),(2,1001,102,1,2499.00),

(3,1002,101,1,799.00),(4,1003,103,1,349.00),

(5,1004,104,1,1299.00),(6,1005,102,1,2499.00);



INSERT INTO payments VALUES

(1,1001,'UPI','SUCCESS',3298.00,'2026-03-01 10:12:00'),

(2,1002,'CARD','SUCCESS',799.00,'2026-03-05 12:01:00'),

(3,1003,'COD','PENDING',349.00,NULL),

(4,1004,'CARD','FAILED',1299.00,'2026-04-02 09:02:00'),

(5,1005,'UPI','SUCCESS',2499.00,'2026-04-15 18:22:00');



INSERT INTO inventory VALUES

(101,50,NOW()),(102,20,NOW()),(103,NULL,NOW()),(104,15,NOW());

\--------------------------------------------------------------------------



13\. : DMS (RDS → S3)



&#x20;    Subnet groups → Create subnet group  → Name: ecom-dms-subnets → VPC: ecom-vpc → Add both private subnets 



&#x20;     Replication instances → Create replication instance

&#x20;   

&#x20;    CREATE SOURCE ENDPOINTS AND DESTINATION ENDPOINTS AND RUN THE TEST IT SHOULD BE SUCCESFULL

&#x20;  

&#x20;   Database migration tasks → Create task --- Table mappings → Editing mode: Wizard → Add new selection rule: Schema : ecommerce 



14\. CREATE ANY THREE SAMPLE CSV FILE (STORE IT IN LOCAL COMPUTER ) AND UPLOAD IT TO S3 BUCKETS 



15\. Lambda → Create function → Author from scratch → Use an existing role → ecom-lambda-role



\----------------------------------------------------------------------------------------------------------

&#x20;

&#x20;   On the Code tab, open lambda\_function.py, delete everything, and paste this:



&#x20;import boto3, csv, io, urllib.parse

from botocore.exceptions import ClientError



s3 = boto3.client("s3")



REQUIRED = {

&#x20;   "product\_catalog": {"product\_id", "name", "category", "price"},

&#x20;   "sales\_data": {"order\_id", "product\_id", "quantity", "sale\_date"},

&#x20;   "reviews": {"product\_id", "rating", "review\_text"},

}



def lambda\_handler(event, context):

&#x20;   for rec in event\["Records"]:

&#x20;       bucket = rec\["s3"]\["bucket"]\["name"]

&#x20;       key = urllib.parse.unquote\_plus(rec\["s3"]\["object"]\["key"])



&#x20;       # Skip folder placeholders and non-CSV files

&#x20;       if key.endswith("/") or not key.lower().endswith(".csv"):

&#x20;           print(f"Skipping {key}")

&#x20;           continue



&#x20;       parts = key.split("/")            # csv/<dataset>/<file>.csv

&#x20;       dataset = parts\[1] if len(parts) > 2 else ""



&#x20;       try:

&#x20;           body = s3.get\_object(Bucket=bucket, Key=key)\["Body"].read().decode("utf-8-sig")

&#x20;       except ClientError as e:

&#x20;           print(f"Cannot read {key}: {e}")   # already moved on an earlier run

&#x20;           continue



&#x20;       rows = csv.reader(io.StringIO(body))

&#x20;       header = {h.strip() for h in next(rows, \[])}

&#x20;       required = REQUIRED.get(dataset)



&#x20;       if required is None or not required.issubset(header):

&#x20;           s3.copy\_object(Bucket=bucket, Key=f"quarantine/{key}",

&#x20;                          CopySource={"Bucket": bucket, "Key": key})

&#x20;           s3.delete\_object(Bucket=bucket, Key=key)

&#x20;           print(f"QUARANTINED {key}. Header was {sorted(header)}")

&#x20;           continue



&#x20;       print(f"VALID {key}")

&#x20;   return {"status": "ok"} 



\--------------------------------------------------------------------------------------------------------------------



16\. ADD S3 TRIGGER IN THIS LAMBDA FUNCTION

&#x20;  

&#x20;  On the function page click Add trigger → S3.



17.Lambda → Create function → name ecom-api-ingest



&#x20;   existing role ---  ecom-lambda-role.

\--------------------------------------------------------------------------------------------------------------------

Paste this into lambda\_function.py, then click Deploy: 



&#x20;import boto3, json, os, random, urllib.request

from datetime import datetime, timezone



s3 = boto3.client("s3")

sm = boto3.client("secretsmanager")



ENDPOINTS = {"shipping": "/shipping", "ratings": "/ratings", "suppliers": "/suppliers"}



def get\_api\_key():

&#x20;   raw = sm.get\_secret\_value(SecretId="ecom/shipping-api-key")\["SecretString"]

&#x20;   try:

&#x20;       return json.loads(raw)\["api\_key"]      # secret stored as key/value

&#x20;   except Exception:

&#x20;       return raw                             # plain-text secret



def fetch(path, key):

&#x20;   req = urllib.request.Request(os.environ\["API\_URL"].rstrip("/") + path,

&#x20;                                headers={"Authorization": f"Bearer {key}"})

&#x20;   with urllib.request.urlopen(req, timeout=30) as r:

&#x20;       return json.loads(r.read())



def mock(name):

&#x20;   """Sample data used when no real API is configured."""

&#x20;   if name == "shipping":

&#x20;       return \[{"order\_id": 1000 + i, "carrier": random.choice(\["Delhivery", "BlueDart", "Ekart"]),

&#x20;                "status": random.choice(\["IN\_TRANSIT", "DELIVERED", "RETURNED"]),

&#x20;                "shipping\_cost": round(random.uniform(40, 150), 2)} for i in range(1, 8)]

&#x20;   if name == "ratings":

&#x20;       return \[{"product\_id": 101 + (i % 4), "rating": random.randint(1, 5)} for i in range(10)]

&#x20;   return \[{"supplier\_id": i, "name": f"Supplier {i}", "lead\_days": random.randint(2, 10)}

&#x20;           for i in range(1, 5)]



def lambda\_handler(event, context):

&#x20;   now = datetime.now(timezone.utc)

&#x20;   use\_mock = not os.environ.get("API\_URL")

&#x20;   key = None if use\_mock else get\_api\_key()



&#x20;   for name, path in ENDPOINTS.items():

&#x20;       records = mock(name) if use\_mock else fetch(path, key)

&#x20;       body = "\\n".join(json.dumps(r) for r in records)          # JSON Lines

&#x20;       s3\_key = f"api/{name}/dt={now:%Y-%m-%d}/{name}\_{now:%H%M%S}.json"

&#x20;       s3.put\_object(Bucket=os.environ\["RAW\_BUCKET"], Key=s3\_key, Body=body.encode("utf-8"))

&#x20;       print(f"Wrote {len(records)} records to {s3\_key}")

&#x20;   return {"status": "done", "mock": use\_mock, "ts": now.isoformat()}

&#x20;

\--------------------------------------------------------------------------------------------------------------------



&#x20;18. Create the Glue databases : create 3 databases



&#x20; 	AWS Glue → Data Catalog → Databases → Add database. → Name: ecom\_raw

&#x20; 

&#x20;       AWS Glue → Data Catalog → Databases → Add database. → Name: ecom\_PROCESSED



&#x20;      AWS Glue → Data Catalog → Databases → Add database. → Name: ecom\_curated



19\.  Create the raw crawlers

&#x20;

&#x20;   Crawlers → Create crawler → Name: crawler-raw-MySQL 

&#x20;   IAM role: choose the existing role ecom-glue-role.→ Target database: ecom\_raw.
    

&#x20; AFTER CREATION OF THIS CREATE THE SAME FOR crawler-raw-csv \&\&\& crawler-raw-api NAD RUN THEM INDIVIDUALLY.





20\. Glue job 1, raw → processed

&#x20;

&#x20;   ETL jobs → Script editor. → Engine: Spark. Options: Start fresh. Click Create script.

\--------------------------------------------------------------------------------------------------------------------



import sys

from awsglue.utils import getResolvedOptions

from awsglue.context import GlueContext

from awsglue.job import Job

from pyspark.context import SparkContext

from pyspark.sql import functions as F, Window



args = getResolvedOptions(sys.argv, \["JOB\_NAME", "PROCESSED\_PATH"])

sc = SparkContext()

glue = GlueContext(sc)

job = Job(glue)

job.init(args\["JOB\_NAME"], args)

P = args\["PROCESSED\_PATH"].rstrip("/")



def read(table):

&#x20;   df = glue.create\_dynamic\_frame.from\_catalog(

&#x20;       database="ecom\_raw", table\_name=table).toDF()

&#x20;   return df.toDF(\*\[c.lower() for c in df.columns])      # lowercase all columns



def latest(df, key):

&#x20;   """Apply DMS changes: newest row per key, drop rows whose last change was a delete."""

&#x20;   if "op" not in df.columns:

&#x20;       df = df.withColumn("op", F.lit("I"))

&#x20;   if "dms\_ts" not in df.columns:

&#x20;       df = df.withColumn("dms\_ts", F.lit(None).cast("string"))

&#x20;   w = Window.partitionBy(key).orderBy(F.col("dms\_ts").desc\_nulls\_last())

&#x20;   df = df.withColumn("\_rn", F.row\_number().over(w)).filter("\_rn = 1").drop("\_rn")

&#x20;   return df.filter(F.col("op") != "D").drop("op", "dms\_ts")



def write(df, name, parts=None):

&#x20;   w = df.write.mode("overwrite")

&#x20;   if parts:

&#x20;       w = w.partitionBy(\*parts)

&#x20;   w.parquet(f"{P}/{name}/")

&#x20;   print(f"{name}: {df.count()} rows written")



zero12 = F.lit(0).cast("decimal(12,2)")



\# ---------- ORDERS ----------

orders = (latest(read("orders"), "order\_id")

&#x20;   .dropDuplicates(\["order\_id"])

&#x20;   .withColumn("order\_date", F.to\_timestamp("order\_date"))

&#x20;   .withColumn("total\_amount", F.coalesce(F.col("total\_amount").cast("decimal(12,2)"), zero12))

&#x20;   .fillna({"status": "UNKNOWN"})

&#x20;   .filter(F.col("customer\_id").isNotNull())

&#x20;   .withColumn("order\_year", F.year("order\_date"))

&#x20;   .withColumn("order\_month", F.month("order\_date")))

write(orders, "orders", \["order\_year", "order\_month"])



\# ---------- ORDER ITEMS ----------

items = (latest(read("order\_items"), "item\_id")

&#x20;   .dropDuplicates(\["item\_id"])

&#x20;   .withColumn("quantity", F.coalesce(F.col("quantity").cast("int"), F.lit(1)))

&#x20;   .withColumn("unit\_price", F.col("unit\_price").cast("decimal(10,2)")))

write(items, "order\_items")



\# ---------- CUSTOMERS ----------

cust = (latest(read("customers"), "customer\_id")

&#x20;   .dropDuplicates(\["customer\_id"])

&#x20;   .withColumn("email", F.lower(F.trim("email")))

&#x20;   .fillna({"state": "UNKNOWN", "city": "UNKNOWN"}))

write(cust, "customers")



\# ---------- PRODUCTS ----------

prod = (latest(read("products"), "product\_id")

&#x20;   .dropDuplicates(\["product\_id"])

&#x20;   .withColumn("price", F.col("price").cast("decimal(10,2)"))

&#x20;   .fillna({"category": "UNCATEGORIZED"}))

write(prod, "products")



\# ---------- PAYMENTS ----------

pay = (latest(read("payments"), "payment\_id")

&#x20;   .dropDuplicates(\["payment\_id"])

&#x20;   .withColumn("paid\_at", F.to\_timestamp("paid\_at"))

&#x20;   .withColumn("amount", F.col("amount").cast("decimal(12,2)"))

&#x20;   .withColumn("is\_success", (F.col("status") == "SUCCESS").cast("int")))

write(pay, "payments")



\# ---------- INVENTORY ----------

inv = (latest(read("inventory"), "product\_id")

&#x20;   .withColumn("stock\_qty", F.coalesce(F.col("stock\_qty").cast("int"), F.lit(0))))

write(inv, "inventory")



job.commit()



\--------------------------------------------------------------------------------------------------------------------



21\. Click the Job details tab and set:



&#x20;Name	        : etl-raw-to-processed

IAM Role	: ecom-glue-role

Type	        : Spark

Glue version	: Glue 4.0 (or 5.0)

Language	: Python 3

Worker type	: G.1X

Requested number of workers :	2

Job bookmark	: Disable

Number of retries : 	0

Job timeout	: 30 (minutes)



Expand Advanced properties, then scroll to the Job parameters

Key: --PROCESSED\_PATH 

Value: s3://ecom-processed-tejes/cleaned



Open the Runs tab. The status goes Starting → Running → Succeeded





22.Crawler for the processed zone



&#x20;Crawlers → Create crawler. Name: crawler-processed.

Data source: S3, path s3://ecom-processed-tejes/cleaned/.

IAM role: ecom-glue-role. Target database: ecom\_processed

Create, then Run



\--------------------------------------------------------------------------------------------------------------------



23.Glue job 2 :: processed → curated



ETL jobs → Script editor → Spark → Start fresh → Create script.

&#x20;--------------------------------------------------------------------------------------------------------------------



import sys

from awsglue.utils import getResolvedOptions

from awsglue.context import GlueContext

from awsglue.job import Job

from pyspark.context import SparkContext

from pyspark.sql import functions as F



args = getResolvedOptions(sys.argv, \["JOB\_NAME", "CURATED\_PATH"])

sc = SparkContext()

glue = GlueContext(sc)

job = Job(glue)

job.init(args\["JOB\_NAME"], args)

C = args\["CURATED\_PATH"].rstrip("/")



def rd(table):

&#x20;   df = glue.create\_dynamic\_frame.from\_catalog(

&#x20;       database="ecom\_processed", table\_name=table).toDF()

&#x20;   return df.toDF(\*\[c.lower() for c in df.columns])



orders = rd("orders")

items  = rd("order\_items")

cust   = rd("customers")

prod   = rd("products")



\# ---------- curated/sales : one row per order line ----------

sales = (items

&#x20;   .join(orders.select("order\_id", "customer\_id", "order\_date", "status",

&#x20;                       "order\_year", "order\_month"), "order\_id")

&#x20;   .join(prod.select("product\_id", F.col("name").alias("product\_name"), "category"), "product\_id")

&#x20;   .join(cust.select("customer\_id", "state", "city"), "customer\_id")

&#x20;   .withColumn("line\_total", (F.col("quantity") \* F.col("unit\_price")).cast("decimal(12,2)"))

&#x20;   .select("item\_id", "order\_id", "customer\_id", "product\_id", "product\_name", "category",

&#x20;           "state", "city", "quantity", "unit\_price", "line\_total",

&#x20;           "order\_date", "status", "order\_year", "order\_month"))

sales.write.mode("overwrite").partitionBy("order\_year", "order\_month").parquet(f"{C}/sales/")

print("sales rows:", sales.count())



\# ---------- curated/customers : customer lifetime metrics ----------

cm = (orders.filter(F.col("status") != "CANCELLED")

&#x20;     .groupBy("customer\_id")

&#x20;     .agg(F.count("order\_id").alias("total\_orders"),

&#x20;          F.sum("total\_amount").alias("lifetime\_value"),

&#x20;          F.max("order\_date").alias("last\_order\_date")))

cust\_out = (cust.join(cm, "customer\_id", "left")

&#x20;   .fillna({"total\_orders": 0})

&#x20;   .withColumn("lifetime\_value", F.coalesce(F.col("lifetime\_value"), F.lit(0).cast("decimal(22,2)"))))

cust\_out.write.mode("overwrite").parquet(f"{C}/customers/")

print("customers rows:", cust\_out.count())



\# ---------- curated/products : product performance ----------

pm = (items.groupBy("product\_id")

&#x20;     .agg(F.sum("quantity").alias("units\_sold"),

&#x20;          F.sum(F.col("quantity") \* F.col("unit\_price")).cast("decimal(22,2)").alias("revenue")))

prod\_out = (prod.join(pm, "product\_id", "left")

&#x20;   .fillna({"units\_sold": 0})

&#x20;   .withColumn("revenue", F.coalesce(F.col("revenue"), F.lit(0).cast("decimal(22,2)"))))

prod\_out.write.mode("overwrite").parquet(f"{C}/products/")

print("products rows:", prod\_out.count())



job.commit()



\--------------------------------------------------------------------------------------------------------------------



24\. Same as job 1, except:



Field	                  : Value

Name	                 : etl-processed-to-curated

Job parameter key	 : --CURATED\_PATH

Job parameter value	 : s3://ecom-curated-tejes





25\. Crawler for the curated zone

Crawlers → Create crawler. Name: crawler-curated.

Data source: S3, path s3://ecom-curated-<ACCOUNT\_ID>/.

IAM role: ecom-glue-role. Target database: ecom\_curated





26\. Query with Athena : Create the workgroup



&#x20;Workgroups → Create workgroup.

Name: ecom-wg. Engine: Athena SQL.

Query result configuration: Location s3://ecom-athena-results-tejes/. Tick Encrypt query results → SSE-KMS → key ecom-datalake-key.



27\. Run queries



Open Query editor.  → choose workgroup ecom-wg. If it asks for a results location, use the bucket above.

Set Data source  → AwsDataCatalog and Database → ecom\_curated.



\-- 1. Sample of the joined table

SELECT \* FROM ecom\_curated.sales LIMIT 10;



\-- 2. Monthly revenue (excluding cancelled)

SELECT order\_year, order\_month, SUM(line\_total) AS revenue

FROM ecom\_curated.sales

WHERE status <> 'CANCELLED'

GROUP BY 1, 2 ORDER BY 1, 2;



\-- 3. Top products

SELECT product\_name, SUM(quantity) AS units, SUM(line\_total) AS revenue

FROM ecom\_curated.sales

GROUP BY 1 ORDER BY revenue DESC LIMIT 10;



\-- 4. Payment success rate

SELECT ROUND(100.0 \* SUM(is\_success) / COUNT(\*), 2) AS success\_pct

FROM ecom\_processed.payments;



\-- 5. State-wise sales

SELECT state, SUM(line\_total) AS revenue

FROM ecom\_curated.sales GROUP BY 1 ORDER BY 2 DESC;





\------------------------------------------------------------------------------------------------------------------------------------------------------------



OPTIONAL FOR REDSHIFT NOT REQUIRED IF U ARE LOOKING OUT FOR COST OPTIMIZATION. REDSHIFT WORKS SAME AS ATHENA ,BUT REDSHIFT IS USED FOR HUGE DATASETS STORED IN DATA WAREHOUSE 





28.Create it :: 

\-- Search Amazon Redshift → Redshift Serverless → Create workgroup (or "Get started" and choose Customize settings).

\-- Workgroup name: ecom-wg-rs. Base capacity: the lowest available (4 or 8 RPUs). Under max capacity, set a limit of 32 RPUs.

\-- Network: VPC ecom-vpc, the two private subnets, and a security group (create sg-redshift first with no inbound rules for now). Turn Publicly accessible off.

\-- Namespace: create new, name ecom-ns, database dev. Under Permissions, Manage IAM roles → Associate IAM roles → ecom-redshift-role.

\-- Encryption: use ecom-datalake-key.

\-- Create. Wait for Available 

\-- In Usage limits, add a limit of about 20 RPU-hours per day with action Turn off user queries, as a cost guard.



29.Create the schema (Query editor v2) :

&#x20;-- Open Query editor v2, connect to ecom-wg-rs with Federated user (or a database user).



\------------------------------------------------------------------------------------------------------------------------------------------------------------



\-- Run each block:



CREATE SCHEMA IF NOT EXISTS dw;



CREATE TABLE dw.dim\_customer (

&#x20; customer\_id INT, name VARCHAR(100), email VARCHAR(150),

&#x20; state VARCHAR(50), city VARCHAR(50),

&#x20; total\_orders INT, lifetime\_value DECIMAL(22,2)

) DISTSTYLE ALL;



CREATE TABLE dw.dim\_product (

&#x20; product\_id INT, name VARCHAR(150), category VARCHAR(50), price DECIMAL(10,2),

&#x20; units\_sold BIGINT, revenue DECIMAL(22,2)

) DISTSTYLE ALL;



CREATE TABLE dw.dim\_location (

&#x20; location\_id INT IDENTITY(1,1), state VARCHAR(50), city VARCHAR(50)

) DISTSTYLE ALL;



CREATE TABLE dw.dim\_date (

&#x20; date\_id INT, full\_date DATE, year SMALLINT, quarter SMALLINT, month SMALLINT,

&#x20; month\_name VARCHAR(12), day SMALLINT, day\_of\_week VARCHAR(10), is\_weekend BOOLEAN

) DISTSTYLE ALL;



CREATE TABLE dw.fact\_orders (

&#x20; order\_id INT, customer\_id INT, date\_id INT, status VARCHAR(20),

&#x20; total\_amount DECIMAL(12,2)

) DISTKEY(customer\_id) SORTKEY(date\_id);



CREATE TABLE dw.fact\_sales (

&#x20; item\_id INT, order\_id INT, customer\_id INT, product\_id INT, date\_id INT,

&#x20; quantity INT, unit\_price DECIMAL(10,2), line\_total DECIMAL(12,2)

) DISTKEY(product\_id) SORTKEY(date\_id);



CREATE TABLE dw.fact\_payments (

&#x20; payment\_id INT, order\_id INT, date\_id INT, method VARCHAR(30),

&#x20; status VARCHAR(20), is\_success SMALLINT, amount DECIMAL(12,2)

) SORTKEY(date\_id);





INSERT INTO dw.dim\_date

WITH RECURSIVE dates(d) AS (

&#x20; SELECT '2020-01-01'::date

&#x20; UNION ALL SELECT (d + 1)::date FROM dates WHERE d < '2030-12-31'::date)

SELECT CAST(TO\_CHAR(d,'YYYYMMDD') AS INT), d, EXTRACT(year FROM d),

&#x20;      EXTRACT(quarter FROM d), EXTRACT(month FROM d), TO\_CHAR(d,'Mon'),

&#x20;      EXTRACT(day FROM d), TO\_CHAR(d,'Dy'),

&#x20;      CASE WHEN EXTRACT(dow FROM d) IN (0,6) THEN TRUE ELSE FALSE END

FROM dates;





SELECT d.year, d.month\_name, SUM(f.line\_total) AS revenue

FROM dw.fact\_sales f JOIN dw.dim\_date d ON f.date\_id = d.date\_id

GROUP BY 1, 2 ORDER BY 1, MIN(d.month);



SELECT p.name, SUM(f.line\_total) AS revenue

FROM dw.fact\_sales f JOIN dw.dim\_product p ON f.product\_id = p.product\_id

GROUP BY 1 ORDER BY 2 DESC;



SELECT c.state, SUM(f.line\_total) AS revenue

FROM dw.fact\_sales f JOIN dw.dim\_customer c ON f.customer\_id = c.customer\_id

GROUP BY 1 ORDER BY 2 DESC;



\-----------------------------------------------------------------------------------------------------------



TO TEST : IN EC2 INSTANCE MAKING SOME CHANGES IN QUERY LIKE ADDING SOME TABLES AND ALL HERE WHEN U WRITE A QUERY TO SEARCH FOR THAT TABLE DATA IN QUERY EDITOR IT SHOULD BE VISIBLE CLEARLY .

































































































&#x20;



&#x20;                                                                                                           

























































&#x20;  

&#x20;     













































