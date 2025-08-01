import frappe
from frappe import _

@frappe.whitelist()
def delete_all_donation_data():
    try:
        frappe.db.sql("DELETE FROM `tabDonation Data`")
        frappe.db.commit()
        return "success"
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delete All Donation Data Error")
        return "error"
