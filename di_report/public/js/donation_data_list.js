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
    }
}
