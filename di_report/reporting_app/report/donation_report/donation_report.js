// Copyright (c) 2025, Nisar and contributors
// For license information, please see license.txt

// frappe.query_reports["Donation Report"] = {
// 	"filters": [

// 	]
// };
frappe.query_reports["Donation Report"] = {
  "filters":[
    {
      fieldname: "report_type",
      label: __("Report Type"),
      fieldtype: "Select",
      options: ["","Donation Summary","User Report","Group Report","Undeposit Report"],
      default: "",
      reqd: 1,
      on_change: function() {
                // Call function on filter change
                let report = frappe.query_report;
                frappe.query_reports["Donation Report"].toggleMenuButtonGroup(report);
            }
    },
    {
      fieldname: "type",
      label: __("Type"),
      fieldtype: "Select",
      options: ["","Eraseed","DM"],
      default: "",
      reqd: 1,
    },
    {
      fieldname: "group_by",
      label: __("Group By"),
      fieldtype: "Select",
      options: ["","Location","Region","State","Department","Area","Date","Mode","Purpose","main_type","sub_type"],
      default: "Location",
      reqd: 0,
      depends_on: 'eval:doc.report_type == "Group Report"',
    },
    {
      fieldname: "location",
      label: __("Location"),
      fieldtype: "Link",
      options: "Location",
      default: "",
      reqd: 0,
    },
    {
      fieldname: "deposit_status",
      label: __("Deposit Status"),
      fieldtype: "Select",
      options: "",
      default: "",
      reqd: 0,
    },
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      reqd: 0,
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      reqd: 0,
    },
        {
      fieldname: "department",
      label: __("Department"),
      fieldtype: "Link",
      options: "Org Department",
      default: "",
      reqd: 0,
    },
    {
      fieldname: "mode",
      label: __("Mode"),
      fieldtype: "Select",
      options: "",
      default: "",
      reqd: 0,
    },
    {
      fieldname: "main_type",
      label: __("Main Type"),
      fieldtype: "Select",
      options: "",
      default: "",
      reqd: 0,
    },
    {
      fieldname: "sub_type",
      label: __("Sub Type"),
      fieldtype: "Select",
      options: "",
      default: "",
      reqd: 0,
    },
    {
      fieldname: "purpose",
      label: __("Purpose"),
      fieldtype: "Select",
      options: "",
      default: "",
      reqd: 0,
    },
  ],
  onload: function(report) {
    report.page.page_form.find('[data-label="Actions"]').hide();
    //report.page.menu_btn_group.hide();
    this.toggleMenuButtonGroup(report);
    report.page.add_inner_button('Reset Filters', function() {
        // Clear all filters
        report.filters.forEach(filter => {
            filter.set_value('');
        });
        // Optionally refresh the report after clearing
        report.refresh();
    });
    frappe.call({
      method: "di_report.reporting_app.report.donation_report.donation_report.get_filter_options",
      callback: function(r) {
        if (!r.message) return;

        const { deposit_status, mode, department, main_type, sub_type, purpose } = r.message;

        const updateFilter = (fieldname, options) => {
          const filter = report.get_filter(fieldname);
          if (filter && options.length) {
            //filter.df.options = options.join("\n");
            filter.df.options = ["", ...options].join("\n");
            filter.refresh();
          }
        };

        updateFilter("deposit_status", deposit_status);
        updateFilter("mode", mode);
        updateFilter("main_type", main_type);
        updateFilter("sub_type", sub_type);
        updateFilter("purpose", purpose);
      }
    });
  },
    refresh: function(report) {
        this.toggleMenuButtonGroup(report);
        report.page.page_form.find('[data-label="Actions"]').hide();
    },
    toggleMenuButtonGroup: function(report) {
    let report_type = frappe.query_report.get_filter_value("report_type");

    setTimeout(function() {
        let menu_group = report.page.menu_btn_group;

        if (report_type === "Undeposit Report") {
            // Show the menu group
            menu_group.show();

            // Hide all menu items
            menu_group.find("li").hide();

            // Show only the Export option
            menu_group.find('a:contains("Export")').parent().show();
        } else {
            menu_group.hide();
        }
    }, 0);
}
 };
