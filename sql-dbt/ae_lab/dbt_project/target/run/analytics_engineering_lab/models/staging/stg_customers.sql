
  
  create view "analytics"."main"."stg_customers__dbt_tmp" as (
    select customer_id, customer_name, segment, region from "analytics"."raw"."customers"
  );
