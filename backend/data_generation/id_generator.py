
from collections import defaultdict


class IDGenerator:

    def __init__(self):
        self.counters = defaultdict(int)

    def next_number(self, key):
        self.counters[key] += 1
        return self.counters[key]

    def customer_id(self):
        number = self.next_number("customer")
        return f"CUS-{number:06d}"

    def product_id(self):
        number = self.next_number("product")
        return f"PRD-{number:04d}"

    def order_id(self):
        number = self.next_number("order")
        return f"ORD-2026-{number:06d}"

    def order_item_id(self, order_number, item_number):
        return f"OIT-2026-{order_number:06d}-{item_number:02d}"

    def complaint_id(self):
        number = self.next_number("complaint")
        return f"CMP-2026-{number:06d}"

    def message_id(self, complaint_id):
        number = self.next_number(f"message:{complaint_id}")
        return f"MSG-{complaint_id}-{number:03d}"

    def assignment_id(self, complaint_id):
        number = self.next_number(f"assignment:{complaint_id}")
        return f"ASG-{complaint_id}-{number:02d}"

    def history_id(self, complaint_id):
        number = self.next_number(f"history:{complaint_id}")
        return f"HST-{complaint_id}-{number:03d}"

    def sla_id(self, complaint_id):
        return f"SLA-{complaint_id}"

    def sla_event_id(self, complaint_id):
        number = self.next_number(f"sla_event:{complaint_id}")
        return f"SLE-{complaint_id}-{number:03d}"

    def resolution_id(self, complaint_id, cycle_no=1):
        if cycle_no == 1:
            return f"RES-{complaint_id}"

        return f"RES-{complaint_id}-{cycle_no:02d}"

    def survey_id(self, complaint_id):
        return f"SRV-{complaint_id}"

    def decision_id(self, complaint_id, decision_type):
        return f"DEC-{complaint_id}-{decision_type}"

    def exception_id(self):
        number = self.next_number("exception")
        return f"EXC-{number:06d}"

    def ground_truth_id(self):
        number = self.next_number("ground_truth")
        return f"GT-{number:06d}"


# One shared ID generator
id_generator = IDGenerator()
