frappe.listview_settings['Donation Data'] = {
    onload(listview) {
        listview.page.add_inner_button('Delete All', () => {
            frappe.confirm(
                'Are you sure you want to delete all records in Donation Data?',
                () => {
                    frappe.call({
                        method: 'di_report.api.delete_all_donation_data',
                        callback: function(r) {
                            if (r.message === "success") {
                                frappe.msgprint("All records deleted successfully.");
                                listview.refresh();
                            } else {
                                frappe.msgprint("Failed to delete records.");
                            }
                        }
                    });
                },
                () => {
                    frappe.msgprint("Operation cancelled.");
                }
            );
        });
            listview.page.add_inner_button('Import CSV', () => {
                const dialog = new frappe.ui.Dialog({
                    title: 'Import Donation Data via File ID',
                    fields: [
                        {
                            label: 'File ID',
                            fieldname: 'file_id',
                            fieldtype: 'Data',
                            description: 'Paste the name or ID of the File record (e.g., FILE-2024-00001)',
                            reqd: 1
                        }
                    ],
                    primary_action_label: 'Import',
                    primary_action(values) {
                        dialog.hide();
                        frappe.call({
                            method: "di_report.api.fast_import_donation_data",
                            args: {
                                file_id: values.file_id
                            },
                            freeze: true,
                            freeze_message: "Importing data, please wait...",
                            callback: function (r) {
                                frappe.msgprint(r.message || "Import Completed");
                                listview.refresh();
                            }
                        });
                }
            });
            dialog.show();
        });
    }
}


