import frappe
from frappe import _
import csv
import io
from frappe.utils.file_manager import get_file

@frappe.whitelist()
def delete_all_donation_data():
    try:
        frappe.db.sql("DELETE FROM `tabDonation Data`")
        frappe.db.commit()
        return "success"
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delete All Donation Data Error")
        return "error"



# @frappe.whitelist()
# def import_csv_by_file_id(file_id):
#     try:
#         file_doc = frappe.get_doc("File", file_id)

#         # Get raw CSV content (already decoded to string in most recent Frappe versions)
#         content = file_doc.get_content()
#         if not content:
#             return "Error: No content found in file."

#         # Use content directly as string
#         text_stream = io.StringIO(content)

#         inserted = 0
#         reader = csv.DictReader(text_stream)
#         data = []

#         for row in reader:
#             doc = frappe.get_doc({
#                 "doctype": "Donation Data",
#                 **row
#             })
#             data.append(doc)

#             if len(data) >= 1000:
#                 _bulk_insert(data)
#                 inserted += len(data)
#                 data = []

#         if data:
#             _bulk_insert(data)
#             inserted += len(data)

#         return f"✅ Successfully imported {inserted} records from file {file_id}"

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Donation Data Import Error")
#         return f"❌ Error importing file: {str(e)}"


# def _bulk_insert(doc_list):
#     for doc in doc_list:
#         doc.insert(ignore_permissions=True, ignore_links=True, ignore_mandatory=True)
#     frappe.db.commit()


@frappe.whitelist()
def fast_import_donation_data(file_id):
    try:
        file_doc = frappe.get_doc("File", file_id)
        content = file_doc.get_content()

        if not content:
            return "❌ No content found in file."

        text_stream = io.StringIO(content)
        reader = csv.DictReader(text_stream)

        # Get actual column names from table
        table_fields = frappe.db.get_table_columns("Donation Data")

        insert_columns = []
        first_row = next(reader)
        for field in first_row:
            if field in table_fields:
                insert_columns.append(field)
        else:
            pass  # Not a match? Skip it.

        # Reset stream and start inserting
        text_stream.seek(0)
        reader = csv.DictReader(text_stream)

        batch_data = []
        total_inserted = 0
        for row in reader:
            values = [row.get(col) for col in insert_columns]
            batch_data.append(values)

            if len(batch_data) >= 1000:
                _execute_bulk_insert(insert_columns, batch_data)
                total_inserted += len(batch_data)
                batch_data = []

        if batch_data:
            _execute_bulk_insert(insert_columns, batch_data)
            total_inserted += len(batch_data)

        return f"✅ Fast imported {total_inserted} rows into Donation Data"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Fast Donation Import Error")
        return f"❌ Error: {str(e)}"


def _execute_bulk_insert(columns, data):
    if not data:
        return

    placeholders = ", ".join(["%s"] * len(columns))
    column_list = ", ".join(f"`{col}`" for col in columns)
    query = f"""
        INSERT INTO `tabDonation Data` ({column_list})
        VALUES ({placeholders})
    """

    for row in data:
        frappe.db.sql(query, row)

    frappe.db.commit()
