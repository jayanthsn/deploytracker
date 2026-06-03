Ask the user the following question before doing anything:

"What changed that needs new or updated tests? Describe the endpoint, service function, exception, or schema that was added or modified (e.g. 'added PUT /deployments/{id}', 'added DuplicateDeployment exception', 'added region validation in service layer')."

Once the user answers:

1. Read the relevant changed source file (service, endpoint, schema, or exception) based on their description.
2. Read `tests/test_deployments.py` to understand the existing fixture usage, assertion style, and class grouping.
3. In `tests/test_deployments.py`, add or update test cases that cover:
   - The happy path for the new/changed behaviour
   - Any new custom exception (assert `status`, `code`, and `message` in the response body)
   - Pydantic validation failures introduced by new fields or validators
   - Edge cases specific to the change (empty values, boundary inputs, unknown IDs, etc.)
4. Follow the existing patterns exactly: use the `client: AsyncClient` fixture, group tests in a class named after the feature, keep assertions focused.
5. Report which test cases were added or updated and why each one was necessary.
