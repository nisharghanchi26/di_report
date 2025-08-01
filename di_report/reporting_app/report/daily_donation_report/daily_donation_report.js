frappe.query_reports["Daily Donation Report"] = {
    onload: function(report) {
        // Load Mode options
        frappe.call({
            method: "di_report.reporting_app.report.daily_donation_report.daily_donation_report.get_mode_options",
            callback: function(r) {
                if (r.message) {
                    let filter = report.get_filter('mode');
                    if (filter) {
                        filter.df.options = r.message;
                        filter.refresh();
                    }
                }
            }
        });

        // Load Deposit Status options
        frappe.call({
            method: "di_report.reporting_app.report.daily_donation_report.daily_donation_report.get_deposit_status_options",
            callback: function(r) {
                if (r.message) {
                    let filter = report.get_filter('deposit_status');
                    if (filter) {
                        filter.df.options = r.message;
                        filter.refresh();
                    }
                }
            }
        });
    }
};
