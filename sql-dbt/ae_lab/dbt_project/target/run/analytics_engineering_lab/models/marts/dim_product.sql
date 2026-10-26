
    

    create  table
      "analytics"."main"."dim_product__dbt_tmp"
  
    
    as (
      select product_id, product_name, category_id, category_name, department, unit_price from "analytics"."main"."stg_products"
    );
    
  