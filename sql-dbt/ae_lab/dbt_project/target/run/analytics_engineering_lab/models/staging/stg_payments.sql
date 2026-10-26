
  
  create view "analytics"."main"."stg_payments__dbt_tmp" as (
    select payment_id, order_id, payment_amount, payment_method, payment_status from "analytics"."raw"."payments"
  );
