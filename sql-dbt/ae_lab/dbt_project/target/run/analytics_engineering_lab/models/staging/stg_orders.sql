
  
  create view "analytics"."main"."stg_orders__dbt_tmp" as (
    select order_id, customer_id, product_id, cast(order_date as date) as order_date, quantity, unit_price from "analytics"."raw"."orders"
  );
