import json

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from hamcrest import equal_to, assert_that, has_entry, not_none, is_, none
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_200_OK
from river.models import State, Workflow, TransitionMeta, Function, OnTransitHook


class TransitionHookViewTest(TestCase):

    def test__shouldCreateTransitionHook(self):
        initial_state = State.objects.create(label="state-1")
        state_2 = State.objects.create(label="state-2")

        content_type = ContentType.objects.first()
        workflow = Workflow.objects.create(initial_state=initial_state, content_type=content_type, field_name="test-field")
        transition_meta = TransitionMeta.objects.create(workflow=workflow, source_state=initial_state, destination_state=state_2)

        function = Function.objects.create(name="test-function-1", body="function-body")
        response = self.client.post('/transition-hook/create/', json.dumps({
            "workflow": workflow.id,
            "content_type": content_type.id,
            "transition_meta": transition_meta.id,
            "callback_function": function.id,
            "transition": None,
            "object_id": None

        }), content_type='application/json')

        assert_that(response.status_code, equal_to(HTTP_200_OK))

        created_transition_hook = OnTransitHook.objects.first()
        assert_that(created_transition_hook, not_none())
        assert_that(response.status_code, equal_to(HTTP_200_OK))
        assert_that(response.data, has_entry("id", equal_to(created_transition_hook.pk)))

    def test__shouldReturnNotFoundWhenAnInexistentTransitionHookIsRequestedToDelete(self):
        response = self.client.delete('/transition-hook/delete/1/')
        assert_that(response.status_code, equal_to(HTTP_404_NOT_FOUND))

    def test__shouldDeleteTransitionHook(self):
        initial_state = State.objects.create(label="state-1")
        state_2 = State.objects.create(label="state-2")

        content_type = ContentType.objects.first()
        workflow = Workflow.objects.create(initial_state=initial_state, content_type=content_type, field_name="test-field")
        transition_meta = TransitionMeta.objects.create(workflow=workflow, source_state=initial_state, destination_state=state_2)

        function = Function.objects.create(name="test-function-1", body="function-body")

        transition_hook = OnTransitHook.objects.create(workflow=workflow, callback_function=function, transition_meta=transition_meta)

        response = self.client.delete('/transition-hook/delete/%d/' % transition_hook.id)
        assert_that(response.status_code, equal_to(HTTP_200_OK))
        assert_that(OnTransitHook.objects.filter(pk=transition_hook.id).first(), is_(none()))
