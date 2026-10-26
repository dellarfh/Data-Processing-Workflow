
  
  create view "analytics"."main"."int_sales__dbt_tmp" as (
    select order_id, order_date, customer_id, product_id, quantity, unit_price, quantity * unit_price as sales_amount from "analytics"."main"."stg_orders"
  );
