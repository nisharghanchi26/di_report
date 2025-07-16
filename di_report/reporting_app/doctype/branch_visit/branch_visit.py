# Copyright (c) 2025, Nisar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import nowdate
from frappe.utils import now


class BranchVisit(Document):
    def validate(self):
        for row in self.response_details:
            if row.is_new() and row.response:
                row.replied_by = frappe.session.user
                row.replied_by_name = frappe.utils.get_fullname(frappe.session.user)
                row.replay_date = now()
            elif row.name:
                old_response = frappe.db.get_value(row.doctype, row.name, 'response')
                if old_response != row.response:
                    row.replied_by = frappe.session.user
                    row.replied_by_name = frappe.utils.get_fullname(frappe.session.user)
                    row.replay_date = now()
        
        # Run only if user is trying to Close the visit
        if self.workflow_state == "Closed":
            checklist_points = {row.point for row in self.checklist_points}
            responded_points = {row.point for row in self.response_details}
            
            # 1. Check all checklist points are replied
            missing_points = checklist_points - responded_points
            if missing_points:
                frappe.throw(_("Cannot close the visit. The following checklist points are not responded to: {0}")
                             .format(", ".join(missing_points)))

            # 2. Check no empty responses
            empty_responses = [
                row.point for row in self.response_details
                if not row.response or not row.response.strip()
            ]
            if empty_responses:
                frappe.throw(_("Response is missing for the following points: {0}")
                             .format(", ".join(empty_responses)))