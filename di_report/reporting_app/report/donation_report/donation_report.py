# Copyright (c) 2025, Nisar and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt
import pymysql

def get_descendant_locations(location_name):
    descendants = [location_name]

    children = frappe.get_all('Location', filters={'parent_location': location_name}, pluck='name')
    for child in children:
        descendants.extend(get_descendant_locations(child))

    return descendants


def execute(filters=None):
    user = frappe.session.user
    user_roles = frappe.get_roles(user)
    lcs = frappe.get_all('User Permission', filters={'user': user, 'allow': 'Location'})
    dpt = frappe.get_all('User Permission', filters={'user': user, 'allow': 'Org Department'})
    #frappe.msgprint(", ".join(user_roles))
    if 'System Manager' not in user_roles and (len(lcs) == 0 and len(dpt) == 0):
        frappe.throw("You have no access to report")
    columns = get_columns(filters)
    data = get_data(filters)
#    page_length = frappe.form_dict.get("limit",100)
#    start = frappe.form_dict.get("state",0)
#    paged_data = data[start:start+page_length]
    chart = None
    if filters.get("report_type") == "Group Report":
        chart = get_chart(data)
#    return columns, paged_data, None, chart
    return columns, data, None, chart

def get_columns(filters):
    group_by = filters.get("group_by")
    if filters.get("report_type") == "Donation Summary":
        return [
          {"label": "Location", "fieldname": "location", "fieldtype": "Link", "options": "Location", "width": 250},
          {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 110},
          {"label": "Status", "fieldname": "deposit_status", "fieldtype": "Data", "width": 110},
          {"label": "User", "fieldname": "user", "fieldtype": "Data", "width": 250},  
          {"label": "Mobile", "fieldname": "user_mobile", "fieldtype": "Data", "width": 110},
          {"label": "Mode", "fieldname": "mode", "fieldtype": "Data", "width": 150},
          {"label": "Main Type", "fieldname": "main_type", "fieldtype": "Data", "width": 120},
          {"label": "Sub Type", "fieldname": "sub_type", "fieldtype": "Data", "width": 120},
          {"label": "Purpose", "fieldname": "purpose", "fieldtype": "Data", "width": 200},
          {"label": "Department", "fieldname": "department", "fieldtype": "Link", "options": "Org Department", "width": 200},
          {"label": "Area", "fieldname": "area", "fieldtype": "Data", "width": 200},
          {"label": "Branch", "fieldname": "branch", "fieldtype": "Data", "width": 300},
          {"label": "User Gender", "fieldname": "user_gender", "fieldtype": "Data", "width": 100},
          {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 150}
        ]
    elif filters.get("report_type") == "Undeposit Report":
        return [
          {"label": "Location", "fieldname": "location", "fieldtype": "Link", "options": "Location", "width": 250},
          {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 110},
          {"label": "Receipt#", "fieldname": "receipt_no", "fieldtype": "Data", "width": 110},
          {"label": "User", "fieldname": "user", "fieldtype": "Data", "width": 250},  
          {"label": "Mobile", "fieldname": "user_mobile", "fieldtype": "Data", "width": 110},
          {"label": "Emp Code", "fieldname": "emp_code", "fieldtype": "Data", "width": 110},
          {"label": "Mode", "fieldname": "mode", "fieldtype": "Data", "width": 150},
          {"label": "Main Type", "fieldname": "main_type", "fieldtype": "Data", "width": 120},
          {"label": "Sub Type", "fieldname": "sub_type", "fieldtype": "Data", "width": 120},
          {"label": "Purpose", "fieldname": "purpose", "fieldtype": "Data", "width": 200},
          {"label": "Department", "fieldname": "department", "fieldtype": "Link", "options": "Org Department", "width": 200},
          {"label": "Area", "fieldname": "area", "fieldtype": "Data", "width": 200},
          {"label": "Branch", "fieldname": "branch", "fieldtype": "Data", "width": 300},
          {"label": "User Gender", "fieldname": "user_gender", "fieldtype": "Data", "width": 100},
          {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 150}
        ]
    elif filters.get("report_type") == "User Report":
        return [
          {"label": "Location", "fieldname": "location", "fieldtype": "Link", "options": "Location", "width": 250},
          {"label": "User", "fieldname": "user", "fieldtype": "Data", "width": 250},  
          {"label": "Mobile", "fieldname": "user_mobile", "fieldtype": "Data", "width": 110},
          {"label": "Deposited", "fieldname": "deposited", "fieldtype": "Currency", "width": 100},
          {"label": "Undeposit", "fieldname": "undeposit", "fieldtype": "Currency", "width": 100},
          {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 150}
        ]
    elif filters.get("report_type") == "Group Report":
        if group_by == "Location":
            return[
                {"label": "Location", "fieldname": "details", "fieldtype": "Link", "options": "Location", "width": 250},
                {"label": "Deposited", "fieldname": "deposited", "fieldtype": "Currency", "width": 100},
                {"label": "Undeposit", "fieldname": "undeposit", "fieldtype": "Currency", "width": 100},
                {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 150}
            ]
        elif group_by == "Department":
            return[
                {"label": "Department", "fieldname": "details", "fieldtype": "Link", "options": "Org Department", "width": 250},
                {"label": "Deposited", "fieldname": "deposited", "fieldtype": "Currency", "width": 100},
                {"label": "Undeposit", "fieldname": "undeposit", "fieldtype": "Currency", "width": 100},
                {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 150}
            ]
        else:
            return[
                {"label": group_by.capitalize().replace("_"," "), "fieldname": "details", "fieldtype": "Data", "width": 300},
                {"label": "Deposited", "fieldname": "deposited", "fieldtype": "Currency", "width": 100},
                {"label": "Undeposit", "fieldname": "undeposit", "fieldtype": "Currency", "width": 100},
                {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 150}
            ]
    else:
        return[]

def get_data(filters):
    conditions = []
    conn = pymysql.connect(
        host="172.237.36.137",
        user="root",
        password="f5c46a0cd29b8617",
        database="finance"
    )
    where_clause = ""
    params = []
    user = frappe.session.user
    
    allowed_departments = frappe.get_all("User Permission", 
        filters={"user": user, "allow": "Org Department"}, 
        pluck="for_value"
    )

    allowed_locations = frappe.get_all("User Permission", 
        filters={"user": user, "allow": "Location"}, 
        pluck="for_value"
    )
    expanded_allowed_locations = []
    for loc in allowed_locations:
        expanded_allowed_locations.extend(get_descendant_locations(loc))
    expanded_allowed_locations = list(set(expanded_allowed_locations))  # remove duplicates

    if allowed_departments:
        placeholders = ", ".join(["%s"] * len(allowed_departments))
        conditions.append(f"department IN ({placeholders})")
        params.extend(allowed_departments)

    if filters.get("location"):
        selected_locations = get_descendant_locations(filters["location"])
    else:
        selected_locations = []
    
    if filters.get("location"):
        if expanded_allowed_locations:
            filtered_locations = list(set(selected_locations) & set(expanded_allowed_locations))
        else:
            filtered_locations = selected_locations
    else:
        filtered_locations = expanded_allowed_locations
    
    if filtered_locations:
        placeholders = ", ".join(["%s"] * len(filtered_locations))
        conditions.append(f"location IN ({placeholders})")
        params.extend(filtered_locations)
    
    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("date BETWEEN %s AND %s")
        params += [filters["from_date"], filters["to_date"]]

    # if filters.get("location"):
    #     # conditions.append("location = %s")
    #     # params.append(filters["location"])
    #     locations = get_descendant_locations(filters["location"])
    #     conditions.append(f"location IN ({', '.join(['%s'] * len(locations))})")
    #     params.extend(locations)

    if filters.get("mode"):
        conditions.append("mode = %s")
        params.append(filters["mode"])
    
    if filters.get("main_type"):
        conditions.append("main_type = %s")
        params.append(filters["main_type"])

    if filters.get("sub_type"):
        conditions.append("sub_type = %s")
        params.append(filters["sub_type"])

    if filters.get("purpose"):
        conditions.append("purpose = %s")
        params.append(filters["purpose"])

    if filters.get("department"):
        conditions.append("department = %s")
        params.append(filters["department"])

    if filters.get("deposit_status"):
        conditions.append("deposit_status = %s")
        params.append(filters["deposit_status"])

    if filters.get("type"):
        conditions.append("type = %s")
        params.append(filters["type"])

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    if filters.get("report_type") == "Undeposit Report":
        where_clause += "AND deposit_status='Un-Deposit'"
    group_by = filters.get("group_by")
    
    if filters.get("report_type") == "Donation Summary":
        query = f"""
        SELECT location, date, deposit_status, user,user_mobile,mode,main_type,sub_type,purpose,department,area,branch,user_gender, SUM(amount) as `amount`
        FROM forErpReport
        {where_clause}
        GROUP BY location, date,deposit_status, user,user_mobile,mode,main_type,sub_type,purpose,department,area,branch,user_gender HAVING SUM(amount)>0
        ORDER BY date DESC
        """
    if filters.get("report_type") == "Undeposit Report":
        query = f"""
        SELECT location, date, receipt_no, user,user_mobile,emp_code,mode,main_type,sub_type,purpose,department,area,branch,user_gender, amount
        FROM forErpReport
        {where_clause}
        ORDER BY date ASC
        """
    if filters.get("report_type") == "User Report":
        query = f"""
        SELECT location,user,user_mobile, SUM(CASE WHEN deposit_status='Deposit' THEN amount END) AS `deposited`, SUM(CASE WHEN deposit_status='Un-Deposit' THEN amount END) AS `undeposit`,SUM(amount) as `amount`
        FROM forErpReport
        {where_clause}
        GROUP BY location,user,user_mobile
        """
    if filters.get("report_type") == "Group Report":
        query = f"""
        SELECT {group_by} as `details`, SUM(CASE WHEN deposit_status='Deposit' THEN amount END) AS `deposited`, SUM(CASE WHEN deposit_status='Un-Deposit' THEN amount END) AS `undeposit`,SUM(amount) as `amount`
        FROM forErpReport
        {where_clause}
        GROUP BY `{group_by}`
        ORDER BY SUM(amount) DESC
        """

    with conn.cursor() as cursor:
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()

    conn.close()

    result = []
    if filters.get("report_type") == "Donation Summary":
        for row in rows:
            result.append({
                "location": row[0],
                "date": row[1],
                "deposit_status": row[2],
                "user": row[3],
                "user_mobile": row[4],
                "mode": row[5],
                "main_type": row[6],
                "sub_type": row[7],
                "purpose": row[8],
                "department": row[9],
                "area": row[10],
                "branch": row[11],
                "user_gender": row[12],
                "amount": row[13]
            })
    if filters.get("report_type") == "Undeposit Report":
        for row in rows:
            result.append({
                "location": row[0],
                "date": row[1],
                "receipt_no": row[2],
                "user": row[3],
                "user_mobile": row[4],
                "emp_code": row[5],
                "mode": row[6],
                "main_type": row[7],
                "sub_type": row[8],
                "purpose": row[9],
                "department": row[10],
                "area": row[11],
                "branch": row[12],
                "user_gender": row[13],
                "amount": row[14]
            })

    if filters.get("report_type") == "User Report":
        for row in rows:
            result.append({
                "location": row[0],
                "user": row[1],
                "user_mobile": row[2],
                "deposited": row[3],
                "undeposit": row[4],
                "amount": row[5]
            })
    if filters.get("report_type") == "Group Report":
        for row in rows:
            result.append({
                "details": row[0],
                "deposited": row[1],
                "undeposit": row[2],
                "amount": row[3]
            })
    return result

def get_chart(data):
    labels = [row["details"] for row in data]
    values = [row["amount"] for row in data]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Amount",
                    "values": values
                }
            ]
        },
        "type": "bar"  # You can change this to "pie", "line", etc.
    }



@frappe.whitelist()
def get_filter_options():
    conn = pymysql.connect(
        host="172.237.36.137",
        user="root",
        password="f5c46a0cd29b8617",
        database="finance"
    )

    with conn.cursor() as cursor:
        def get_distinct(field):
            cursor.execute(f"SELECT DISTINCT {field} FROM forErpReport WHERE {field} IS NOT NULL AND {field} != ''")
            return [row[0] for row in cursor.fetchall()]

        result = {
            "deposit_status": get_distinct("deposit_status"),
            "mode": get_distinct("mode"),
            "main_type": get_distinct("main_type"),
            "sub_type": get_distinct("sub_type"),
            "purpose": get_distinct("purpose")
        }

    conn.close()
    return result

