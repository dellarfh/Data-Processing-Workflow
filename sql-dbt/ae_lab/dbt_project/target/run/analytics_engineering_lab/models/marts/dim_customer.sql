
    

    create  table
      "analytics"."main"."dim_customer__dbt_tmp"
  
    
    as (
      select customer_id, customer_name, segment, region from "analytics"."main"."stg_customers"
    );
    
  