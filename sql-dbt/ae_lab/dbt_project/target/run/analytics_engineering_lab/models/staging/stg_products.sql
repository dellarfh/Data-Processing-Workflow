
  
  create view "analytics"."main"."stg_products__dbt_tmp" as (
    select product_id, product_name, category_id, category_name, department, unit_price from "analytics"."raw"."products"
  );
