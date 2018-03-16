{
    "name": "DalSil Soft Package - Basic",
    "description": "Paket Module DalSil Basic",
    "version": "10.0.0.0.1",
    "author": "DalSil Soft",
    "license": "AGPL-3",
    "category": "DalSil",
    "depends": [
        "base", "product", "stock", "sale", "account", "ss_common", "account_accountant",
        "account_financial_report_qweb", "purchase", "dalsil"
    ],
    "data": [
        'data/sequence.xml',
        'cron/cron_start_stock.xml',
        'cron/cron_expired_fee_sales.xml',

        'security/group_security.xml',

        'view/modified/res_partner.xml',
        'view/modified/account_invoice.xml',
        'view/modified/product_template.xml',
        'view/modified/payment_term.xml',

        'view/config/config.xml',
        'view/config/wiz_config.xml',

        'view/master/truck.xml',
        'view/fee_sales/fee_sales.xml',
        'view/fee_sales/gen_fee_sales.xml',
        'view/rent_truck/rent_truck.xml',
        'view/rent_truck/rent_truck_line.xml',
        'view/rent_truck/wiz_rent_truck.xml',
        'view/rent_truck/wiz_rent_truck_line_invoice.xml',
        'view/rent_truck/wiz_rent_truck_line_purchase.xml',
        'view/supplier_return/supplier_return.xml',
        'view/supplier_return/supplier_return_line.xml',
        'view/customer_return/customer_return.xml',
        'view/customer_return/customer_return_line.xml',
        'view/start_stock/start_stock.xml',
        'view/start_stock/start_stock_line.xml',

        'view/check_giro/in_check_giro.xml',
        'view/check_giro/in_check_giro_line.xml',
        'view/check_giro/out_check_giro.xml',
        'view/check_giro/out_check_giro_line.xml',
        'view/cash_bank/other_deposit.xml',
        'view/cash_bank/other_deposit_line.xml',
        'view/cash_bank/other_payment.xml',
        'view/cash_bank/other_payment_line.xml',
        'view/journal_voucher/journal_voucher.xml',
        'view/journal_voucher/journal_voucher_line.xml',

        'view/gen_payment_invoice/gen_payment_invoice.xml',

        'view/report/report_stock.xml',
        'view/report/report_summary_stock.xml',
        'view/report/account_invoice.xml',
        'view/report/report_invoice.xml',

        'view/menu.xml',

        'security/ir.model.access.csv',
    ],
}
