# Copyright (c) 2025, Nisar and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Location", "fieldname": "location", "fieldtype": "Link", "options": "Location", "width": 120},
        {"label": "Deposit Status", "fieldname": "deposit_status", "fieldtype": "Data", "width": 120},
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 100},
        {"label": "User", "fieldname": "user", "fieldtype": "Data", "width": 120},
        {"label": "User Mobile", "fieldname": "user_mobile", "fieldtype": "Data", "width": 120},
        {"label": "Mode", "fieldname": "mode", "fieldtype": "Data", "width": 100},
        {"label": "Main Type", "fieldname": "main_type", "fieldtype": "Data", "width": 100},
        {"label": "Sub Type", "fieldname": "sub_type", "fieldtype": "Data", "width": 100},
        {"label": "Purpose", "fieldname": "purpose", "fieldtype": "Data", "width": 100},
        {"label": "Department", "fieldname": "department", "fieldtype": "Data", "width": 100},
        {"label": "Area / District", "fieldname": "area_district", "fieldtype": "Data", "width": 120},
        {"label": "Branch C4", "fieldname": "branch_c4", "fieldtype": "Data", "width": 100},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 100},
        {"label": "User Gender", "fieldname": "user_gender", "fieldtype": "Data", "width": 100},
    ]

def get_data(filters):
    conditions = []
    if filters.get("location"):
        conditions.append(f"location = '{filters.location}'")
    if filters.get("deposit_status"):
        conditions.append(f"deposit_status = '{filters.deposit_status}'")
    if filters.get("mode"):
        conditions.append(f"mode = '{filters.mode}'")
    if filters.get("start_date"):
        conditions.append(f"date >= '{filters.start_date}'")
    if filters.get("end_date"):
        conditions.append(f"date <= '{filters.end_date}'")

    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = "WHERE " + where_clause

    data = frappe.db.sql(f"""
        SELECT 
            location, deposit_status, date, user, user_mobile,
            mode, main_type, sub_type, purpose, department,
            area_district, branch_c4, amount, user_gender
        FROM `tabDonation Data`
        {where_clause}
        ORDER BY date DESC
    """, as_dict=True)
    return data

@frappe.whitelist()
def get_mode_options():
    modes = frappe.db.sql_list("""
        SELECT DISTINCT mode 
        FROM `tabDonation Data`
        WHERE IFNULL(mode, '') != ''
        ORDER BY mode
    """)
    return [""] + modes

@frappe.whitelist()
def get_deposit_status_options():
    statuses = frappe.db.sql_list("""
        SELECT DISTINCT deposit_status
        FROM `tabDonation Data`
        WHERE IFNULL(deposit_status, '') != ''
        ORDER BY deposit_status
    """)
    return [""] + statuses