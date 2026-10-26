
    

    create  table
      "analytics"."main"."sales_mart__dbt_tmp"
  
    
    as (
      select d.year, d.month, c.segment, c.region, p.category_name as category, sum(f.sales_amount) as total_sales, sum(f.quantity) as total_quantity from "analytics"."main"."fct_sales" f join "analytics"."main"."dim_customer" c on f.customer_id=c.customer_id join "analytics"."main"."dim_product" p on f.product_id=p.product_id join "analytics"."main"."dim_date" d on f.order_date=d.full_date group by 1,2,3,4,5
    );
    
  