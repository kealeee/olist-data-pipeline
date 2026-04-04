
      
        
        
        delete from "olist_dw"."analytics"."fact_sales" as DBT_INTERNAL_DEST
        where (order_id) in (
            select distinct order_id
            from "fact_sales__dbt_tmp223640072531" as DBT_INTERNAL_SOURCE
        );

    

    insert into "olist_dw"."analytics"."fact_sales" ("order_id", "order_item_id", "product_id", "seller_id", "customer_id", "purchased_at", "price", "freight_value", "total_sale_amount")
    (
        select "order_id", "order_item_id", "product_id", "seller_id", "customer_id", "purchased_at", "price", "freight_value", "total_sale_amount"
        from "fact_sales__dbt_tmp223640072531"
    )
  