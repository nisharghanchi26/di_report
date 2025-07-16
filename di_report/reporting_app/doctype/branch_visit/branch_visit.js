// Copyright (c) 2025, Nisar and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Branch Visit", {
// 	refresh(frm) {

// 	},
// });



frappe.ui.form.on('Branch Visit', {
    onload: function(frm) {
        
        
if (frm.is_new() && !frm.doc.checklist_points?.length) {
    frappe.model.with_doctype('Visit Checklist', () => {
        const point_field = frappe.meta.get_docfield('Visit Checklist', 'point');
        
        if (point_field?.options) {
            const checklist_points = point_field.options
                .split('\n')
                .map(opt => opt.trim())
                .filter(opt => opt);
            
            // Clear any existing rows first (optional)
            frm.clear_table('checklist_points');
            
            checklist_points.forEach(point => {
                let child = frm.add_child('checklist_points', { point: point });
                // Refresh each row if needed
                frappe.model.set_value(child.doctype, child.name, 'point', point);
            });
            
            frm.refresh_field('checklist_points');
        }
    });
}
        
        // Set Visit Date to today's date if not already set
        if (!frm.doc.visit_date) {
            frm.set_value('visit_date', frappe.datetime.get_today());
        }
        if (frm.is_new()) {
            frm.set_df_property('section_break_uobz', 'hidden', 1);
        }

        // Set Created By from session user if not already set
        if (!frm.doc.created_by && frappe.session.user !== 'Guest') {
            frm.set_value('created_by', frappe.session.user);
        }
    },
refresh: function(frm) {
        // Show section only if the document is saved
        if (!frm.is_new()) {
            frm.set_df_property('section_break_uobz', 'hidden', 0);
        } else {
            frm.set_df_property('section_break_uobz', 'hidden', 1);
        }

        // if (frm.doc.status !== 'Saved') {
        //     frm.set_df_property('checklist_points', 'cannot_delete_rows', true);
        //     frm.set_df_property('checklist_points', 'cannot_delete_all_rows', true);

        //     frm.set_df_property('response_details', 'cannot_delete_rows', true);
        //     frm.set_df_property('response_details', 'cannot_delete_all_rows', true);
        // }
       if (frm.doc.checklist_points?.length && frm.doc.response_details?.length === 0  && frm.doc.workflow_state !== 'Saved') {
        frm.doc.checklist_points.forEach(row => {
            frm.add_child('response_details', {
                checklist_points: row.name,  // or row.point depending on your field structure
                point: row.point  // make sure this matches your actual field name
            });
        });
        frm.refresh_field('response_details');
    } 
    },
        before_save: function(frm) {
        // Check if visit_checklist child table has at least one row
        if (!frm.doc.checklist_points || frm.doc.checklist_points.length === 0) {
            frappe.throw(__("Please add at least one item in the Visit Checklist table before saving."));
        }
    },
   
});

