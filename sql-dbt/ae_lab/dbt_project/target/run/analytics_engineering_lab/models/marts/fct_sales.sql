
    

    create  table
      "analytics"."main"."fct_sales__dbt_tmp"
  
    
    as (
      select order_id, order_date, customer_id, product_id, quantity, unit_price, sales_amount from "analytics"."main"."int_sales"
    );
    
  