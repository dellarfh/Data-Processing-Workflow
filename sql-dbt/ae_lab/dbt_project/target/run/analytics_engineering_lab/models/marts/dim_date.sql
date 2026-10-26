
    

    create  table
      "analytics"."main"."dim_date__dbt_tmp"
  
    
    as (
      select distinct order_date as full_date, extract(year from order_date) as year, extract(month from order_date) as month, extract(quarter from order_date) as quarter from "analytics"."main"."stg_orders"
    );
    
  