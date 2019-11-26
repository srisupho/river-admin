from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction
from river.models import TransitionApprovalMeta

from river_admin_issue_tracker_example.models import Issue

OPEN = "Open"
IN_PROGRESS = "In Progress"
RESOLVED = "Resolved"
RE_OPENED = "Re-Opened"
CLOSED = "Closed"


class Command(BaseCommand):
    help = 'Bootstrapping database with necessary items'

    @transaction.atomic()
    def handle(self, *args, **options):
        from river.models import State, Workflow, TransitionMeta
        from django.contrib.contenttypes.models import ContentType

        developer, _ = Group.objects.update_or_create(name="Developer")
        team_leader, _ = Group.objects.update_or_create(name="Team Leader")
        tester, _ = Group.objects.update_or_create(name="Tester")

        issue_content_type = ContentType.objects.get_for_model(Issue)

        open_state, _ = State.objects.get_or_create(label=OPEN)
        in_progress_state, _ = State.objects.get_or_create(label=IN_PROGRESS)
        resolved_state, _ = State.objects.get_or_create(label=RESOLVED)
        re_opened_state, _ = State.objects.get_or_create(label=RE_OPENED)
        closed_state, _ = State.objects.get_or_create(label=CLOSED)

        workflow, _ = Workflow.objects.get_or_create(content_type=issue_content_type, field_name="issue_status", defaults={"initial_state": open_state})

        open_state_to_in_progress, _ = TransitionMeta.objects.get_or_create(workflow=workflow, source_state=open_state, destination_state=in_progress_state)
        in_progress_to_resolved, _ = TransitionMeta.objects.get_or_create(workflow=workflow, source_state=in_progress_state, destination_state=resolved_state)
        resolved_to_closed, _ = TransitionMeta.objects.get_or_create(workflow=workflow, source_state=resolved_state, destination_state=closed_state)
        resolved_to_re_opened, _ = TransitionMeta.objects.get_or_create(workflow=workflow, source_state=resolved_state, destination_state=re_opened_state)
        re_opened_to_in_progress, _ = TransitionMeta.objects.get_or_create(workflow=workflow, source_state=re_opened_state, destination_state=in_progress_state)

        open_state_to_in_progress_rule, _ = TransitionApprovalMeta.objects.get_or_create(workflow=workflow, transition_meta=open_state_to_in_progress, priority=0)
        open_state_to_in_progress_rule.groups.set([developer])

        in_progress_to_resolved_rule, _ = TransitionApprovalMeta.objects.get_or_create(workflow=workflow, transition_meta=in_progress_to_resolved, priority=0)
        in_progress_to_resolved_rule.groups.set([developer])

        resolved_to_closed_rule_1, _ = TransitionApprovalMeta.objects.get_or_create(workflow=workflow, transition_meta=resolved_to_closed, priority=0)
        resolved_to_closed_rule_1.groups.set([team_leader])

        resolved_to_closed_rule_2, _ = TransitionApprovalMeta.objects.get_or_create(workflow=workflow, transition_meta=resolved_to_closed, priority=1)
        resolved_to_closed_rule_2.groups.set([tester])

        resolved_to_re_opened_rule, _ = TransitionApprovalMeta.objects.get_or_create(workflow=workflow, transition_meta=resolved_to_re_opened, priority=0)
        resolved_to_re_opened_rule.groups.set([team_leader, tester])

        re_opened_to_in_progress_rule, _ = TransitionApprovalMeta.objects.get_or_create(workflow=workflow, transition_meta=re_opened_to_in_progress, priority=0)
        re_opened_to_in_progress_rule.groups.set([developer])

        self.stdout.write(self.style.SUCCESS('Successfully bootstrapped the db '))
